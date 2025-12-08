const express = require('express');
const dotenv = require('dotenv');
const path = require('path');
const multer = require('multer');
const cors = require('cors');
const fetch = (...args) => import('node-fetch').then(({ default: fetch }) => fetch(...args));
const FormData = require('form-data');
const OpenAI = require('openai');

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
    ],
    params_to_pass: [
      'gender',
      'age',
      'hypertension',
      'heart_disease',
      'smoking_history',
      'bmi',
      'HbA1c_level',
      'blood_glucose_level',
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
    ],
    params_to_pass: [
      'age',
      'blood_group',
      'bmi',
      'pulse_rate',
    ]
  },
  brain_tumor: {
    tool_name: "predictBrainTumor",
    description: "User suspects a brain tumor.",
    fields: [
      { name: "image", question: "Please provide the MRI image path.", type: "string", mandatory: true }
    ],
    params_to_pass: []
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
    ],
    params_to_pass: [
      'Age',
      'Sex',
      'ChestPainType',
      'RestingBP',
      'Cholesterol',
      'FastingBS',
      'MaxHR',
      'RestingECG',
      'ExerciseAngina',
      'Oldpeak',
      'ST_Slope'
    ]
  },
  chronic_kideny: {
    tool_name: "predictChronicKidney",
    description: "User suspects heart failure.",
    fields: [
      { name: "Bp", question: "What is your Blood Pressure?", type: "number", mandatory: true },
      { name: "Sg", question: "What is your Specific Gravity?", type: "number", mandatory: true },
      { name: "Al", question: "What is your Albumin?", type: "number", mandatory: true },
      { name: "Su", question: "What is your Sugar?", type: "number", mandatory: true },
      { name: "Rbc", question: "What is your Red Blood Cell?", type: "number", mandatory: true },
      { name: "Bu", question: "What is your Blood Urea?", type: "number", mandatory: true },
      { name: "Sc", question: "What is your Serum Creatinine?", type: "number", mandatory: true },
      { name: "Sod", question: "What is your Sodium?", type: "number", mandatory: true },
      { name: "Pot", question: "What is your Pottasium?", type: "number", mandatory: true },
      { name: "Hemo", question: "What is your Blood Pressure?", type: "number", mandatory: true },
      { name: "Wbcc", question: "What is your White Blood Cell Count?", type: "number", mandatory: true },
      { name: "Rbcc", question: "What is your Red Blood Cell Count?", type: "number", mandatory: true },
      { name: "Htn", question: "What is your Hypertension?", type: "enum", options: ["yes", "no"], mandatory: true },
    ],
    params_to_pass: [
      'Bp',
      'Sg',
      'Al',
      'Su',
      'Rbc',
      'Bu',
      'Sc',
      'Sod',
      'Pot',
      'Hemo',
      'Wbcc',
      'Rbcc',
      'Htn'
    ]
  }
};

const upload = multer({ storage: multer.memoryStorage() });
const deepseek = new OpenAI({
  apiKey: process.env.DEEPSEEK_API_KEY,
  baseURL: 'https://api.deepseek.com'
});

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
  const langInstruction = (req.body.lang === 'arabic')
    ? "OUTPUT RULE: The 'message' field MUST be in Egyptian Arabic (لهجة مصرية). The 'reasoning' and technical keys MUST remain in English."
    : "OUTPUT RULE: The 'message' field MUST be in English.";

  const fewShotExamples = `
    *** FEW-SHOT EXAMPLES (Follow this logic) ***
    Example 1 (Asking for missing info):
    User: "I think I have diabetes."
    Context: []
    Response: {
      "reasoning": "User initiated diabetes check. Missing 'gender' and 'age'. I will ask for gender first.",
      "message": "Okay, let's check that. First, are you Male or Female?"
    }

    Example 2 (Handling 'I don't know' for lab data):
    User: "I don't know my HBA1c level."
    Context: [...diabetes data...]
    Response: {
      "reasoning": "Field 'HbA1c_level' has suggest_lab=true. User doesn't know. I should suggest checking a lab report.",
      "message": "That's okay. This is usually found in your blood test report. If you don't have it handy, I can suggest a laboratory to visit, do you want me to suggest some laboratories ?"
    }

    Example 3 (Triggering Tool):
    User: "I'm 25, male, no hypertension, no heart disease, never smoked."
    Context: [...all mandatory diabetes fields present...]
    Response: {
      "reasoning": "All mandatory fields for diabetes are collected. I can now trigger the prediction.",
      "tool": {
        "name": "predictDiabetes",
        "params": { "age": 25, "gender": "Male", "hypertension": 0, "heart_disease": 0, "smoking_history": "never" }
      }
    }

    Example 4 (Triggering Image-Only-based Tool):
    User: "I want you to check my MRI image of my brain."
    Context: [...tells that image is attached...]
    Response: {
      "reasoning": "MRI image of brain is gained. I can now trigger the prediction.",
      "tool": {
        "name": "predictBrainTumor",
        "params": {}
      }
    }
  `;

  const systemPrompt = `
    [ROLE]
    You are 'MedAssist', a professional medical triage bot.
    
    [GOAL]
    Collect specific medical parameters from the user to run a prediction tool. Do not give medical advice.
    
    [DATA CONFIGURATION]
    ${JSON.stringify(CLINIC_CONFIG)}

    [OPERATING RULES]
    1. **Identify Condition**: Based on the user's input, decide which condition (diabetes, pcos, etc.) they are checking.
    2. **Check Missing Fields**: Compare the conversation history with the 'fields' list in [DATA CONFIGURATION].
    3. **One Step at a Time**: Ask for ONLY ONE missing field at a time.
    4. **Data Cleaning**: 
       - If user says "mail" or "man", map it to "Male".
       - If user says "twenty", map it to 20.
    5. **Chain of Thought**: Before answering, fill the "reasoning" field to explain what data you have and what you need next.
    6. **Tool Results**: By calling a tool successfully, it may say that there is a missing field or provide the result report, reformate this report and send it to the user.

    ${fewShotExamples}

    ${langInstruction}
    
    [OUTPUT FORMAT]
    Return ONLY valid JSON. No markdown formatting.
    Format: { "reasoning": "string", "message": "string" } OR { "reasoning": "string", "tool": { ... } }
  `;

  try {
    const completion = await deepseek.chat.completions.create({
      model: "deepseek-chat",
      messages: [
        {
          role: "system",
          content: systemPrompt
        },
        {
          role: "user",
          content: `Current Conversation Context: ${JSON.stringify(req.body.context)}`
        }
      ],
      temperature: 0.2,
      response_format: { type: "json_object" }
    });

    let aiText = completion.choices[0].message.content;
    
    if (aiText.startsWith("```json")) {
      aiText = aiText.replace(/```json|```/g, "");
    }
    
    return JSON.parse(aiText.trim());
  } catch (error) {
    console.error("DeepSeek API error:", error);
    throw new Error("Failed to get response from AI model");
  }
};

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

const predictChronicKidney = async (data) => {
  const res = await fetch('http://127.0.0.1:8000/kidney', {
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

    let aiText = await llm(req)
    // let aiText = {"tool": {"name": "predictDiabetes", "params": {"age": 2, "gender": "Male", "hypertension": 0, "heart_disease": 0, "smoking_history": "never", "bmi": 22, "HbA1c_level": 150, "blood_glucose_level": 5}}}
    // let aiText = {"tool": {"name": "predictBrainTumor"}}
    // let aiText = {"tool": {"name": "predictPCOS", "params": {"age": 22, "blood_group": "A-", "bmi": 23, "pulse_rate": 70}}}
    // let aiText = {"tool": {"name": "predictHeartFailure", "params": {"Age": 22, "Sex": "M", "ChestPainType": 'ATA', "RestingBP": 150, "Cholesterol": 290, "FastingBS": 0, "RestingECG": 'Normal', "MaxHR": 170, "ExerciseAngina": 'N', "Oldpeak": 1, "ST_Slope": 'UP'}}}
    for (let i=0;i<5;i++){
      if(aiText.tool == undefined) break 
      console.log(`loop entered ${i}`)
      if (aiText.tool.name == 'predictDiabetes'){
        const toolRes = await predictDiabetes(aiText.tool.params)
        console.log(toolRes)
        req.body.context.push({tool: toolRes})
        aiText = await llm(req)
      } else if (aiText.tool.name == 'predictPCOS'){
        const toolRes = await predictPCOS(aiText.tool.params)
        console.log(toolRes)
        req.body.context.push({tool: toolRes})
        aiText = await llm(req)
      } else if (aiText.tool.name == 'predictBrainTumor'){
        const toolRes = await predictBrainTumor(req.body.image)
        console.log(toolRes)
        req.body.context.push({tool: toolRes})
        aiText = await llm(req)
      } else if (aiText.tool.name == 'predictHeartFailure'){
        const toolRes = await predictHeartFailure(aiText.tool.params)
        console.log(toolRes)
        req.body.context.push({tool: toolRes})
        aiText = await llm(req)
      } else if (aiText.tool.name == 'predictChronicKidney'){
        const toolRes = await predictChronicKidney(aiText.tool.params)
        console.log(toolRes)
        req.body.context.push({tool: toolRes})
        aiText = await llm(req)
      }
    }
    const ttsResponse = await tts(res, aiText)

    const audioBuf = Buffer.from(await ttsResponse.arrayBuffer());
    const audioBase64 = audioBuf.toString("base64");
    return res.json({
      agentMessage: aiText,
      userMessage: transcript,
      audio: audioBase64,
      format: "mp3"
    });

  } catch (e) {
    console.error(e);
    return res.status(500).send('error');
  }
});

app.post('/text', async (req, res) => {
  try {
    let aiText = await llm(req)
    // let aiText = {"tool": {"name": "predictDiabetes", "params": {"age": 2, "gender": "Male", "hypertension": 0, "heart_disease": 0, "smoking_history": "never", "bmi": 22, "HbA1c_level": 150, "blood_glucose_level": 5}}}
    // let aiText = {"tool": {"name": "predictBrainTumor"}}
    // let aiText = {"tool": {"name": "predictPCOS", "params": {"age": 22, "blood_group": "A-", "bmi": 23, "pulse_rate": 70}}}
    // let aiText = {"tool": {"name": "predictHeartFailure", "params": {"Age": 22, "Sex": "M", "ChestPainType": 'ATA', "RestingBP": 150, "Cholesterol": 290, "FastingBS": 0, "RestingECG": 'Normal', "MaxHR": 170, "ExerciseAngina": 'N', "Oldpeak": 1, "ST_Slope": 'UP'}}}
    for (let i=0;i<5;i++){
      if(aiText.tool == undefined) break 
      console.log(`loop entered ${i}`)
      if (aiText.tool.name == 'predictDiabetes'){
        const toolRes = await predictDiabetes(aiText.tool.params)
        console.log(toolRes)
        req.body.context.push({tool: toolRes})
        aiText = await llm(req)
      } else if (aiText.tool.name == 'predictPCOS'){
        const toolRes = await predictPCOS(aiText.tool.params)
        console.log(toolRes)
        req.body.context.push({tool: toolRes})
        aiText = await llm(req)
      } else if (aiText.tool.name == 'predictBrainTumor'){
        const toolRes = await predictBrainTumor(req.body.image)
        console.log(toolRes)
        req.body.context.push({tool: toolRes})
        aiText = await llm(req)
      } else if (aiText.tool.name == 'predictHeartFailure'){
        const toolRes = await predictHeartFailure(aiText.tool.params)
        console.log(toolRes)
        req.body.context.push({tool: toolRes})
        aiText = await llm(req)
      } else if (aiText.tool.name == 'predictChronicKidney'){
        const toolRes = await predictChronicKidney(aiText.tool.params)
        console.log(toolRes)
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
