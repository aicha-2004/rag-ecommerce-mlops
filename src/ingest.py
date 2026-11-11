"""Phase 2 - Ingestion : nettoyage, decoupage (chunking) et metadonnees."""
import re
from pathlib import Path


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, size: int, overlap: int):
    """Decoupe `text` en morceaux de `size` caracteres au plus, avec recouvrement.

    Retourne une liste de (start, chunk). On coupe de preference sur un saut de ligne,
    sinon sur un espace.
    """
    if size <= overlap:
        raise ValueError("chunk_size doit etre superieur a chunk_overlap")
    chunks, start, n = [], 0, len(text)
    while start < n:
        end = min(start + size, n)
        if end < n:
            cut = text.rfind("\n", start + size // 2, end)
            if cut == -1:
                cut = text.rfind(" ", start + size // 2, end)
            if cut != -1:
                end = cut
        piece = text[start:end].strip()
        if piece:
            chunks.append((start, piece))
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks


def _heading_before(text: str, pos: int) -> str:
    """Dernier titre Markdown (# ou ##) situe avant la position `pos`."""
    heading = ""
    for m in re.finditer(r"^#{1,3}\s+(.+)$", text[: pos + 1], flags=re.MULTILINE):
        heading = m.group(1).strip()
    return heading


def build_chunks(raw_dir, size: int, overlap: int):
    """Lit tous les .md de `raw_dir` et retourne les chunks avec leurs metadonnees."""
    out = []
    for path in sorted(Path(raw_dir).glob("*.md")):
        text = clean_text(path.read_text(encoding="utf-8"))
        for i, (start, piece) in enumerate(chunk_text(text, size, overlap)):
            out.append({
                "chunk_id": f"{path.name}#{i}",
                "source": path.name,
                "section": _heading_before(text, start),
                "chunk_index": i,
                "text": piece,
            })
    return out
