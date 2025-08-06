import os

import faiss
import numpy as np
import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from utils.db import DataBaseManagement

load_dotenv()

PROXY_URL = os.getenv("CF_WORKER_URL")

embedder = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384
index = faiss.IndexFlatL2(dimension)
documents = []


def load_and_index_emails():
    """Load all email bodies from MariaDB and index them in FAISS."""
    db = DataBaseManagement()
    all_emails = db.get_all_sent_emails()
    email_bodies = [email[3] for email in all_emails]
    if email_bodies:
        add_documents(email_bodies)


def add_documents(texts):
    global documents
    embeddings = embedder.encode(texts)
    index.add(np.array(embeddings, dtype=np.float32))
    documents.extend(texts)


def search(query, k=3):
    if len(documents) == 0 or index.ntotal == 0:
        return []
    q_emb = embedder.encode([query])
    D, I = index.search(np.array(q_emb, dtype=np.float32), min(k, index.ntotal))
    return [documents[i] for i in I[0] if i < len(documents)]

def call_gemini(prompt, context=""):
    payload = {
        "contents": [
            {
                "parts": [
                    { "text": f"Context:\n{context}\n\nUser Request:\n{prompt}" }
                ]
            }
        ]
    }
    try:
        response = requests.post(PROXY_URL, json=payload, timeout=30)
        print("Worker raw response:", response.text)
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                return data["response"]
            elif "candidates" in data:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return f"❌ Unexpected Worker Response: {data}"
        return f"❌ Worker Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"❌ Request Failed: {e}"


def generate_email_with_rag(user_prompt, title, tone="formal"):
    context_docs = search(user_prompt)
    context = "\n".join(context_docs) if context_docs else "No relevant past data."
    tone_instruction = "- Use a formal and professional tone." if tone == "formal" else "- Use a casual and friendly tone."
    enhanced_prompt = (
        f"You are an email assistant. Rewrite and improve the user's draft as an email.\n\n"
        f"### Context (related past emails):\n{context}\n\n"
        f"### User Draft:\n{user_prompt}\n\n"
        f"### Instructions:\n"
        f"{tone_instruction}\n"
        f"- Use natural email formatting.\n"
        f"- Suggest a good subject line.\n"
        f"- Provide only the improved email.\n\n"
        f"Now write the final email:"
        f"Remember sender name is Mahdi Ghasemi"
        f"Remember recivers name = name"
        f"Remember senders title = title"
    )
    return call_gemini(enhanced_prompt, context)
