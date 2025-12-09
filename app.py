from flask import Flask, request, jsonify, redirect
import pickle
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input
import pandas as pd
import base64
import io
from PIL import Image
import joblib
import dash_bootstrap_components as dbc

def convert_to_valid_binary(x, true, false):
    if type(x) == str: x = x.lower().strip()
    if x in ['yes', 'y', True, 'true', 1]: return true
    if x in ['no', 'n', False, 'false', 0]: return false
    return None

def convert_to_valid_gender(x, male, female):
    if type(x) == str: x = x.lower().strip()
    if x in ['male', 'm']: return male
    if x in ['female', 'f']: return female
    return None

app = Flask(__name__)

brainTumorModel = load_model(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "brainTumor.h5"))
pcosModel = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "pcos.pkl"))
diabetesModel = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "diabetes.pkl"))
heartFailureScalerModel = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "scaler_heart.pkl"))
heartFailureModel = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "heart_clinic_model_optimized.pkl"))
kidneyModel = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", 'kidney_model.pkl'))
kidneyScaler = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", 'kidney_scaler.pkl'))
skinCancerModel = load_model(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", 'skinCancer.h5'))

import dash
from dash import Dash, html, dcc

pcos_dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname='/dashboards/pcos/',
    external_stylesheets=[dbc.themes.VAPOR],
    suppress_callback_exceptions=True
)

diabetes_dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname='/dashboards/diabetes/',
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

heart_dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname='/dashboards/heart/',
    external_stylesheets=[dbc.themes.VAPOR],
    suppress_callback_exceptions=True
)

kidney_dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname='/dashboards/kidney/',
    external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
    suppress_callback_exceptions=True
)

from dashboards import pcos, diabetes, heart, kidney

pcos_dash_app.layout = pcos.layout
diabetes_dash_app.layout = diabetes.layout
heart_dash_app.layout = heart.layout
kidney_dash_app.layout = kidney.layout

@app.route("/heartFailure", methods=["POST"])
def predict_heart_disease():
    data = request.json

    cols_order = ['Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope', 'MaxHR_Age', 'Oldpeak_Slope']

    for d in ['Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 'FastingBS', 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope']:
        try:
            fsdghaw = data[d]
        except KeyError:
            return f"{d} is missing, please provide it" 

    sex_map = {'Male': 1, 'Female': 0} 
    cp_map = {'ASY': 0, 'ATA': 1, 'NAP': 2, 'TA': 3} 
    restecg_map = {'Normal': 1, 'ST-T Wave Abnormality': 2, 'LVH': 0}
    exang_map = {'Yes': 1, 'No': 0}
    slope_map = {'Up': 2, 'Flat': 1, 'Down': 0}

    input_data = pd.DataFrame([[
        data['Age'], sex_map.get(convert_to_valid_gender(data['Sex'], 'Male', 'Female'), 1), cp_map.get(data['ChestPainType'], 0), data['RestingBP'], data['Cholesterol'], data['FastingBS'], 
        restecg_map.get(data['RestingECG'], 1), data['MaxHR'], exang_map.get(convert_to_valid_binary(data['ExerciseAngina'], 1, 0), 0), 
        data['Oldpeak'], slope_map.get(data['ST_Slope'], 1)
    ]], columns=['Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 'FastingBS', 
                 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope'])
    
    input_data['MaxHR_Age'] = input_data['MaxHR'] / input_data['Age']
    
    slope_val_num = input_data['ST_Slope'].values[0]
    slope_factor = 1 if slope_val_num == 1 else (2 if slope_val_num == 2 else 0)
    input_data['Oldpeak_Slope'] = input_data['Oldpeak'] * slope_factor
    
    input_data = input_data[cols_order]

    input_data_scaled = heartFailureScalerModel.transform(input_data)
    
    prediction = heartFailureModel.predict(input_data_scaled)[0]
    probability = heartFailureModel.predict_proba(input_data_scaled)[0][1] 
    return f"Heart failure prediction is {prediction} with probability of {probability * 100}%"

@app.route("/kidney", methods=["POST"])
def kidney():
    data = request.json
    for d in ['Bp', 'Sg', 'Al', 'Su', 'Rbc', 'Bu', 'Sc', 'Sod', 'Pot', 'Hemo', 'Wbcc', 'Rbcc', 'Htn']:
        try:
            fsdghaw = data[d]
        except KeyError:
            return f"{d} is missing, please provide it" 
    df = pd.DataFrame([{
        "Bp": data['Bp'],
        "Sg": data['Sg'],
        "Al": data['Al'],
        "Su": data['Su'],
        "Rbc": data['Rbc'],
        "Bu": data['Bu'],
        "Sc": data['Sc'],
        "Sod": data['Sod'],
        "Pot": data['Pot'],
        "Hemo": data['Hemo'],
        "Wbcc": data['Wbcc'],
        "Rbcc": data['Rbcc'],
        "Htn": convert_to_valid_binary(data['Htn'], 1, 0)
    }])
    data_scaled = kidneyScaler.transform(df)
    res = kidneyModel.predict(data_scaled)
    return f"chronic kidney disease prediction is {res[0]}"

@app.route("/diabetes", methods=["POST"])
def diabetes():
    data = request.json
    for d in ['gender', 'age', 'hypertension', 'heart_disease', 'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level']:
        try:
            fsdghaw = data[d]
        except KeyError:
            return f"{d} is missing, please provide it" 
    df = pd.DataFrame([{
        "gender": convert_to_valid_gender(data['gender'], 'Male', 'Female'),
        "age": data['age'],
        "hypertension": convert_to_valid_binary(data['hypertension'], 1, 0),
        "heart_disease": convert_to_valid_binary(data['heart_disease'], 1, 0),
        "smoking_history": data['smoking_history'],
        "bmi": data['bmi'],
        "HbA1c_level": data['HbA1c_level'],
        "blood_glucose_level": data['blood_glucose_level']
    }])
    res = diabetesModel.predict(df)
    return f"diabetes prediction is {'positive' if res[0] else 'negative'}"

@app.route("/pcos", methods=["POST"])
def pcos():
    data = request.json
    for d in ['bmi', 'age', 'pulse_rate', 'blood_group']:
        try:
            fsdghaw = data[d]
        except KeyError:
            return f"{d} is missing, please provide it" 

    df = pd.DataFrame([{
        "Age (yrs)": 33,
        "Weight (Kg)": 58,
        "Height(Cm)": 159,
        "BMI": 23.14,
        "Pulse rate(bpm)": 72,
        "RR (breaths/min)": 20,
        "Hb(g/dl)": 11,
        "Cycle(R/I)": 2,
        "Cycle length(days)": 5,
        "Marraige Status (Yrs)": 13,
        "No. of aborptions": 2,
        "I   beta-HCG(mIU/mL)": 100,
        "II    beta-HCG(mIU/mL)": 100,
        "FSH(mIU/mL)": 4.9,
        "LH(mIU/mL)": 3.1,
        "FSH/LH": 1.6,
        "Hip(inch)": 44,
        "Waist(inch)": 38,
        "Waist:Hip Ratio": .9,
        "TSH (mIU/L)": 12.2,
        "AMH(ng/mL)": 1.5,
        "PRL(ng/mL)": 4,
        "Vit D3 (ng/mL)": 38,
        "PRG(ng/mL)": .26,
        "RBS(mg/dl)": 91,
        "BP _Systolic (mmHg)": 120,
        "BP _Diastolic (mmHg)": 80,
        "Follicle No. (L)": 7,
        "Follicle No. (R)": 6,
        "Avg. F size (L) (mm)": 15,
        "Avg. F size (R) (mm)": 18,
        "Endometrium (mm)": 7,
        "Blood Group_A-": False,
        "Blood Group_AB+": False,
        "Blood Group_AB-": False,
        "Blood Group_B+": True,
        "Blood Group_B-": False,
        "Blood Group_O+": False,
        "Blood Group_O-": False,
        "Pregnant(Y/N)_yes": True,
        "Weight gain(Y/N)_yes": True,
        "hair growth(Y/N)_yes": False,
        "Skin darkening (Y/N)_yes": False,
        "Hair loss(Y/N)_yes": False,
        "Pimples(Y/N)_yes": False,
        "Fast food (Y/N)_yes": False,
        "Reg.Exercise(Y/N)_yes": False
    }])
    df.loc[0, 'Age (yrs)'] = data['age']
    df.loc[0, 'BMI'] = data['bmi']
    df.loc[0, 'Pulse rate(bpm)'] = data['pulse_rate']
    df.loc[0, 'Blood Group_A-'] = data['blood_group'] == 'A-'
    df.loc[0, 'Blood Group_AB+'] = data['blood_group'] == 'AB+'
    df.loc[0, 'Blood Group_AB-'] = data['blood_group'] == 'AB-'
    df.loc[0, 'Blood Group_B+'] = data['blood_group'] == 'B+'
    df.loc[0, 'Blood Group_B-'] = data['blood_group'] == 'B-'
    df.loc[0, 'Blood Group_O+'] = data['blood_group'] == 'O+'
    df.loc[0, 'Blood Group_O-'] = data['blood_group'] == 'O-'
    res = pcosModel.predict(df)
    return f"PCOS prediction is {'positive' if res[0] else 'negative'}"

@app.route("/brainTumor", methods=["POST"])
def brainTumor():
    data = request.json

    target_size=(224, 224)
    base64_image_string = data.get('image')

    if not base64_image_string:
        return "Error: 'image' not found in input data."

    try:
        if ';base64,' in base64_image_string:
            _, base64_image_string = base64_image_string.split(';base64,')
            
        image_data = base64.b64decode(base64_image_string)
    except Exception as e:
        print(f"Error decoding Base64: {e}")
        return "Base64 decoding failed."

    try:
        image_stream = io.BytesIO(image_data)
        img = Image.open(image_stream).convert('RGB')
        img = img.resize(target_size)
    except Exception as e:
        print(f"Error processing image data: {e}")
        return "Image processing failed."

    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0) 
    
    processed_img = preprocess_input(img_array)

    class_indices = {'glioma': 0, 'meningioma': 1, 'notumor': 2, 'pituitary': 3}
    classes = sorted(class_indices, key=class_indices.get) 

    predictions = brainTumorModel.predict(processed_img)
    predicted_index = np.argmax(predictions[0])
    
    predicted_class = classes[predicted_index]
    
    confidence = predictions[0][predicted_index] * 100

    print(f"Prediction probabilities: {predictions[0]}")
    print(f"Predicted Class: {predicted_class}")
    print(f"Confidence: {confidence:.2f}%")

    return f"""MRI brain tumor prediction report
    
    Prediction probabilities:
    glioma: {predictions[0][class_indices['glioma']] * 100}%
    meningioma: {predictions[0][class_indices['meningioma']] * 100}%
    notumor: {predictions[0][class_indices['notumor']] * 100}%
    pituitary: {predictions[0][class_indices['pituitary']] * 100}%

    Predicted Class: {predicted_class}
    Confidence: {confidence:.2f}%"""

@app.route("/skinCancer", methods=["POST"])
def skinCancer():
    data = request.json
    
    target_size = (150, 150)
    base64_image_string = data.get('image')

    if not base64_image_string:
        return jsonify({"error": "'image' not found in input data."}), 400

    try:
        if ';base64,' in base64_image_string:
            _, base64_image_string = base64_image_string.split(';base64,')
            
        image_data = base64.b64decode(base64_image_string)
    except Exception as e:
        print(f"Error decoding Base64: {e}")
        return jsonify({"error": "Base64 decoding failed."}), 400

    try:
        image_stream = io.BytesIO(image_data)
        img = Image.open(image_stream).convert('RGB')
        
        img = image.resize(target_size)
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        processed_img = img_array / 255.0
    except Exception as e:
        print(f"Error processing image data: {e}")
        return jsonify({"error": "Image processing failed."}), 400

    try:
        prediction = skin_cancer_model.predict(processed_img, verbose=0)
        
        malignant_probability = float(prediction[0][0])
        benign_probability = 1.0 - malignant_probability
        
        threshold = 0.42
        is_malignant = malignant_probability > threshold
        
        if is_malignant:
            confidence = malignant_probability * 100
            predicted_class = "Malignant"
        else:
            confidence = benign_probability * 100
            predicted_class = "Benign"
            
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"error": "Prediction failed."}), 500

    response = {
        "predicted_class": predicted_class,
        "confidence": f"{confidence:.2f}%",
        "probabilities": {
            "benign": f"{benign_probability * 100:.2f}%",
            "malignant": f"{malignant_probability * 100:.2f}%"
        },
        "threshold_used": threshold,
        "is_malignant": bool(is_malignant)
    }
    
    report = f"""Skin Cancer Prediction Report
    
    Prediction probabilities:
    Benign: {benign_probability * 100:.2f}%
    Malignant: {malignant_probability * 100:.2f}%
    
    Predicted Class: {predicted_class}
    Confidence: {confidence:.2f}%
    Threshold: {threshold}
    
    {'⚠️ WARNING: Potential malignant lesion detected. Please consult a dermatologist.' if is_malignant else '✅ Likely benign. Still, regular skin checks are recommended.'}"""
    
    return report

@app.route('/dashboards/pcos/<path:path>')
def pcos_dash_route(path):
    return pcos_dash_app.index()

@app.route('/dashboards/diabetes/<path:path>')
def diabetes_dash_route(path):
    return diabetes_dash_app.index()

@app.route('/dashboards/heart/<path:path>')
def heart_dash_route(path):
    return heart_dash_app.index()

@app.route('/dashboards/kidney/<path:path>')
def kidney_dash_route(path):
    return kidney_dash_app.index()

@app.route('/dashboards/pcos')
def redirect_pcos():
    return redirect('/dashboards/pcos/')

@app.route('/dashboards/diabetes')
def redirect_diabetes():
    return redirect('/dashboards/diabetes/')

@app.route('/dashboards/heart')
def redirect_heart():
    return redirect('/dashboards/heart/')

@app.route('/dashboards/kidney')
def redirect_kidney():
    return redirect('/dashboards/kidney/')

@app.route('/')
def index():
    try:
        with open('./index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return '''<h1>ERROR</h1>'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)