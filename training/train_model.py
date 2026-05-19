import os
import pickle
import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, HistGradientBoostingRegressor, VotingRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

from training.train_utils import parse_memory, extract_cpu_speed

def train():
    data_path = 'data/laptop_data.csv'
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Source data file not found at {data_path}")

    print("Loading data from:", data_path)
    df = pd.read_csv(data_path)
    
    # Data Cleaning and Feature Engineering
    df.drop(columns=['Unnamed: 0'], inplace=True)
    
    # 1. Clean RAM and Weight
    df['Ram'] = df['Ram'].str.replace('GB', '').astype('int32')
    df['Weight'] = df['Weight'].str.replace('kg', '').astype('float32')
    
    # 2. Extract Touchscreen and IPS from ScreenResolution
    df['Touchscreen'] = df['ScreenResolution'].apply(lambda x: 1 if 'Touchscreen' in x else 0)
    df['Ips'] = df['ScreenResolution'].apply(lambda x: 1 if 'IPS' in x else 0)
    
    # 3. Calculate PPI
    def get_resolution_and_size(row):
        res_str = row['ScreenResolution']
        size = row['Inches']
        # Find resolution dimensions (e.g. 1920x1080)
        match = re.search(r'(\d+)\s*[xX]\s*(\d+)', res_str)
        if match:
            x_res = float(match.group(1))
            y_res = float(match.group(2))
            ppi = ((x_res**2) + (y_res**2))**0.5 / size
            return ppi
        return 120.0 # default fallback ppi
        
    df['ppi'] = df.apply(get_resolution_and_size, axis=1)
    
    # 4. CPU Brand and Speed Extraction
    def get_cpu_brand(cpu_str):
        cpu_str = str(cpu_str)
        # Check Core types
        if 'Intel Core i7' in cpu_str:
            return 'Intel Core i7'
        elif 'Intel Core i5' in cpu_str:
            return 'Intel Core i5'
        elif 'Intel Core i3' in cpu_str:
            return 'Intel Core i3'
        elif 'Intel' in cpu_str:
            return 'Other Intel Processor'
        else:
            return 'AMD Processor'
            
    df['Cpu brand'] = df['Cpu'].apply(get_cpu_brand)
    df['Cpu_Speed'] = df['Cpu'].apply(extract_cpu_speed)
    
    # 5. Storage (HDD & SSD) parsing
    memory_parsed = df['Memory'].apply(parse_memory)
    df['HDD'] = [m[0] for m in memory_parsed]
    df['SSD'] = [m[1] for m in memory_parsed]
    
    # 6. GPU brand cleaning
    df['Gpu brand'] = df['Gpu'].apply(lambda x: x.split()[0])
    df = df[df['Gpu brand'] != 'ARM'] # Remove rare ARM GPU
    
    # 7. OS categorization
    def categorize_os(os_str):
        os_str = str(os_str)
        if os_str in ['Windows 10', 'Windows 7', 'Windows 10 S']:
            return 'Windows'
        elif os_str in ['macOS', 'Mac OS X']:
            return 'Mac'
        else:
            return 'Others/No OS/Linux'
            
    df['OS'] = df['OpSys'].apply(categorize_os)
    
    # Drop intermediate columns
    df.drop(columns=['ScreenResolution', 'Inches', 'Cpu', 'Memory', 'Gpu', 'OpSys'], inplace=True)
    
    # Reorder columns to match existing structure and preserve index references
    cols = ['Company', 'TypeName', 'Ram', 'Weight', 'Price', 'Touchscreen', 'Ips', 'ppi', 'Cpu brand', 'HDD', 'SSD', 'Gpu brand', 'OS', 'Cpu_Speed']
    df = df[cols]
    
    # Set features and target
    X = df.drop(columns=['Price'])
    Y = np.log(df['Price'])
    
    # Split
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.15, random_state=2)
    
    # Train pipeline setup
    step1 = ColumnTransformer(transformers=[ 
       ('col_tnf', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), [0,1,7,10,11]) 
    ], remainder='passthrough')
    
    rf = RandomForestRegressor(n_estimators=100, random_state=3, max_samples=0.85, max_features=0.45, max_depth=26)
    et = ExtraTreesRegressor(n_estimators=100, random_state=3, max_samples=0.85, max_features=0.45, max_depth=26, bootstrap=True)
    hgb = HistGradientBoostingRegressor(random_state=3, max_iter=150, learning_rate=0.08, max_depth=8)
    xgb = XGBRegressor(n_estimators=120, max_depth=6, learning_rate=0.08, random_state=3, subsample=0.8, colsample_bytree=0.8, reg_alpha=0.1, reg_lambda=1.0)
    lgb = LGBMRegressor(n_estimators=120, max_depth=6, learning_rate=0.08, random_state=3, subsample=0.8, colsample_bytree=0.8, reg_alpha=0.1, reg_lambda=1.0, verbosity=-1)
    
    step2 = VotingRegressor([
        ('rf', rf),
        ('et', et),
        ('hgb', hgb),
        ('xgb', xgb),
        ('lgb', lgb)
    ], weights=[1.0, 0.5, 3.0, 1.0, 1.0])
    
    pipe = Pipeline([
        ('step1', step1),
        ('step2', step2)
    ])
    
    # Training
    print("Fitting model...")
    pipe.fit(X_train, Y_train)
    
    # Evaluation
    Y_pred = pipe.predict(X_test)
    print("Training finished successfully!")
    print(f"R2 score (log space): {r2_score(Y_test, Y_pred):.5f}")
    print(f"MAE (original price): {mean_absolute_error(np.exp(Y_test), np.exp(Y_pred)):.2f}")
    
    # Ensure app/models directory exists and save
    os.makedirs('app/models', exist_ok=True)
    pickle.dump(df, open('app/models/df.pkl', 'wb'))
    pickle.dump(pipe, open('app/models/pipe.pkl', 'wb'))
    print("Successfully exported df.pkl and pipe.pkl to app/models/")

if __name__ == '__main__':
    train()
