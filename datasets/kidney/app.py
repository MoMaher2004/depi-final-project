import streamlit as st
import joblib
import numpy as np
import pandas as pd

# 1. تحميل الملفات المحفوظة
model = joblib.load('kidney_model_final.pkl')
scaler = joblib.load('scaler_final.pkl')
feature_names = joblib.load('features_names.pkl')

# 2. تظبيط شكل الصفحة (The Glow)
st.set_page_config(page_title="Kidney AI Doctor", page_icon="🩺", layout="centered")

st.markdown("""
    <style>
    .main {background-color: #0e1117;}
    h1 {color: #00ffcc; text-align: center;}
    .stButton>button {width: 100%; background-color: #ff4b4b; color: white;}
    </style>
    """, unsafe_allow_html=True)

st.title(" Kidney Disease Prediction AI")
st.write("### Please enter patient data below:")
col1, col2 = st.columns(2)
user_inputs = []


for i, col_name in enumerate(feature_names):
    with (col1 if i % 2 == 0 else col2):
        val = st.number_input(f"{col_name}", value=0.0, step=0.1)
        user_inputs.append(val)

if st.button("Analyze Result"):
    data_array = np.array([user_inputs])
    data_scaled = scaler.transform(data_array)


    prediction = model.predict(data_scaled)
    prob = model.predict_proba(data_scaled)[0][1]
    st.divider()

    if prediction[0] == 1:
        st.error(f" Positive for CKD (Chronic Kidney Disease)")
        st.write(f"Confidence: **{prob*100:.1f}%**")
        st.warning("Please consult a Nephrologist immediately.")
    else:
        st.success(f" Negative (Healthy)")
        st.write(f"Confidence: **{(1-prob)*100:.1f}%**")
        st.balloons()
