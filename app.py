import streamlit as st
from st_audiorec import st_audiorec
import numpy as np
import soundfile as sf
from google import genai
from google.genai import types
from gtts import gTTS
import tempfile
import os

# === CONFIG ===
client = genai.Client(api_key="AIzaSyBz7xWDWXbkyA5SRFOKE0VPm4m0Uifmf0c")  # Replace with your key
MODEL = "gemini-1.5-flash"
PDF_FILE = "Saveetha_Engineering_College.pdf"
TTS_AUDIO_FILE = "summary_audio.mp3"

st.set_page_config(page_title="Voice AI", layout="centered")
st.title("🎤 Voice AI (Mic Permission Required)")
st.markdown("Record your voice, transcribe it, summarize PDF, and play summary!")

# === AUDIO RECORDER ===
st.info("Please click the mic below and speak.")
wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    # Save audio to temporary .wav
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(wav_audio_data)
        audio_path = tmpfile.name
        st.success("✅ Audio recorded!")

    # === Transcript using Gemini ===
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    transcript_response = client.models.generate_content(
        model=MODEL,
        contents=[
            "Transcript the audio clip",
            types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
        ]
    )
    transcript = transcript_response.text
    st.subheader("📝 Transcript")
    st.write(transcript)

    # === Refined version
    refined = client.models.generate_content(
        model=MODEL,
        contents=transcript,
        config=types.GenerateContentConfig(
            system_instruction="Replace any sentence with a version that focuses only on Saveetha Engineering College without changing the meaning."
        )
    )
    refined_text = refined.text
    st.subheader("🎯 Refined Text")
    st.write(refined_text)

    # === Summarize PDF + Refined Text
    with open(PDF_FILE, "rb") as f:
        pdf_bytes = f.read()

    pdf_summary = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
            refined_text + " in simple 2-3 sentences"
        ]
    )

    summary_text = pdf_summary.text
    st.subheader("📚 Summary from PDF + Voice")
    st.write(summary_text)


