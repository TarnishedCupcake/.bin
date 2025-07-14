import streamlit as st
import random
import requests
import os

# --- Agent Styles ---
STYLE_PROMPTS = {
    "Calm": "Respond in a calm, logical, and balanced tone.",
    "Aggressive": "Debate in a strong, confrontational, and assertive manner.",
    "Sarcastic": "Use sarcasm and irony while presenting your points.",
    "Emotional": "Appeal to values and emotions strongly in your arguments.",
    "Academic": "Use academic language, references, and structured logic.",
    "Random": "Use a unique and unpredictable speaking style."
}

# --- Prompt Formatter ---
def format_prompt(role, style, history, topic):
    style_prompt = STYLE_PROMPTS.get(style, "Respond objectively.")
    return f"You are {role}. {style_prompt}\nTopic: \"{topic}\"\nDebate history so far:\n{history}\nTake a clear position and defend it. Do not change the topic."

# --- LLM Completion using Ollama ---
def get_response(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt, "stream": False}
    )
    return response.json()["response"].strip()

# --- Judge Agent ---
def judge_debate(history, topic):
    judge_prompt = f"Analyze the following debate on: '{topic}'.\nDebate log:\n{history}\n\nScore each debater (A and B), explain your reasoning, and declare a winner."
    return get_response(judge_prompt)

# --- Streamlit UI ---
st.set_page_config(page_title="AI Debate Judge", layout="wide")
st.title("🧠 AI Debate Judge")

# --- Input Section ---
col1, col2 = st.columns(2)
with col1:
    topic = st.text_input("Debate Topic:", "What is the best way to raise a toddler as a new parent?")
    rounds = st.slider("Number of Rounds", 1, 10, 3)
with col2:
    agent_a_style = st.selectbox("Agent A Style", list(STYLE_PROMPTS.keys()))
    agent_b_style = st.selectbox("Agent B Style", list(STYLE_PROMPTS.keys()))

if st.button("Start Debate"):
    with st.spinner("Running debate..."):
        debate_log = ""
        for i in range(1, rounds + 1):
            st.subheader(f"🗣️ Round {i}")

            prompt_a = format_prompt("Debater A", agent_a_style, debate_log, topic)
            response_a = get_response(prompt_a)
            st.markdown(f"**Agent A ({agent_a_style}):** {response_a}")

            debate_log += f"Round {i} - A: {response_a}\n"

            prompt_b = format_prompt("Debater B", agent_b_style, debate_log, topic)
            response_b = get_response(prompt_b)
            st.markdown(f"**Agent B ({agent_b_style}):** {response_b}")

            debate_log += f"Round {i} - B: {response_b}\n"

        # Judge Evaluation
        st.subheader("⚖️ Judge Verdict")
        judgment = judge_debate(debate_log, topic)
        st.markdown(judgment)

        # Save results
        st.download_button("💾 Download Debate Log", data=debate_log, file_name="debate_log.txt")
