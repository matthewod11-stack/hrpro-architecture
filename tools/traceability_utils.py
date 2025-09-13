#!/usr/bin/env python3
"""Utility helpers for traceability scripts.

Provides spec autodiscovery, Markdown section loading and reference parsing.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Tuple, Optional

__all__ = [
    "discover_spec_files",
    "load_md_sections",
    "parse_ref_number",
]

# Regular expressions reused across scripts
_VERSION_RE = re.compile(r"v(\d+(?:\.\d+)*)", re.IGNORECASE)
_SECTION_RE = re.compile(r"^\s*#{1,6}\s+((\d+)(?:\.\d+)*)\s+(.+?)\s*$")
_REF_RE = re.compile(r"§\s*([\d]+(?:\.[\d]+)*)")


def _version_key(path: Path) -> Tuple[int, ...]:
    """Return a tuple version key for sorting file versions."""
    m = _VERSION_RE.search(path.name)
    if not m:
        return tuple()
    return tuple(int(x) for x in m.group(1).split("."))


def discover_spec_file(base: Path, prefix: str) -> Optional[Path]:
    """Discover the latest spec file in ``base`` matching ``prefix``.

    Parameters
    ----------
    base: Path
        Directory to search.
    prefix: str
        Expected filename prefix, e.g. ``"PRD_"``.
    """
    candidates = sorted(
        [p for p in base.glob(f"{prefix}*.md") if p.is_file()],
        key=_version_key,
        reverse=True,
    )
    return candidates[0] if candidates else None


def discover_spec_files(repo_root: Path) -> Dict[str, Optional[Path]]:
    """Discover PRD, Architecture and UI spec markdown files.

    Searches under ``docs/PRD``, ``docs/Architecture`` and ``docs/UI_Framework``.
    If the UI spec is not found in ``docs/UI_Framework`` a fallback search under
    ``docs`` is performed.
    """
    docs = repo_root / "docs"
    prd = discover_spec_file(docs / "PRD", "PRD_v")
    arch = discover_spec_file(docs / "Architecture", "Architecture_v")
    ui_dir = docs / "UI_Framework"
    ui = discover_spec_file(ui_dir, "UIFramework_v")
    if ui is None:
        # Fallback: search anywhere under docs for a UI spec
        ui = next((p for p in docs.rglob("UIFramework_v*.md")), None)
    return {"prd": prd, "arch": arch, "ui": ui}


def load_md_sections(md_path: Optional[Path]):
    """Read a Markdown file and return (sections_set, titles_dict).

    ``sections_set`` contains all numbered section identifiers, while
    ``titles_dict`` maps section numbers to their titles.
    """
    sections, titles = set(), {}
    if not md_path or not md_path.exists():
        return sections, titles
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        m = _SECTION_RE.match(line)
        if m:
            num = m.group(1).strip()
            title = m.group(3).strip()
            sections.add(num)
            titles[num] = title
    return sections, titles


def parse_ref_number(cell: str) -> Optional[str]:
    """Extract ``§X[.Y]`` section number from a reference cell."""
    if not isinstance(cell, str):
        return None
    m = _REF_RE.search(cell)
    return m.group(1) if m else None
