"""Stil et spørgsmål til dine dokumenter fra terminalen.

Kør:  python ask.py "Hvad er en B-tree?"
      python ask.py --retrieve-only "Hvad er en B-tree?"   (vis kun de fundne chunks, ingen LLM)
"""
import os
import sys

import chromadb

DB_DIR = "chroma_db"
COLLECTION = "noter"
MODEL = os.environ.get("RAG_MODEL", "llama3.2")
TOP_K = 4

PROMPT = """Du er en hjælpsom studieassistent. Svar på spørgsmålet KUN ud fra konteksten nedenfor.
Hvis svaret ikke står i konteksten, så sig det ærligt. Henvis til kilderne i [firkantede parenteser].

Kontekst:
{context}

Spørgsmål: {question}
Svar:"""


def retrieve(question: str, k: int = TOP_K) -> list[tuple[str, dict]]:
    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_collection(COLLECTION)
    res = collection.query(query_texts=[question], n_results=k)
    return list(zip(res["documents"][0], res["metadatas"][0]))


def answer(question: str) -> tuple[str, list[tuple[str, dict]]]:
    import ollama  # importeres her, så --retrieve-only virker uden Ollama

    hits = retrieve(question)
    context = "\n\n".join(f"[{m['source']}, side {m['page']}]\n{doc}" for doc, m in hits)
    resp = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT.format(context=context, question=question)}],
    )
    return resp["message"]["content"], hits


def main() -> None:
    args = sys.argv[1:]
    retrieve_only = "--retrieve-only" in args
    args = [a for a in args if a != "--retrieve-only"]
    if not args:
        print(__doc__)
        sys.exit(1)
    question = " ".join(args)

    if retrieve_only:
        for doc, m in retrieve(question):
            print(f"--- {m['source']}, side {m['page']} ---\n{doc[:300]}...\n")
        return

    text, hits = answer(question)
    print(text)
    print("\nKilder:")
    for _, m in hits:
        print(f"  - {m['source']}, side {m['page']}")


if __name__ == "__main__":
    main()