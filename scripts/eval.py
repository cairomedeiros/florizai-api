import chromadb


col = chromadb.PersistentClient(path="./chroma").get_or_create_collection("plantas")

EVAL = [
    ("what plants are good for shade?", "shade"),
    ("how much light does a plant in low light need?", "newspaper"),
    ("what is the common name of Sansevieria?", "Mother-in-Law"),
    ("which plants like bright light?", "bright"),
    ]


def first_hit_rank(chunks: list[str], keyword: str) -> int | None:
    """1-based position of the first chunk containing keyword, or None."""
    kw = keyword.lower()
    for i, chunk in enumerate(chunks, start=1):
        if kw in chunk.lower():
            return i
    return None


def eval_calculator():
    total = len(EVAL)
    hit3 = hit8 = 0
    reciprocal_sum = 0.0
    for question, keyword in EVAL:
        chunks = col.query(query_texts=[question], n_results=8)["documents"][0]
        rank = first_hit_rank(chunks, keyword)
        # ponytail: keyword-in-chunk is a cheap proxy for relevance — fine for a
        # ~60-chunk corpus. Move to graded/embedding judgments if the corpus grows.
        if rank is not None:
            hit8 += 1
            if rank <= 3:
                hit3 += 1
            reciprocal_sum += 1 / rank
        print(f"{'HIT' if rank else 'MISS':4} rank={rank}  {question}")

    print(f"\nHit@3: {hit3}/{total}   Hit@8: {hit8}/{total}   "
          f"MRR: {reciprocal_sum / total:.2f}")


def _selfcheck():
    chunks = ["nothing here", "talks about SHADE plants", "shade again"]
    assert first_hit_rank(chunks, "shade") == 2, "should find first hit at rank 2"
    assert first_hit_rank(chunks, "missing") is None, "absent keyword -> None"
    print("selfcheck ok")


if __name__ == "__main__":
    _selfcheck()
    eval_calculator()
