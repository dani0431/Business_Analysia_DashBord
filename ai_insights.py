"""
ai_insights.py
Sends a compact statistical summary of the dataset to Claude and asks for
structured business insights, anomalies, and recommendations.

We never send the raw dataset to the model — only the profiled summary —
to keep costs low and avoid context-window issues with large files.
"""

import os
import json
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a senior business data analyst. You will be given a
statistical profile of a company's dataset (not the raw data). Based only on
this profile, identify the most important business insights, trends,
anomalies, and risks, and provide actionable recommendations.

Respond ONLY with valid JSON in this exact structure, with no preamble,
no markdown code fences, and no extra commentary:

{
  "summary": "2-3 sentence overview of the dataset and what it likely represents for the business",
  "insights": [
    {
      "title": "short insight title",
      "detail": "1-3 sentence explanation grounded in the stats provided",
      "type": "trend" | "anomaly" | "opportunity" | "risk"
    }
  ],
  "recommendations": [
    "short actionable recommendation"
  ]
}

Provide 3 to 6 insights and 2 to 5 recommendations. Be specific and reference
actual column names and numbers from the profile where possible. Do not
invent data that isn't supported by the profile."""


@st.cache_data(show_spinner=False)
def get_ai_insights(profile_text: str) -> dict:
    """
    Call the Anthropic API with the dataset profile summary and return
    parsed structured insights. Cached by Streamlit so repeated runs on
    the same profile don't re-call the API.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {
            "error": "No ANTHROPIC_API_KEY found. Add it to your .env file."
        }

    client = Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Here is the dataset profile:\n\n{profile_text}",
                }
            ],
        )

        raw_text = "".join(
            block.text for block in response.content if block.type == "text"
        )

        # Defensive cleanup in case the model wraps output in code fences
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json\n", "", 1)

        parsed = json.loads(cleaned)
        return parsed

    except json.JSONDecodeError:
        return {"error": "AI response could not be parsed as JSON.", "raw": raw_text}
    except Exception as e:
        return {"error": f"AI request failed: {e}"}
