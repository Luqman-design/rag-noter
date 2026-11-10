import pytest 
from ingest import chunk_text

def test_overlap_too_big_raises_error():
    with pytest.raises(ValueError):
        chunk_text("samme størrelse", size=100, overlap=100)

def test_empty_text_gives_no_chunks():
    assert chunk_text("") == []

def test_short_text_gives_one_chunk():
    assert chunk_text("hej", size=100, overlap=10) == ["hej"]

def test_overlap_works():
    result = chunk_text("abcdefghij", size=4, overlap=2)
    assert result == ["abcd", "cdef", "efgh", "ghij", "ij"]