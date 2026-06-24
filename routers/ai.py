import chromadb
from fastapi import APIRouter
from pydantic import BaseModel
from groq import Groq
from ..config import settings

router = APIRouter()
col = chromadb.PersistentClient(path="./chroma").get_or_create_collection("plantas")
groq = Groq(api_key=settings.settings.GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"   # check current list at console.groq.com/docs/models

class Ask(BaseModel):
    question: str

@router.post("/ask")
def ask(body: Ask):
    hits = col.query(query_texts=[body.question], n_results=8)   # ponytail: small corpus (22 chunks), top-8 is cheap and catches "clean" chunks that fall outside top-5
    chunks, metas, dists = hits["documents"][0], hits["metadatas"][0], hits["distances"][0]

    prompt = (
        "Answer using ONLY the context below. If it's not there, say you don't know.\n\n"
        f"Context:\n{chr(10).join(chunks)}\n\nQuestion: {body.question}"
    )
    answer = groq.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

    # ponytail: confidence = distance of the best chunk. Heuristic; replace with Thursday's eval.
    confidence = round(max(0.0, 1 - dists[0]), 2)
    return {"answer": answer, "sources": list(dict.fromkeys(m["source"] for m in metas)),
            "confidence": confidence}