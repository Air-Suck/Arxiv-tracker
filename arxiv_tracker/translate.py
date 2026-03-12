# -*- coding: utf-8 -*-
from typing import Dict, Any, List


def _split_text(text: str, max_len: int = 3500) -> List[str]:
    """Split long text into chunks to avoid translator request limits."""
    s = (text or "").strip()
    if not s:
        return []
    if len(s) <= max_len:
        return [s]

    chunks: List[str] = []
    current = []
    size = 0
    for para in s.split("\n"):
        p = para.strip()
        if not p:
            continue
        add_len = len(p) + (1 if current else 0)
        if size + add_len > max_len and current:
            chunks.append("\n".join(current))
            current = [p]
            size = len(p)
        else:
            current.append(p)
            size += add_len
    if current:
        chunks.append("\n".join(current))
    return chunks


def _google_translate_text(text: str, target_lang: str = "zh-CN") -> str:
    try:
        from deep_translator import GoogleTranslator
    except Exception as e:
        raise RuntimeError(
            "deep-translator is not installed. Run: pip install deep-translator"
        ) from e

    chunks = _split_text(text)
    if not chunks:
        return ""

    translator = GoogleTranslator(source="auto", target=target_lang)
    out = []
    for c in chunks:
        out.append((translator.translate(c) or "").strip())
    return "\n\n".join([x for x in out if x]).strip()


def translate_item_non_llm(
    item: Dict[str, Any],
    target_lang: str = "zh",
    fields: List[str] = None,
    provider: str = "google",
) -> Dict[str, str]:
    """
    Non-LLM translation for arXiv items.
    Returns keys compatible with existing renderers: title_zh / summary_zh / comments_zh.
    """
    if target_lang != "zh":
        raise ValueError("Only zh target language is supported in non-LLM mode right now")

    provider = (provider or "google").lower()
    if provider not in ("google", "free", "deep-translator"):
        raise ValueError(f"Unsupported non-LLM provider: {provider}")

    fields = fields or ["title", "summary"]
    out: Dict[str, str] = {}

    if "title" in fields and item.get("title"):
        out["title_zh"] = _google_translate_text(item.get("title", ""), "zh-CN")
    if "summary" in fields and item.get("summary"):
        out["summary_zh"] = _google_translate_text(item.get("summary", ""), "zh-CN")
    if "comments" in fields and item.get("comments"):
        out["comments_zh"] = _google_translate_text(item.get("comments", ""), "zh-CN")
    return out
