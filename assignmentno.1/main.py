# streamlit run app.py

import streamlit as st
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Validate API key
if not gemini_api_key:
    st.error("GEMINI_API_KEY is not set. Please check your .env file.")
    st.stop()

# Set up Gemini client
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Create model instance
model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",  # You may need to change this to a model supported by Gemini's OpenAI wrapper
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# --- Streamlit UI ---
st.title("🌐 Urdu Translator: English & French")

urdu_text = st.text_input("✍️ Enter some text in Urdu:")


agent = Agent(
            name="Writer Agent",
            instructions=urdu_text
        )
#st.success("Translation complete!")


async def run_agent(agent, config):
    return await Runner.run(
        agent,
        input="Convert to English and French , put colourful asteriks in gaps between two translations and give title of english and french to respective translations.Also,dont show this text in output response.no text at all.Thanks",
        run_config=config
    )

response = asyncio.run(run_agent(agent, config))


        # Show translated output
st.text_area("📝 Output:", value=response.final_output, height=800)

