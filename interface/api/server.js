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

  const gemini = async (req) => {
const ai_res = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: `You are a medical bot who directs people to the appropriate doctor according to their symptoms
you can keep asking for the symptoms like blood pressure and age to gather information to make a check up to the patient
the following clinics are available attached with the questions or required symptoms (columns formate will be like that: symptom_name_to_ask_user|symptom_name_to_use_tools|[array_of_valid_values] or valid values condition|suggest_going_to_laboratory_if_user_dont_know)

diabetes:
gender|gender|[Male,Female]|no(ask user again)
age|age|any positive integer|no(ask user again)
hypertension|hypertension|[1,0]|yes
heart disease|heart_disease|[1,0]|no(ask user again)
smoking history|smoking_history|['never', 'current', 'former', 'ever', 'not current']|no(ask user again)
bmi|bmi|any positive number|yes
H B A 1 C level|HbA1c_level|any positive number|yes
blood glucose level|blood_glucose_level|any positive number|yes

PCOS:
age|age|any positive integer|no(ask user again)
blood group|blood_group|[AB+, AB-, A+, A-, B+, B-, O+, O-]|yes
bmi|bmi|positive number|no(ask user again)
pulse rate|pulse_rate|positive number|yes

brain tumor:
image path|image_path|valid path|no(ask user again)

heart failure:
age|Age|any positive integer|no(ask user again)
gender|Sex|[M, F]|no(ask user again)
Chest pain type|ChestPainType|[ATA, NAP, ASY, TA]|yes
Resting Blood Pressure|RestingBP|positive number|yes
cholesterol|Cholesterol|positive number|yes
Fasting Blood Sugar|FastingBS|positive number|yes
Maximum Heart Rate|Cholesterol|positive number|yes
Resting Electrocardiographic results|RestingECG|[Normal, ST, LVH]|yes
chest pain during exercise|ExerciseAngina|[Yes, No]|no(ask user again)
ST segment|Oldpeak|positive number|yes
ST slope|ST_Slope|[Up, Flat, Down]|yes


the following are the available tools to call:
1- predictDiabetes: predicts diabetes and takes age, gender, hypertension, heart_disease, smoking_history, bmi, HbA1c_level, blood_glucose_level as parameters
2- predictPCOS: predicts PCOS and takes  age, gender, blood_group, hemoglobin, bmi
3- predictBrainTumor: predicts brain tumor and doesn't take parameters


you must ask all required questions before using a dependant tool
the user may answer like "i am a man" instead of "male" or make some misspelling like "mail" instead of man or any similar thing, it is ok
your role is to generate answers in VALID json formate like the following examples
{"message": "what is your age ?"}
{"tool": {"name": "predictDiabetes", "params": {"age": 22, "gender": "Male", "hypertension": 1, "heart_disease": 0, "smoking_history": "never", "bmi": 25, "HbA1c_level": 150, "blood_glucose_level": 5}}}

NEVER make the output look like this
\`\`\`json
{
  "message": "Hi, I'm SHS chatbot. How can I help you?",
  "tools": []
}
\`\`\`

MAKE THE OUTPUT A VALID JSON STRING SO THAT I CAN DIRECTLY CONVERT IT TO JSON OBJECT

note that numbers can be written as twenty two point o4 or in any formate of numbers

conversation context example
[{agent: "Hi, i'm SHS chatbot. how can i help you ?"},
{user: "i want to make a check up, i suspect that i have diabetes"},
{agent: "what is your age"},
{user: "twenty two"},
{agent: "what is your smoking history ?"},
{user: "i dont know"},
{agent: "this information is too important, please answer, what is your smoking history ?"},
{user: "i never smoked"},
{agent: "what is you gender ?"},
{user: "male"},
{agent: "do you have hypertension ?"},
{user: "no"},
{agent: "do you have any heart disease ?"},
{user: "no"},
{agent: "what is your bmi ?"},
{user: "twenty five"},
{agent: "what is your H B A 1 C level ?"},
{user: "five"},
{agent: "what is your blood glucose level ?"},
{user: "one hundred and fifty"},
{tool: "diabetes prediction result is: 10%"},
{agent: "your propability to have diabetes is 10%. do you want to book an appointment with a doctor to make sure ?"},
{user: "yes please"},
{tool: "appointment booked with doctor mokhtar, 31-01-2026, 7:30pm"},
{agent: "you have an appointment with doctor mokhtar on 31-01-2026 at 7:30 PM. have a nice day"}
]

if there any answer that is not valid or not clear like

[{agent: "what is your age"},
{user: "red"}]

or

[{agent: "do you suffer from hypertension"},
{user: "day"}]

you can ask the user to repeat the answer

DONT AUTO COMPLETE INFORMATION

current coversation context is:
${req.body.context}

answer in ${req.body.lang == 'arabic' ? 'arabic specially egyptian accent' : 'english'}
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
    let aiText = await gemini(req)
    // let aiText = {"tool": {"name": "predictDiabetes", "params": {"age": 22, "gender": "Male", "hypertension": 1, "heart_disease": 0, "smoking_history": "never", "bmi": 25, "HbA1c_level": 150, "blood_glucose_level": 5}}}
    // let aiText = {"tool": {"name": "predictBrainTumor", "params": {"age": 22, "gender": "male", "hypertension": "yes", "heart_disease": "no", "smoking_history": "never", "bmi": 25, "HbA1c_level": 150, "blood_glucose_level": 5}}}
    // let aiText = {"tool": {"name": "predictPCOS", "params": {"age": 22, "blood_group": "A-", "bmi": 23, "pulse_rate": 70}}}
    // let aiText = {"tool": {"name": "predictHeartFailure", "params": {"Age": 22, "Sex": "M", "ChestPainType": 'ATA', "RestingBP": 150, "Cholesterol": 290, "FastingBS": 0, "RestingECG": 'Normal', "MaxHR": 170, "ExerciseAngina": 'N', "Oldpeak": 1, "ST_Slope": 'UP'}}}
    if (aiText.tool != undefined){
      if (aiText.tool.name == 'predictDiabetes'){
        const toolRes = await predictDiabetes(aiText.tool.params)
        req.body.context.push({tool: toolRes})
        aiText = await gemini(req)
      } else if (aiText.tool.name == 'predictPCOS'){
        const toolRes = await predictPCOS(aiText.tool.params)
        req.body.context.push({tool: toolRes})
        aiText = await gemini(req)
      } else if (aiText.tool.name == 'predictBrainTumor'){
        const toolRes = await predictBrainTumor(req.body.image)
        req.body.context.push({tool: toolRes})
        aiText = await gemini(req)
      } else if (aiText.tool.name == 'predictHeartFailure'){
        const toolRes = await predictHeartFailure(aiText.tool.params)
        console.log(toolRes)
        req.body.context.push({tool: toolRes})
        aiText = await gemini(req)
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

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`server started at: http://127.0.0.1:${port}`);
});
