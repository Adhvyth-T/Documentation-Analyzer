from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import httpx
import os
from typing import Optional, List, Dict
import textstat
import re
import json
import undetected_chromedriver as uc
from playwright.async_api import async_playwright
import asyncio


async def _fetch_and_clean(url: str) -> str:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            ))
            page = await context.new_page()
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("networkidle")

            html = await page.content()
            await browser.close()

            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator="\n", strip=True)

            # Force UTF-8 safe printing
            safe_text = text.encode("utf-8", errors="ignore").decode("utf-8")
            
            return safe_text

    except Exception as e:
        raise ValueError(f"Failed to fetch URL {url}: {str(e)}")

def fetch_and_clean(url: str) -> str:
    return asyncio.run(_fetch_and_clean(url))


def chunk_text(text: str) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50
    )
    return splitter.create_documents([text])


def create_vector_store(chunks: List[Document]):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(chunks, embeddings)


def query_openrouter(prompt: str, context: str, api_key: str, model: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a documentation analyst."},
            {"role": "user", "content": f"Context:\n{context}\n\nTask: {prompt}"}
        ]
    }

    response = httpx.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"OpenRouter API Error: {response.status_code} - {response.text}")

    return response.json()['choices'][0]['message']['content']


def extract_json_objects(text: str):
    """Extracts valid JSON objects from a string, ignoring markdown-style code fences."""
    json_objects = []
    brace_stack = []
    start_index = None

    # Preprocess: Remove markdown code fences like ```json ... ```
    cleaned_text = re.sub(r"```json\s*", "", text)
    cleaned_text = re.sub(r"```", "", cleaned_text)

    for i, char in enumerate(cleaned_text):
        if char == '{':
            if not brace_stack:
                start_index = i
            brace_stack.append('{')
        elif char == '}':
            if brace_stack:
                brace_stack.pop()
                if not brace_stack and start_index is not None:
                    block = cleaned_text[start_index:i+1]
                    try:
                        json_obj = json.loads(block)
                        json_objects.append(json_obj)
                    except json.JSONDecodeError:
                        pass  # skip invalid JSON
                    start_index = None

    return json_objects


# ────────────────────────────────────────────────
# Analysis Functions for each Criterion
# ────────────────────────────────────────────────

def analyze_style(text: str, api_key: str, model: str):
    prompt = """Analyze this text for Microsoft Style Guide compliance:
1. Check for passive voice
2. Identify complex jargon
3. Evaluate sentence length
4. Assess action-oriented language
Return findings in JSON format
Only return necessary changes"""

    return query_openrouter(prompt, text, api_key, model)


def analyze_readability(text: str, api_key: str, model: str):
    score = textstat.flesch_kincaid_grade(text)
    prompt = f"""Analyze this documentation for readability for a **non-technical marketer**.
The Flesch-Kincaid Grade Level is {score}.
- Identify sections that are too technical or complex
- Suggest simplifications
Return results in JSON format with:
- Overall readability comment
- Problematic sentences and simplified alternatives
Only return necessary changes
"""
    return query_openrouter(prompt, text, api_key, model)


def analyze_structure(text: str, api_key: str, model: str):
    prompt = """Assess the structure and flow of this documentation:
- Are the headings and subheadings logical and helpful?
- Are paragraphs appropriately short?
- Are bullet points or numbered lists used where appropriate?
- Is the information presented in a logical order?
Return findings and suggestions in JSON format.
Only return necessary changes"""
    return query_openrouter(prompt, text, api_key, model)


def analyze_completeness(text: str, api_key: str, model: str):
    prompt = """Check if this article provides complete and clear guidance.
- Are any steps or details missing?
- Are examples used effectively?
- Suggest where examples or clarifications should be added.
Return findings in JSON format.
Only return necessary changes"""
    return query_openrouter(prompt, text, api_key, model)
