from src.config import ROOT, normalize
from src.ingest import build_chunks, chunk_text, clean_text


def test_clean_text():
    assert clean_text("a   b\n\n\n\nc") == "a b\n\nc"


def test_chunk_size_respected_and_text_covered():
    text = " ".join(f"mot{i}" for i in range(300))
    chunks = chunk_text(text, 200, 40)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for _, c in chunks)
    assert chunks[0][1].startswith("mot0") and chunks[-1][1].endswith("mot299")


def test_chunk_overlap_must_be_smaller_than_size():
    import pytest

    with pytest.raises(ValueError):
        chunk_text("abc", 50, 50)


def test_build_chunks_adds_metadata():
    chunks = build_chunks(ROOT / "data" / "raw", 400, 60)
    assert chunks
    for c in chunks:
        assert {"chunk_id", "source", "section", "chunk_index", "text"} <= c.keys()
        assert c["source"].endswith(".md")
    assert len({c["chunk_id"] for c in chunks}) == len(chunks)


def test_smaller_chunks_give_more_chunks():
    small = build_chunks(ROOT / "data" / "raw", 150, 20)
    large = build_chunks(ROOT / "data" / "raw", 800, 20)
    assert len(small) > len(large)


def test_normalize_handles_accents_and_nbsp():
    assert normalize("80\u202f% À la LIVRAISON") == "80 % a la livraison"


def test_chunks_never_start_in_the_middle_of_a_word():
    text = " ".join(f"mot{i}" for i in range(200))
    words = set(text.split())
    for _, chunk in chunk_text(text, 120, 40)[1:]:
        assert chunk.split()[0] in words


def test_section_strategy_keeps_each_fact_with_its_title():
    chunks = build_chunks(ROOT / "data" / "raw", 400, 60, "section")
    target = [c for c in chunks if c["section"] == "Colis non reçu"]
    assert len(target) == 1
    assert "10 jours" in target[0]["text"] and "Colis non reçu" in target[0]["text"]


def test_section_chunks_start_with_a_title_not_a_fragment():
    for c in build_chunks(ROOT / "data" / "raw", 400, 60, "section"):
        assert c["text"][0].isupper() or c["text"][0] == "#"


def test_fixed_strategy_still_available():
    fixed = build_chunks(ROOT / "data" / "raw", 400, 60, "fixed")
    section = build_chunks(ROOT / "data" / "raw", 400, 60, "section")
    assert fixed and section and fixed != section
