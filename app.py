import hmac
import os

import streamlit as st
from agents import Runner

from agent import stock_analyst


st.set_page_config(page_title="AI Stock Analyst", page_icon="📈")


def check_password() -> bool:
    expected = st.secrets.get("APP_PASSWORD", "")
    if not expected:
        st.error("APP_PASSWORD is not configured in Streamlit secrets.")
        return False

    entered = st.text_input("Password", type="password")
    if not entered:
        return False

    if hmac.compare_digest(entered, expected):
        return True

    st.error("Incorrect password.")
    return False


api_key = st.secrets.get("OPENAI_API_KEY", "")
if not api_key:
    st.error("OPENAI_API_KEY is not configured in Streamlit secrets.")
    st.stop()

os.environ["OPENAI_API_KEY"] = api_key

st.title("📈 AI Stock Analyst")
st.caption("My first AI agent — powered by OpenAI Agents SDK")

if not check_password():
    st.stop()

company = st.text_input("Company to analyse", value="Societe Generale")

if st.button("Analyse", type="primary", use_container_width=True):
    if not company.strip():
        st.warning("Enter a company name.")
    else:
        task = f"""
Analyse {company.strip()} as an equity-research screening candidate.
Use current information and perform whatever web searches are needed.
Give me the most decision-useful facts, risks, and a clear screening verdict.
"""
        with st.spinner("Agent is researching and analysing..."):
            try:
                result = Runner.run_sync(stock_analyst, task)
                st.markdown(result.final_output)
            except Exception as exc:
                st.error(f"Agent error: {exc}")

st.caption("Research assistance only — not personalized investment advice.")
