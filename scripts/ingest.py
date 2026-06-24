"""Loads the plant docs into Chroma. Run once: python scripts/ingest.py"""
import pathlib, chromadb
from pypdf import PdfReader

DOCS_DIR = pathlib.Path("docs")
CHUNK, OVERLAP = 1000, 200

def read_text(f: pathlib.Path) -> str:
    if f.suffix == ".pdf":
        return "\n".join(p.extract_text() or "" for p in PdfReader(f).pages)
    return f.read_text(encoding="utf-8")

def chunks(text):
    step = CHUNK - OVERLAP
    return [text[i:i + CHUNK] for i in range(0, len(text), step)]

def main():
    client = chromadb.PersistentClient(path="./chroma")
    col = client.get_or_create_collection("plantas")
    docs, ids, metas = [], [], []
    for f in DOCS_DIR.glob("*"):
        if f.suffix not in (".txt", ".md", ".pdf"):
            continue
        for n, ch in enumerate(chunks(read_text(f))):
            if ch.strip():
                docs.append(ch); ids.append(f"{f.stem}-{n}"); metas.append({"source": f.name})
    col.upsert(documents=docs, ids=ids, metadatas=metas)
    print(f"{len(docs)} chunks from {len(set(m['source'] for m in metas))} docs")

if __name__ == "__main__":
    assert chunks("abcd") and len(chunks("x" * 2500)[0]) <= CHUNK
    main()