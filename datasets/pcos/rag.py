import joblib
import pandas as pd
import json
import datetime
import re
import random

clinic_database = [
    {"id": 1, "name": "Lotus Women's Care", "location": "Downtown Cairo", "specialty": "PCOS & Hormones", "doctors": ["Dr. Sarah Ahmed"], "rating": 4.9},
    {"id": 2, "name": "Al-Amal Fertility", "location": "Nasr City", "specialty": "IVF", "doctors": ["Dr. Hoda Nabil"], "rating": 4.5},
    {"id": 3, "name": "Elite Gyn Clinic", "location": "Maadi", "specialty": "General Gyn", "doctors": ["Dr. Tarek Zaki"], "rating": 4.2}
]

lab_database = [
    {"id": 101, "name": "Alfa Labs", "location": "Maadi", "tests": ["Hormone Profile", "Insulin", "AMH"], "price_range": "$$"},
    {"id": 102, "name": "Al-Mokhtabar", "location": "Downtown", "tests": ["PCOS Panel", "Glucose"], "price_range": "$$"},
    {"id": 103, "name": "Cairo Scan", "location": "Nasr City", "tests": ["Ultrasound", "AMH"], "price_range": "$$$"}
]

medical_advice_db = {
    "high_amh": "High AMH (>4.5) often indicates a high ovarian reserve but is a strong marker for PCOS. Consider reducing sugar intake.",
    "irregular_cycle": "Irregular cycles suggest anovulation. Tracking your cycle using an app is recommended.",
    "weight_gain": "Weight management is crucial for PCOS. Even a 5% reduction in weight can restore regular ovulation.",
    "general": "PCOS is manageable with lifestyle changes. Regular exercise and a balanced diet are your first line of defense."
}

class SessionMemory:
    def __init__(self):
        self.user_profile = {
            'Age': None,
            'AMH(ng/mL)': None,
            'Cycle(R/I)': None,
            'Follicle No. (L)': None,
            'Follicle No. (R)': None,
            'Weight gain(Y/N)': None
        }
        self.history = []

    def update(self, new_data):
        for key, value in new_data.items():
            if value is not None:
                self.user_profile[key] = value

    def get_profile_json(self):
        temp_profile = self.user_profile.copy()
        defaults = {'Age': 25, 'AMH(ng/mL)': 4.0, 'Cycle(R/I)': 2, 'Follicle No. (L)': 5, 'Follicle No. (R)': 5, 'Weight gain(Y/N)': 0}
        for k, v in defaults.items():
            if temp_profile.get(k) is None:
                temp_profile[k] = v
        return json.dumps(temp_profile)

    def is_data_sufficient(self):
        return self.user_profile['AMH(ng/mL)'] is not None or self.user_profile['Cycle(R/I)'] is not None

def extract_medical_data_smart(text):
    text = text.lower()
    data = {}

    amh_match = re.search(r'amh\s*(?:is|:)?\s*(\d+(\.\d+)?)', text)
    if amh_match:
        val = float(amh_match.group(1))
        if 0 < val < 50:
            data['AMH(ng/mL)'] = val

    if 'irregular' in text: data['Cycle(R/I)'] = 4
    elif 'regular' in text: data['Cycle(R/I)'] = 2

    age_match = re.search(r'(\d+)\s*(?:years old|yrs|age)', text)
    if age_match:
        val = int(age_match.group(1))
        if 10 < val < 60:
            data['Age'] = val

    if 'weight' in text and ('gain' in text or 'high' in text):
        data['Weight gain(Y/N)'] = 1

    return data

def tool_predict_pcos_enhanced(memory):
    try:
        pipeline = joblib.load('pcos_pipeline.pkl')
        feature_names = joblib.load('model_features.pkl')

        inputs = json.loads(memory.get_profile_json())
        input_df = pd.DataFrame([inputs])

        for col in feature_names:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[feature_names]

        prob = pipeline.predict_proba(input_df)[0][1]
        prediction = 1 if prob > 0.5 else 0

        result_text = "High Risk (Positive)" if prediction == 1 else "Low Risk (Negative)"
        confidence = f"{prob*100:.1f}%"

        advice = []
        if inputs['AMH(ng/mL)'] > 5.0: advice.append(medical_advice_db['high_amh'])
        if inputs['Cycle(R/I)'] == 4: advice.append(medical_advice_db['irregular_cycle'])
        if inputs['Weight gain(Y/N)'] == 1: advice.append(medical_advice_db['weight_gain'])
        if not advice: advice.append(medical_advice_db['general'])

        return {
            "result": result_text,
            "confidence": confidence,
            "advice": " ".join(advice)
        }

    except FileNotFoundError:
        return {"error": "Model not loaded. Run training script."}
    except Exception as e:
        return {"error": str(e)}

def tool_search_clinics(query):
    query = query.lower()
    results = [c for c in clinic_database if query in c['location'].lower() or query in c['name'].lower()]
    if not results: return "No clinics found in that area. Try 'Downtown' or 'Maadi'."
    return "\n".join([f"🏥 {r['name']} ({r['location']}) - {r['specialty']}" for r in results])

def tool_search_labs(query):
    query = query.lower()
    results = [l for l in lab_database if query in l['location'].lower() or any(query in t.lower() for t in l['tests'])]
    if not results: return "No specific labs found. Showing all: " + ", ".join([l['name'] for l in lab_database])
    return "\n".join([f"🧪 {r['name']} ({r['location']}) - Tests: {', '.join(r['tests'])}" for r in results])

def tool_book(service_type, details):
    ref = f"{service_type[0]}BK-{random.randint(1000,9999)}"
    return f"✅ SUCCESS: Booked {service_type} ({details}). Reference: {ref}"

class PCOS_System:
    def __init__(self):
        self.memory = SessionMemory()
        print("🤖 PCOS Assistant Initialized. (Type 'exit' to stop)")

    def handle_input(self, user_input):
        user_input_lower = user_input.lower()

        extracted_data = extract_medical_data_smart(user_input)
        if extracted_data:
            self.memory.update(extracted_data)
            updates = ", ".join([f"{k}: {v}" for k,v in extracted_data.items()])
            print(f"   [System Note: Updated profile with {updates}]")

        if any(w in user_input_lower for w in ['diagnose', 'predict', 'do i have', 'results', 'analysis']):
            if not self.memory.is_data_sufficient():
                return "I need a bit more info to give a prediction. Please tell me your AMH level or if your cycle is regular."

            res = tool_predict_pcos_enhanced(self.memory)
            if "error" in res: return f"Error: {res['error']}"

            return (f"\n📊 **Analysis Result:** {res['result']}\n"
                    f"🎯 **Confidence:** {res['confidence']}\n"
                    f"💡 **Medical Note:** {res['advice']}")

        elif 'lab' in user_input_lower or 'test' in user_input_lower:
            if 'book' in user_input_lower:
                return tool_book("Lab", "Standard Panel")
            search_term = "amh" if "amh" in user_input_lower else "general"
            return tool_search_labs(search_term)

        elif 'clinic' in user_input_lower or 'doctor' in user_input_lower:
            if 'book' in user_input_lower:
                return tool_book("Doctor", "Next Available Slot")

            locs = ['maadi', 'downtown', 'nasr city']
            found_loc = next((loc for loc in locs if loc in user_input_lower), "")
            return tool_search_clinics(found_loc if found_loc else user_input_lower)

        else:
            return "I can help with PCOS Analysis, Finding Clinics, or Booking Labs. Please share your symptoms (e.g., 'My AMH is 7') or ask for a clinic."

if __name__ == "__main__":
    system = PCOS_System()

    print("\n👋 Hello! I am your PCOS Intelligent Assistant.")
    print("   Tell me about your symptoms, or ask to find a doctor.")
    print("   [Type 'exit' or 'quit' to stop the program]")

    while True:
        try:
            user_text = input("\n👤 You: ")
            if user_text.lower() in ['exit', 'quit', 'stop']:
                print("👋 Goodbye! Stay healthy.")
                break

            response = system.handle_input(user_text)
            print(f"🤖 Assistant: {response}")

        except KeyboardInterrupt:
            break