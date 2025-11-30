from fastapi import FastAPI
import pickle
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

app = FastAPI()

brainTumorModel = load_model('./interface/api/brainTumor.h5')
pcosModel = joblib.load('./datasets/pcos/pcos.pkl')
diabetesModel = joblib.load('./datasets/diabetes/diabetes.pkl')
heartFailureScalerModel = joblib.load('./datasets/heart-failure/scaler_heart.pkl')
heartFailureModel = joblib.load('./datasets/heart-failure/heart_clinic_model_optimized.pkl')

@app.post("/heartFailure")
def predict_heart_disease(data: dict):
    sex_map = {'Male': 1, 'Female': 0} 
    cp_map = {'ASY': 0, 'ATA': 1, 'NAP': 2, 'TA': 3} 
    restecg_map = {'Normal': 1, 'ST-T Wave Abnormality': 2, 'LVH': 0}
    exang_map = {'Yes': 1, 'No': 0}
    slope_map = {'Up': 2, 'Flat': 1, 'Down': 0}

    input_data = pd.DataFrame([[
        data['Age'], sex_map.get(data['Sex'], 1), cp_map.get(data['ChestPainType'], 0), data['RestingBP'], data['Cholesterol'], data['FastingBS'], 
        restecg_map.get(data['RestingECG'], 1), data['MaxHR'], exang_map.get(data['ExerciseAngina'], 0), 
        data['Oldpeak'], slope_map.get(data['ST_Slope'], 1)
    ]], columns=['Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 'FastingBS', 
                 'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope'])
    
    input_data['MaxHR_Age'] = input_data['MaxHR'] / input_data['Age']
    
    slope_val_num = input_data['ST_Slope'].values[0]
    slope_factor = 1 if slope_val_num == 1 else (2 if slope_val_num == 2 else 0)
    input_data['Oldpeak_Slope'] = input_data['Oldpeak'] * slope_factor

    cols_order = ['Age', 'Sex', 'ChestPainType', 'RestingBP', 'Cholesterol', 'FastingBS', 
                  'RestingECG', 'MaxHR', 'ExerciseAngina', 'Oldpeak', 'ST_Slope', 
                  'MaxHR_Age', 'Oldpeak_Slope']
    
    input_data = input_data[cols_order]

    input_data_scaled = heartFailureScalerModel.transform(input_data)
    
    prediction = heartFailureModel.predict(input_data_scaled)[0]
    probability = heartFailureModel.predict_proba(input_data_scaled)[0][1] 
    return f"Heart failure prediction is {prediction} with probability of {probability}"


# @app.post("/heartFailure")
# def diabetes(data: dict):
#     df = pd.DataFrame([{
#         "Age": data['Age'],
#         "Sex": data['Sex'],
#         "ChestPainType": data['ChestPainType'],
#         "RestingBP": data['RestingBP'],
#         "Cholesterol": data['Cholesterol'],
#         "FastingBS": data['FastingBS'].lower() == 'yes',
#         "RestingECG": data['RestingECG'],
#         "MaxHR": data['MaxHR'],
#         "ExerciseAngina": data['ExerciseAngina'].lower() == 'y',
#         "Oldpeak": data['Oldpeak'],
#         "ST_Slope": data['ST_Slope']
#     }])
#     scaled = heartFailureScalerModel.transform(df)
#     res = diabetesModel.predict(scaled)
#     return f"heart failure prediction is {res[0]}"

@app.post("/diabetes")
def diabetes(data: dict):
    df = pd.DataFrame([{
        "gender": data['gender'],
        "age": data['age'],
        "hypertension": data['hypertension'],
        "heart_disease": data['heart_disease'],
        "smoking_history": data['smoking_history'],
        "bmi": data['bmi'],
        "HbA1c_level": data['HbA1c_level'],
        "blood_glucose_level": data['blood_glucose_level']
    }])
    res = diabetesModel.predict(df)
    return f"diabetes prediction is {res[0]}"

@app.post("/pcos")
def pcos(data: dict):
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
    return f"PCOS prediction is {res[0]}"

@app.post("/brainTumor")
def brainTumor(data: dict):
    target_size=(224, 224)
    # image_path = data['image_path']
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

    # img = image.load_img(image_path, target_size=target_size)
    # img_array = image.img_to_array(img)
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