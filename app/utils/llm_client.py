import re
import os
import json
from openai import OpenAI
from app.utils.config import OPENAI_API_KEY


class LLMClient:
    def __init__(self, model="gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "❌ Missing OPENAI_API_KEY. Please set it in your .env file or GitHub Secrets."
            )
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, system_prompt, user_prompt):
        """Send structured prompt to OpenAI and clean the response for JSON parsing."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        user_prompt
                        + "\n\nIMPORTANT: Respond *only* in valid JSON. "
                          "Do not include markdown code blocks or explanations."
                    ),
                },
            ],
            temperature=0.3,
        )

        raw_content = response.choices[0].message.content.strip()

        # --- Clean markdown wrappers ---
        cleaned = re.sub(r"```(?:json)?", "", raw_content, flags=re.IGNORECASE)
        cleaned = cleaned.strip("` \n")

        # --- Validate JSON safely ---
        try:
            json.loads(cleaned)
        except Exception:
            print("⚠️ LLM returned non-JSON or partial output, passing raw string.")
            return cleaned

        return cleaned
