import chromadb


col = chromadb.PersistentClient(path="./chroma").get_or_create_collection("plantas")

EVAL = [
    ("what plants are good for shade?", "shade"),
    ("how much light does a plant in low light need?", "newspaper"),
    ("what is the common name of Sansevieria?", "Mother-in-Law"),
    ("which plants like bright light?", "bright"),
    ]

def eval_calculator():
    hit = 0
    total = len(EVAL)
    for question, keyword in EVAL:
        res = col.query(query_texts=[question], n_results=8)
        print(f"\nQuestion: {question}\nKeyword: {keyword}\n")
        chunks = res["documents"][0]

        if any(keyword.lower() in chunk.lower() for chunk in chunks):
            print("HIT")
            hit += 1
        else:
            print("MISS")

    print(f"\nEvaluation Results: {hit}/{total} hits")

if __name__ == "__main__":
    eval_calculator()
