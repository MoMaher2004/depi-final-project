import fs from "fs";
import FormData from "form-data";
import fetch from "node-fetch";
import dotenv from "dotenv";

dotenv.config();

const apiKey = process.env.ELEVEN_API_KEY;
if (!apiKey) {
    console.error("❌ Missing ELEVEN_API_KEY");
    process.exit(1);
}

async function transcribeLocalFile() {
    const audioPath = "./sample.ogg"; // your stored audio
    const file = fs.readFileSync(audioPath);

    const form = new FormData();
    form.append("file", file, "sample.ogg");
    form.append("model_id", "scribe_v1");

    const response = await fetch(
        "https://api.elevenlabs.io/v1/speech-to-text",
        {
            method: "POST",
            headers: {
                "xi-api-key": apiKey,
            },
            body: form
        }
    );

    const result = await response.json();
    console.log(result);
    console.log(form);
}

transcribeLocalFile();
