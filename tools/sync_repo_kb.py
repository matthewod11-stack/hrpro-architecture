#!/usr/bin/env python
from fnmatch import fnmatch
import pathlib
import re
import shutil
import subprocess
import sys

import yaml

CFG = "knowledge_base/external_kb.yaml"
WORK = pathlib.Path(".kb_sync")


def run(cmd, **kw):
    subprocess.check_call(cmd, **kw)


def is_excluded(path, patterns):
    sp = str(path)
    return any(fnmatch(sp, pat) for pat in patterns)


def ensure_anchor(md_path, prefix):
    txt = md_path.read_text(encoding="utf-8", errors="ignore")
    lines = txt.splitlines()
    if lines and prefix in lines[0]:
        return False
    slug = re.sub(r"[^a-z0-9\-]+", "-", md_path.stem.lower())
    header = f"<!-- {prefix}.{slug} -->\n"
    txt = header + txt
    # Normalize naked § refs: §1.2 -> §<prefix>.1.2
    txt = re.sub(
        r"(?<![a-z0-9\-])§(\d+(\.\d+)*)", rf"§{prefix}.\1", txt, flags=re.IGNORECASE
    )
    md_path.write_text(txt, encoding="utf-8")
    return True


def convert_or_copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    ext = src.suffix.lower()
    if ext in [".pdf", ".docx"]:
        md_out = dst.with_suffix(".md")
        try:
            run(["python", "tools/mdconvert.py", str(src), "--output", str(md_out)])
        except Exception:
            md_out.write_text(
                f"# TODO: convert {src.name}\n\n> Conversion tool missing. Source: `{src}`\n",
                encoding="utf-8",
            )
        return md_out
    else:
        shutil.copy2(src, dst)
        return dst


def main():
    cfg = yaml.safe_load(open(CFG))
    WORK.mkdir(exist_ok=True)
    total_synced = total_converted = total_anchored = 0
    for repo in cfg.get("repos", []):
        rid = repo["id"]
        url = repo["url"]
        br = repo.get("branch", "main")
        dest = pathlib.Path(repo["dest"])
        incl = repo.get("include", ["**/*.md"])
        excl = repo.get("exclude", [])
        prefix = repo.get("anchor_prefix", f"§{rid}")

        tmp = WORK / rid
        if tmp.exists():
            shutil.rmtree(tmp)
        run(["git", "clone", "--depth", "1", "--branch", br, url, str(tmp)])

        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True, exist_ok=True)

        # gather files
        files = []
        for pattern in incl:
            files.extend(
                [
                    p
                    for p in tmp.rglob("*")
                    if p.is_file()
                    and fnmatch(str(p), pattern)
                    and not is_excluded(p, excl)
                ]
            )

        for f in files:
            rel = f.relative_to(tmp)
            out = dest / rel
            md_path = convert_or_copy(f, out)
            total_synced += 1
            if md_path.suffix.lower() == ".md" and md_path != out:
                total_converted += 1
            if md_path.suffix.lower() == ".md":
                if ensure_anchor(md_path, prefix):
                    total_anchored += 1

    print(
        f"OK: synced={total_synced}, converted={total_converted}, anchors_added={total_anchored}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
