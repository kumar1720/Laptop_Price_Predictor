import streamlit as st
import pickle
import numpy as np
pipe = pickle.load(open('pipe.pkl', 'rb'))
df = pickle.load(open('df.pkl', 'rb'))
st.title("Laptop Price Predictor")

#brand
Company = st.selectbox('Brand', df['Company'].unique())
# type
Type = st.selectbox('Type', df['TypeName'].unique())
# Ram
Ram = st.selectbox('Ram',[2,4,6,8,12,16,24,32,64])
# weight
Weight = st.number_input('Weight in KG')
# Touchscreen
Touchscreen = st.selectbox('Touchscreen', ['No','Yes'])
# ips
Ips = st.selectbox('Ips	', ['No','Yes'])
# Screen
Screen_size = st.number_input('Screen size')
# resolution
resolution = st.selectbox('Screen Resolution', ['1920x1080',
         '1366x768', '1600x900', '3840x2160', '3200x1800',
         '2880x1800', '2560x1600', '2560x1440', '2304x1440'])
# Cpu
Cpu = st.selectbox('CPU',df['Cpu brand'].unique())
HDD = st.selectbox('HDD(in GB)',[0,128,256,512,1024,2048])
SSD = st.selectbox('SSD(in GB)',[0,8,128,256,512,1024])
Gpu = st.selectbox('GPU',df['Gpu brand'].unique())
OS = st.selectbox('OS',df['OS'].unique())

if st.button('Predict Price'):
    ppi = None
    if Touchscreen == 'Yes':
        Touchscreen = 1
    else:
        Touchscreen = 0
    if Ips == 'Yes' :
        Ips = 1
    else:
        Ips = 0
    X_res = int(resolution.split('x')[0])
    Y_res = int(resolution.split('x')[1])
    ppi = ((X_res**2) + (Y_res**2))** 0.5/Screen_size
    query = np.array([Company,Type, Ram,Weight,Touchscreen,Ips,ppi,Cpu,HDD,SSD,Gpu,OS])
    query = query.reshape(1,12)
    st.title(np.exp(pipe.predict(query)))

#  cd Laptop_Price_Predictor
#   streamlit run app.py 


