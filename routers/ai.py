import base64
import re
import chromadb
from fastapi import APIRouter
from pydantic import BaseModel
from groq import Groq
from ..config import settings

DEFAULT_INTERVAL_DAYS = 7
INTERVAL_PROMPT = (
    "Você é especialista em plantas. Em quantos dias, em média, esta planta deve "
    "ser regada? Responda APENAS com um número inteiro de dias, nada mais.\n"
    "Planta: {name}\nDescrição: {desc}"
)


def _parse_days(text: str | None) -> int:
    # ponytail: first integer in the reply, clamped to a sane range; fallback 7.
    m = re.search(r"\d+", text or "")
    return max(1, min(60, int(m.group()))) if m else DEFAULT_INTERVAL_DAYS

router = APIRouter()
col = chromadb.PersistentClient(path="./chroma").get_or_create_collection("plantas")
groq = Groq(api_key=settings.settings.GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"   # check current list at console.groq.com/docs/models
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"   # vision; check console.groq.com/docs/vision

class Ask(BaseModel):
    question: str

def rag_answer(question: str) -> dict:
    hits = col.query(query_texts=[question], n_results=8)   # ponytail: small corpus (22 chunks), top-8 is cheap and catches "clean" chunks that fall outside top-5
    chunks, metas, dists = hits["documents"][0], hits["metadatas"][0], hits["distances"][0]

    prompt = (
        "Answer using ONLY the context below. If it's not there, say you don't know.\n\n"
        f"Context:\n{chr(10).join(chunks)}\n\nQuestion: {question}"
    )
    answer = groq.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

    # ponytail: confidence = distance of the best chunk. Heuristic; replace with Thursday's eval.
    confidence = round(max(0.0, 1 - dists[0]), 2)
    return {"answer": answer, "sources": list(dict.fromkeys(m["source"] for m in metas)),
            "confidence": confidence}

def vision_answer(image_bytes: bytes, mime: str, question: str | None) -> str:
    # ponytail: inline base64 data URL, no signed-url round trip. Groq caps base64 at ~4MB; switch to a signed Supabase URL if photos get bigger.
    b64 = base64.b64encode(image_bytes).decode()
    text = question or "Analise esta foto de planta: identifique a planta se possível, aponte problemas de saúde e dê dicas de cuidado. Responda em português."
    resp = groq.chat.completions.create(
        model=VISION_MODEL,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
        ]}],
    )
    return resp.choices[0].message.content

def suggest_interval_text(name: str, description: str | None) -> int:
    try:
        prompt = INTERVAL_PROMPT.format(name=name, desc=description or "—")
        out = groq.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content
        return _parse_days(out)
    except Exception:
        return DEFAULT_INTERVAL_DAYS


def suggest_interval_vision(image_bytes: bytes, mime: str, name: str, description: str | None) -> int:
    try:
        b64 = base64.b64encode(image_bytes).decode()
        prompt = INTERVAL_PROMPT.format(name=name, desc=description or "—")
        out = groq.chat.completions.create(
            model=VISION_MODEL,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            ]}],
        ).choices[0].message.content
        return _parse_days(out)
    except Exception:
        return DEFAULT_INTERVAL_DAYS


@router.post("/ask")
def ask(body: Ask):
    return rag_answer(body.question)