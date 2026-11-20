"""Phase 2 - Ingestion : nettoyage, decoupage (chunking) et metadonnees."""
import re
from pathlib import Path


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _align_to_word(text: str, pos: int) -> int:
    """Avance `pos` jusqu'au debut du mot suivant : un chunk ne commence jamais au milieu d'un mot."""
    while 0 < pos < len(text) and not text[pos - 1].isspace():
        pos += 1
    return pos


def chunk_text(text: str, size: int, overlap: int):
    """Decoupe `text` en morceaux de `size` caracteres au plus, avec recouvrement.

    Retourne une liste de (start, chunk). On coupe de preference sur un saut de ligne,
    sinon sur un espace, et le recouvrement demarre toujours au debut d'un mot.
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
        start = _align_to_word(text, max(end - overlap, start + 1))
        start = min(start, end)
    return chunks


def split_sections(text: str):
    """Decoupe un document Markdown en sections : liste de (titre, contenu avec son titre)."""
    sections, title, lines = [], "", []
    for line in text.split("\n"):
        if re.match(r"^#{1,3}\s+", line):
            if lines:
                sections.append((title, "\n".join(lines).strip()))
            title, lines = line.lstrip("#").strip(), [line]
        else:
            lines.append(line)
    if lines:
        sections.append((title, "\n".join(lines).strip()))
    return [(t, b) for t, b in sections if b]


def _heading_before(text: str, pos: int) -> str:
    """Dernier titre Markdown (# a ###) situe avant la position `pos`."""
    heading = ""
    for m in re.finditer(r"^#{1,3}\s+(.+)$", text[: pos + 1], flags=re.MULTILINE):
        heading = m.group(1).strip()
    return heading


def _fixed_chunks(name, text, size, overlap):
    return [
        {"chunk_id": f"{name}#{i}", "source": name, "section": _heading_before(text, start),
         "chunk_index": i, "text": piece}
        for i, (start, piece) in enumerate(chunk_text(text, size, overlap))
    ]


def _section_chunks(name, text, size, overlap):
    """Un chunk par section (titre du document en tete) : un fait reste avec son titre.

    Une section plus longue que `size` est decoupee avec recouvrement.
    """
    doc_title = next((t for t, _ in split_sections(text) if t), Path(name).stem)
    out = []
    for title, body in split_sections(text):
        if len(body.splitlines()) == 1 and body.startswith("#"):
            continue  # titre seul, sans contenu
        full = body if title == doc_title else f"{doc_title}\n{body}"
        parts = [full] if len(full) <= size else [p for _, p in chunk_text(full, size, overlap)]
        for part in parts:
            out.append({"chunk_id": f"{name}#{len(out)}", "source": name, "section": title,
                        "chunk_index": len(out), "text": part})
    return out


def build_chunks(raw_dir, size: int, overlap: int, strategy: str = "section"):
    """Lit tous les .md de `raw_dir`. strategy : "section" (par defaut) ou "fixed"."""
    make = _fixed_chunks if strategy == "fixed" else _section_chunks
    out = []
    for path in sorted(Path(raw_dir).glob("*.md")):
        out.extend(make(path.name, clean_text(path.read_text(encoding="utf-8")), size, overlap))
    return out
