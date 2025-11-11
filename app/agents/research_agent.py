# app/agents/research_agent.py

import os
import json
import requests
from datetime import datetime
from app.utils.llm_client import LLMClient
from app.utils.config import NEWS_API_KEY

CACHE_DIR = ".cache/research_agent"
LOG_DIR = "outputs/logs/research_agent"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


class ResearchAgent:
    """Fetches news and environmental context for a given site using public data + LLM summarization."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    # -----------------------------
    # STEP 1: Fetch news from API (with caching and fallback)
    # -----------------------------
    def fetch_news(self, address: str, max_articles: int = 5):
        """Use NewsAPI to get solar-related headlines for a region, with caching & fallback."""
        cache_path = os.path.join(CACHE_DIR, f"{address.replace(' ', '_')}.json")

        # Use cache if available (within 24h)
        if os.path.exists(cache_path):
            mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
            if (datetime.now() - mtime).seconds < 86400:
                with open(cache_path, "r") as f:
                    return json.load(f)

        if not NEWS_API_KEY:
            return [
                "No NEWS_API_KEY found — using static mock headlines.",
                f"{address} announces new solar incentives",
                "No local moratoriums reported in recent months.",
            ]

        query = f"{address} solar energy project OR renewable policy OR moratorium"
        url = (
            f"https://newsapi.org/v2/everything?q={query}"
            f"&language=en&sortBy=relevancy&pageSize={max_articles}&apiKey={NEWS_API_KEY}"
        )

        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            data = res.json()
            articles = [
                a["title"]
                for a in data.get("articles", [])
                if any(k in a["title"].lower() for k in ["solar", "energy", "policy", "renewable"])
            ]
            if not articles:
                articles = ["No recent relevant solar or policy news found."]
        except Exception as e:
            articles = [f"NewsAPI error: {e}"]

        # Cache results
        with open(cache_path, "w") as f:
            json.dump(articles, f, indent=2)

        return articles

    # -----------------------------
    # STEP 2: Analyze with LLM (JSON validation & logging)
    # -----------------------------
    def analyze_policy_environment(self, address: str, headlines: list[str]):
        """Use GPT to summarize policy favorability with structured JSON output."""
        system_prompt = (
            "You are a renewable energy policy analyst. "
            "Given recent headlines, determine whether the local environment is favorable "
            "for new solar projects. Consider permitting support, community acceptance, and environmental policies."
        )

        user_prompt = f"""
Address: {address}

Recent Headlines:
{headlines}

Please:
1. Summarize the policy and regulatory tone in 3–5 sentences.
2. Identify up to 3 risks or red flags.
3. Assign a favorability score (0–100).
4. Output your answer as JSON with keys: summary, risks, score, sentiment.
"""

        raw_response = self.llm.chat(system_prompt, user_prompt)

        # Try parsing LLM output into valid JSON
        try:
            analysis = json.loads(raw_response)
        except json.JSONDecodeError:
            # fallback heuristic if model returns text instead of JSON
            analysis = {
                "summary": raw_response[:300] + "...",
                "risks": ["Malformed LLM JSON output"],
                "score": 50,
                "sentiment": "unknown",
            }

        # Normalize missing fields
        analysis.setdefault("summary", "No summary provided.")
        analysis.setdefault("risks", [])
        analysis.setdefault("score", 50)
        analysis.setdefault("sentiment", "neutral")

        # Save LLM trace (prompt + raw output)
        log_path = os.path.join(LOG_DIR, f"{address.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(log_path, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "address": address,
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "raw_response": raw_response,
                    "parsed_analysis": analysis,
                },
                f,
                indent=2,
            )

        return analysis

    # -----------------------------
    # STEP 3: Run pipeline with graceful fallback
    # -----------------------------
    def run(self, address: str):
        """Run the full research pipeline end-to-end with error handling."""
        print(f"🔍 Running ResearchAgent for: {address}")
        try:
            news = self.fetch_news(address)
            analysis = self.analyze_policy_environment(address, news)
        except Exception as e:
            analysis = {
                "summary": f"Error occurred: {e}",
                "risks": ["Unhandled exception during research agent run"],
                "score": 0,
                "sentiment": "error",
            }
            news = []

        return {
            "agent": "ResearchAgent",
            "address": address,
            "news_headlines": news,
            "analysis": analysis,
        }
