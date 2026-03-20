#!/usr/bin/env python3

import os
import traceback
from dotenv import load_dotenv
from ddgs import DDGS
from huggingface_hub import InferenceClient

load_dotenv()


def search_duckduckgo(query: str, max_results: int = 5) -> str:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
        chunks = []
        for r in results:
            title = r.get("title", "")
            body = r.get("body", "")
            href = r.get("href", "")
            chunks.append(f"Title: {title}\nBody: {body}\nURL: {href}")
        return "\n\n".join(chunks)


class FootSeoAgent:
    def __init__(self):
        token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not token:
            raise ValueError("Missing HUGGINGFACEHUB_API_TOKEN in .env")

        self.client = InferenceClient(
            api_key=token,
            provider="auto",
        )

        self.model = os.getenv("HF_MODEL")
        if not self.model:
            raise ValueError("Missing HF_MODEL in .env")

    def generate_seo_draft(self, topic: str) -> str:
        results = search_duckduckgo(f'"{topic}" football soccer premier league')

        system_prompt = (
            "You are an expert football SEO writer. "
            "Write engaging, accurate, fan-friendly markdown articles. "
            "Do not invent stats or facts."
        )

        user_prompt = f"""Write an SEO football article about: "{topic}"

Search results:
{results[:3000]}

REQUIRED FORMAT:
# Catchy H1 Headline

**Meta Description:** one sentence under 160 characters

## H2 Subheading 1
2-3 engaging paragraphs

## H2 Subheading 2
2-3 engaging paragraphs

**Keywords:** keyword1, keyword2, keyword3, keyword4, keyword5
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=800,
                temperature=0.7,
            )
            return response.choices[0].message.content or "No content returned."

        except Exception as e:
            print("\n❌ FULL ERROR:")
            print(repr(e))
            traceback.print_exc()

            return (
                f"LLM failed: {repr(e)}\n\n"
                f"# {topic.title()}\n"
                f"**Discover {topic}**\n"
                f"**Keywords:** {topic.replace(' ', ', ')}"
            )