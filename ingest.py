"""Læser PDF'er fra data/, deler dem i chunks og gemmer dem i ChromaDB.

Kør:  python ingest.py
"""
import sys
from pathlib import Path

import chromadb
from pypdf import PdfReader

DATA_DIR = Path("data")
DB_DIR = "chroma_db"
COLLECTION = "noter"

# Chunk-størrelse i tegn. Prøv at skrue på dem og se, hvordan svarene ændrer sig!
CHUNK_SIZE = 1000
OVERLAP = 200


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """Del tekst i overlappende bidder, så en sætning ikke bliver klippet over uden kontekst."""
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size])
        start += size - overlap
    return chunks


def main() -> None:
    pdfs = sorted(DATA_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"Ingen PDF'er fundet i {DATA_DIR}/ - læg nogle filer derind først.")
        sys.exit(1)

    client = chromadb.PersistentClient(path=DB_DIR)

    # Start forfra hver gang, så gamle chunks ikke hænger ved.
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION)

    total = 0
    for pdf in pdfs:
        reader = PdfReader(pdf)
        for page_no, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if not text:
                continue  # fx scannede sider uden tekstlag
            chunks = chunk_text(text)
            collection.add(
                ids=[f"{pdf.name}-p{page_no}-c{i}" for i in range(len(chunks))],
                documents=chunks,
                metadatas=[{"source": pdf.name, "page": page_no}] * len(chunks),
            )
            total += len(chunks)
        print(f"  {pdf.name}: {len(reader.pages)} sider")

    print(f"Færdig: {total} chunks gemt i {DB_DIR}/")


if __name__ == "__main__":
    main()