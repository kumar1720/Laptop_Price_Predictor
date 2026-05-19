import pickle
import pandas as pd
import numpy as np
import hashlib
from typing import Dict, Any
from app.core.config import settings
from app.core.exceptions import ModelPredictionException
from app.cache.redis_cache import cache
from app.utils.logger import logger

class ModelService:
    def __init__(self):
        self.pipe = None
        self.df = None
        self.load_models()

    def load_models(self):
        try:
            logger.info(f"Loading pipeline from {settings.MODEL_PATH}...")
            with open(settings.MODEL_PATH, 'rb') as f:
                self.pipe = pickle.load(f)
            logger.info("Pipeline loaded successfully.")

            logger.info(f"Loading reference DataFrame from {settings.DF_PATH}...")
            with open(settings.DF_PATH, 'rb') as f:
                self.df = pickle.load(f)
            logger.info("Reference DataFrame loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading model assets: {e}")
            self.pipe = None
            self.df = None

    def generate_cache_key(self, data: Dict[str, Any]) -> str:
        # Create a stable string representation of features to hash
        feature_str = "|".join(f"{k}:{v}" for k, v in sorted(data.items()))
        return f"pred_{hashlib.md5(feature_str.encode()).hexdigest()}"

    def predict_price(self, specs: Dict[str, Any]) -> int:
        if self.pipe is None:
            # Re-try loading in case it was a temp loading issue
            self.load_models()
            if self.pipe is None:
                raise ModelPredictionException("ML model is not initialized/loaded.")
        
        # Check cache
        cache_key = self.generate_cache_key(specs)
        cached_val = cache.get(cache_key)
        if cached_val is not None:
            logger.info(f"Cache hit for key {cache_key}!")
            return cached_val

        try:
            # Convert binary parameters
            touchscreen_val = 1 if specs['Touchscreen'] == 'Yes' else 0
            ips_val = 1 if specs['Ips'] == 'Yes' else 0
            
            # Calculate PPI (Pixels Per Inch)
            resolution = specs['Resolution']
            x_res = int(resolution.split('x')[0])
            y_res = int(resolution.split('x')[1])
            ppi = ((x_res**2) + (y_res**2))**0.5 / specs['Screen_size']
            
            # Construct dictionary matching df features exactly
            query_dict = {
                'Company': [specs['Company']],
                'TypeName': [specs['TypeName']],
                'Ram': [specs['Ram']],
                'Weight': [specs['Weight']],
                'Touchscreen': [touchscreen_val],
                'Ips': [ips_val],
                'ppi': [ppi],
                'Cpu brand': [specs['Cpu_brand']],
                'HDD': [float(specs['HDD'])],
                'SSD': [float(specs['SSD'])],
                'Gpu brand': [specs['Gpu_brand']],
                'OS': [specs['OS']],
                'Cpu_Speed': [specs['Cpu_Speed']]
            }
            
            query_df = pd.DataFrame(query_dict)
            cols_order = ['Company', 'TypeName', 'Ram', 'Weight', 'Touchscreen', 'Ips', 'ppi', 'Cpu brand', 'HDD', 'SSD', 'Gpu brand', 'OS', 'Cpu_Speed']
            query_df = query_df[cols_order]
            
            # Predict
            pred_log = self.pipe.predict(query_df)[0]
            price = int(np.exp(pred_log))
            
            # Store in cache (cache for 24 hours)
            cache.set(cache_key, price, expire_seconds=86400)
            
            return price
        except Exception as e:
            logger.error(f"Error during model prediction: {e}")
            raise ModelPredictionException(f"Prediction failed: {str(e)}")

model_service = ModelService()
