# -*- coding: utf-8 -*-
"""IJEHR 投稿制限の検証スクリプト。"""

import re
from pathlib import Path

from docx import Document

ROOT = Path(__file__).parent
qmd = (ROOT / "Manuscript_IJEHR.qmd").read_text(encoding="utf-8")


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9'-]+", text))


abs_match = re.search(r"# Abstract\n\n(.*?)\n\n\*\*Keywords", qmd, re.S)
abstract = abs_match.group(1).strip()
intro = qmd.find("# Introduction")
ack = qmd.find("# Acknowledgements")
main = qmd[intro:ack]

print("=== IJEHR Limit Check ===")
print(f"Abstract words: {count_words(abstract)} (limit: 200)")
print(f"Main text words (Intro-Conclusions): {count_words(main)} (limit: 3500)")

kw = re.search(r"\*\*Keywords:\*\* (.+)", qmd).group(1)
kws = [k.strip() for k in kw.split(";")]
print(f"Keywords: {len(kws)} -> {kws} (limit: 3-5)")

tables = len(re.findall(r"^## Table ", qmd, re.M))
figs = len(re.findall(r"^## Fig\. ", qmd, re.M))
print(f"Main tables+figures: {tables}+{figs}={tables+figs} (limit: 6)")

cite_keys = set(re.findall(r"@([a-zA-Z0-9_-]+)", qmd))
print(f"References (unique cite keys): {len(cite_keys)} (limit: 35)")

jp_qmd = len(re.findall(r"[\u3040-\u30ff\u4e00-\u9fff]", qmd))
print(f"Japanese chars in qmd: {jp_qmd}")

doc_path = ROOT / "submission_package_IJEHR" / "Manuscript_IJEHR_20260628.docx"
if doc_path.exists():
    doc = Document(doc_path)
    text = "\n".join(p.text for p in doc.paragraphs)
    jp_doc = len(re.findall(r"[\u3040-\u30ff\u4e00-\u9fff]", text))
    print(f"Japanese chars in manuscript docx: {jp_doc}")

print("=== Done ===")
