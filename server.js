const express = require('express');
const dotenv = require('dotenv');
const path = require('path');
const multer = require('multer');
const cors = require('cors');
const fetch = (...args) => import('node-fetch').then(({ default: fetch }) => fetch(...args));
const FormData = require('form-data');
const { GoogleGenAI } = require('@google/genai');

dotenv.config({ path: path.resolve(__dirname, '.env') });

const app = express();
app.use(express.json());
app.use(cors());
app.use(express.static(path.join(__dirname, './assets')));

const CLINIC_CONFIG = {
  diabetes: {
    tool_name: "predictDiabetes",
    description: "User suspects diabetes or wants a diabetes checkup.",
    fields: [
      { name: "gender", question: "What is your gender?", type: "enum", options: ["Male", "Female"], mandatory: true },
      { name: "age", question: "What is your age?", type: "number", mandatory: true },
      { name: "hypertension", question: "Do you suffer from hypertension?", type: "boolean", map: { yes: 1, no: 0 }, mandatory: false, suggest_lab: true },
      { name: "heart_disease", question: "Do you have any heart disease?", type: "boolean", map: { yes: 1, no: 0 }, mandatory: true },
      { name: "smoking_history", question: "What is your smoking history?", type: "enum", options: ["never", "current", "former", "ever", "not current"], mandatory: true },
      { name: "bmi", question: "What is your BMI?", type: "number", mandatory: false, suggest_lab: true },
      { name: "HbA1c_level", question: "What is your HbA1c level?", type: "number", mandatory: false, suggest_lab: true },
      { name: "blood_glucose_level", question: "What is your blood glucose level?", type: "number", mandatory: false, suggest_lab: true }
    ]
  },
  pcos: {
    tool_name: "predictPCOS",
    description: "User suspects PCOS.",
    fields: [
      { name: "age", question: "What is your age?", type: "number", mandatory: true },
      { name: "blood_group", question: "What is your blood group?", type: "enum", options: ["AB+", "AB-", "A+", "A-", "B+", "B-", "O+", "O-"], mandatory: false, suggest_lab: true },
      { name: "bmi", question: "What is your BMI?", type: "number", mandatory: true },
      { name: "pulse_rate", question: "What is your pulse rate?", type: "number", mandatory: false, suggest_lab: true }
    ]
  },
  brain_tumor: {
    tool_name: "predictBrainTumor",
    description: "User suspects a brain tumor.",
    fields: [
      { name: "image", question: "Please provide the MRI image path.", type: "string", mandatory: true }
    ]
  },
  heart_failure: {
    tool_name: "predictHeartFailure",
    description: "User suspects heart failure.",
    fields: [
      { name: "Age", question: "What is your age?", type: "number", mandatory: true },
      { name: "Sex", question: "What is your gender?", type: "enum", options: ["M", "F"], mandatory: true },
      { name: "ChestPainType", question: "What type of chest pain do you have?", type: "enum", options: ["ATA", "NAP", "ASY", "TA"], mandatory: false, suggest_lab: true },
      { name: "RestingBP", question: "What is your resting blood pressure?", type: "number", mandatory: false, suggest_lab: true },
      { name: "Cholesterol", question: "What is your cholesterol level?", type: "number", mandatory: false, suggest_lab: true },
      { name: "FastingBS", question: "What is your fasting blood sugar?", type: "number", mandatory: false, suggest_lab: true },
      { name: "MaxHR", question: "What is your maximum heart rate?", type: "number", mandatory: false, suggest_lab: true },
      { name: "RestingECG", question: "What are your resting ECG results?", type: "enum", options: ["Normal", "ST", "LVH"], mandatory: false, suggest_lab: true },
      { name: "ExerciseAngina", question: "Do you have chest pain during exercise?", type: "enum", options: ["Yes", "No"], mandatory: true },
      { name: "Oldpeak", question: "What is your ST depression (Oldpeak)?", type: "number", mandatory: false, suggest_lab: true },
      { name: "ST_Slope", question: "What is the slope of the peak exercise ST segment?", type: "enum", options: ["Up", "Flat", "Down"], mandatory: false, suggest_lab: true }
    ]
  }
};

const upload = multer({ storage: multer.memoryStorage() });
const ai = new GoogleGenAI({});

const stt = async (req) => {
  const audioBuffer = req.file.buffer;
    const form = new FormData();
    form.append('file', audioBuffer, {
      filename: `${Math.random().toString(36).substring(2, 10)}.webm`,
      contentType: 'audio/webm'
    });
    form.append('model_id', 'scribe_v1');
    form.append('language_code', req.body.lang == 'arabic' ? 'ar' : 'en');
    form.append('num_speakers', '1');

    const sttResponse = await fetch('https://api.elevenlabs.io/v1/speech-to-text', {
      method: 'POST',
      headers: {
        'xi-api-key': process.env.ELEVEN_API_KEY,
        ...form.getHeaders()
      },
      body: form
    });

    if (!sttResponse.ok) {
      const errText = await sttResponse.text();
      console.error('STT error:', errText);
      return res.status(502).send({ error: 'STT request failed', details: errText });
    }

    const stt_res = await sttResponse.json();
    const transcript = stt_res.text || stt_res.transcription || stt_res.result || '';
    return transcript;
  }

  const llm = async (req) => {
    const isArabic = req.body.lang === 'arabic';
  const langInstruction = isArabic
    ? "OUTPUT RULE: The 'message' field MUST be in Egyptian Arabic (لهجة مصرية). The 'reasoning' and technical keys MUST remain in English."
    : "OUTPUT RULE: The 'message' field MUST be in English.";
const ai_res = await ai.models.generateContent({
      model: 'gemini-2.5-pro',
      contents: `You are 'MedAssist', a strict medical triage bot.
    
    *** YOUR GOAL ***
    Identify the medical condition the user is checking for, collect the specific parameters required in the CONFIG below, and trigger the tool once ALL data is collected.

    *** THE CONFIGURATION (STRICT RULES) ***
    ${JSON.stringify(CLINIC_CONFIG)}

    *** OPERATING RULES ***
    1. **Context Analysis**: Look at the conversation history. Determine if the user is in the middle of a checkup (e.g., Diabetes).
    2. **Anti-Hallucination**: If the user is checking for Diabetes, NEVER ask questions from the PCOS list unless they explicitly change the subject.
    3. **Missing Data Loop**: 
       - Compare the collected data in the history against the 'fields' list for the current condition.
       - Identify the *first* missing field.
       - Ask the user for that specific field.
    4. **Handling 'I don't know'**:
       - If the field has 'suggest_lab': true, tell the user this info is needed from a lab test/doctor.
       - If the field has 'mandatory': true, ask them to provide an estimate or the exact value again.
    5. **Data Cleaning**:
       - Convert "twenty two" -> 22.
       - Convert "mail" -> "Male".
       - Convert "Yes"/"No" -> 1/0 (ONLY if the 'map' property exists for that field).
    6. **Tool Trigger**:
       - ONLY when ALL fields for the specific condition are collected, output the "tool" JSON.

    *** REQUIRED JSON OUTPUT FORMAT ***
    Return ONLY a single raw JSON object.

    Scenario A: You need to ask a question.
    {
      "message": "The text of your question here"
    }

    Scenario B: All data is ready. Call the tool.
    {
      "tool": {
        "name": "predictDiabetes",
        "params": {
          "age": 25,
          "gender": "Male",
          "hypertension": 0,
          ... (all other required fields)
        }
      }
    }

    Scenario C: User Input unclear.
    {
      "message": "I didn't understand that. Could you please repeat your [Parameter Name]?"
    }

    ${langInstruction}
  `
    });

    let aiText = (typeof ai_res === 'string') ? ai_res : (ai_res.text || ai_res.output || (ai_res.output && ai_res.output[0] && ai_res.output[0].content) || '');
    if(aiText.slice(0, 7) === "```json" && aiText.slice(-3) == "```") aiText = aiText.slice(7, -3)
    aiText = JSON.parse(aiText)
    return aiText
  }

const tts = async (res, aiText) => {
  const ttsPayload = {
      text: aiText.message,
      model_id: 'eleven_multilingual_v2'
    };

    const ttsResponse = await fetch('https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb?output_format=mp3_44100_128', {
      method: 'POST',
      headers: {
        'xi-api-key': process.env.ELEVEN_API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(ttsPayload)
    });

    if (!ttsResponse.ok) {
      const err = await ttsResponse.text();
      console.error('TTS error:', err);
      return res.status(502).send({ ai: aiText, tts_error: err });
    }

    return ttsResponse
}

const predictPCOS = async (data) => {
  const res = await fetch('http://127.0.0.1:8000/pcos', {
      method: 'POST',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    return res.text()
}

const predictDiabetes = async (data) => {
  const res = await fetch('http://127.0.0.1:8000/diabetes', {
      method: 'POST',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    return res.text()
}

const predictBrainTumor = async (image) => {
  const res = await fetch('http://127.0.0.1:8000/brainTumor', {
      method: 'POST',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({image})
    });

    return res.text()
}

const predictHeartFailure = async (data) => {
  const res = await fetch('http://127.0.0.1:8000/heartFailure', {
      method: 'POST',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    return res.text()
}

app.post('/voice', upload.single('audio'), async (req, res) => {
  try {
    if (!req.file || !req.file.buffer) {
      return res.status(400).send({ error: 'No audio file uploaded' });
    }
    req.body.context = JSON.parse(req.body.context)
    const transcript = await stt(req)
    req.body.context.push({user: transcript})

    let aiText = await gemini(req)
    if (aiText.tool != undefined){
      if (aiText.tool['name'] == 'predictDiabetes'){
        const toolRes = await predictDiabetes(aiText.tool.params)
        req.body.context.push({tool: toolRes})
        aiText = await gemini(req)
      }
    }
    const ttsResponse = await tts(res, aiText)

    const audioBuf = Buffer.from(await ttsResponse.arrayBuffer());
    const audioBase64 = audioBuf.toString("base64");
    res.json({
      agentMessage: aiText,
      userMessage: transcript,
      audio: audioBase64,
      format: "mp3"
    });

  } catch (e) {
    console.error(e);
    res.status(500).send('error');
  }
});

app.post('/text', async (req, res) => {
  try {
    let aiText = await llm(req)
    // let aiText = {"tool": {"name": "predictDiabetes", "params": {"age": 2, "gender": "Male", "hypertension": 0, "heart_disease": 0, "smoking_history": "never", "bmi": 22, "HbA1c_level": 150, "blood_glucose_level": 5}}}
    // let aiText = {"tool": {"name": "predictBrainTumor", "params": {"age": 22, "gender": "male", "hypertension": "yes", "heart_disease": "no", "smoking_history": "never", "bmi": 25, "HbA1c_level": 150, "blood_glucose_level": 5}}}
    // let aiText = {"tool": {"name": "predictPCOS", "params": {"age": 22, "blood_group": "A-", "bmi": 23, "pulse_rate": 70}}}
    // let aiText = {"tool": {"name": "predictHeartFailure", "params": {"Age": 22, "Sex": "M", "ChestPainType": 'ATA', "RestingBP": 150, "Cholesterol": 290, "FastingBS": 0, "RestingECG": 'Normal', "MaxHR": 170, "ExerciseAngina": 'N', "Oldpeak": 1, "ST_Slope": 'UP'}}}
    if (aiText.tool != undefined){
      if (aiText.tool.name == 'predictDiabetes'){
        const toolRes = await predictDiabetes(aiText.tool.params)
        console.log(toolRes)
        req.body.context.push({tool: toolRes})
        aiText = await llm(req)
      } else if (aiText.tool.name == 'predictPCOS'){
        const toolRes = await predictPCOS(aiText.tool.params)
        req.body.context.push({tool: toolRes})
        aiText = await llm(req)
      } else if (aiText.tool.name == 'predictBrainTumor'){
        const toolRes = await predictBrainTumor(req.body.image)
        req.body.context.push({tool: toolRes})
        aiText = await llm(req)
      } else if (aiText.tool.name == 'predictHeartFailure'){
        const toolRes = await predictHeartFailure(aiText.tool.params)
        req.body.context.push({tool: toolRes})
        aiText = await llm(req)
      }
    }
    res.json({
      agentMessage: aiText
    });

  } catch (e) {
    console.error(e);
    res.status(500).send('error');
  }
});

app.get('/', async (req, res) => {
  try {
    res.sendFile(path.join(__dirname, 'index.html'));
  } catch (e) {
    console.error(e);
    res.status(500).send('error');
  }
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`server started at: http://127.0.0.1:${port}`);
});
