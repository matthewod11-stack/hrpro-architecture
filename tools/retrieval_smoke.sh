#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IDX="${ROOT}/versions/index"
LOG="${ROOT}/logs/dev_telemetry.jsonl"

export PYTHONPATH="${ROOT}:${PYTHONPATH:-}"
PY="${PY:-python}"

# Required/optional artifacts
REQ=(tfidf.joblib matrix.npz nn.joblib meta.json)
OPT=(faiss.index embeddings.npy)

banner() { printf "\n=== %s ===\n" "$*"; }

print_artifacts() {
  printf "\nArtifact check at: %s\n" "$IDX"
  printf "%-20s | %-6s | %-6s | %s\n" "file" "exists" "size" "notes"
  printf -- "---------------------+--------+--------+---------------------------\n"
  for f in "${REQ[@]}" "${OPT[@]}"; do
    local p="${IDX}/${f}"
    local ex="no"
    local sz="0"
    local note=""
    if [[ -f "$p" ]]; then
      ex="yes"
      sz=$(stat -f%z "$p" 2>/dev/null || stat -c%s "$p" 2>/dev/null || echo 0)
    fi
    [[ " ${OPT[*]} " == *" $f "* ]] && note="(optional)"
    printf "%-20s | %-6s | %-6s | %s\n" "$f" "$ex" "$sz" "$note"
  done
}

needs_rebuild() {
  local missing=()
  local zero=()
  for f in "${REQ[@]}"; do
    local p="${IDX}/${f}"
    if [[ ! -f "$p" ]]; then
      missing+=("$f")
    elif [[ ! -s "$p" ]]; then
      zero+=("$f")
    fi
  done

  if (( ${#missing[@]} > 0 || ${#zero[@]} > 0 )); then
    echo "missing: ${missing[*]:-none}, zero: ${zero[*]:-none}"
    return 0  # yes, needs rebuild
  fi
  return 1  # no rebuild needed
}

run_retrieval() {
  local topic="$1"
  local topk="${2:-8}"
  local start end ms
  echo "Using PYTHONPATH=${PYTHONPATH}"
  echo "Python: $(${PY} -V 2>&1 || echo unknown)"
  start=$(${PY} -c 'import time; print(int(time.time()*1000))')
  "${PY}" "${ROOT}/tools/retrieve_demo.py" --topic "$topic" --top_k "$topk" || true
  end=$(${PY} -c 'import time; print(int(time.time()*1000))')
  ms=$(( end - start ))
  mkdir -p "$(dirname "$LOG")"
  printf '{"event":"retrieval_smoke","topic":%q,"retrieved_docs_count":%d,"ms":%d}\n' "$topic" 0 "$ms" >> "$LOG"
}

main() {
  mkdir -p "$IDX"

  banner "Artifact verification (pre)"
  print_artifacts

  if needs_rebuild; then
    banner "Artifacts missing/empty → building KB + index"
    make -C "$ROOT" kb-build
    make -C "$ROOT" kb-index
    banner "Artifact verification (post-build)"
    print_artifacts

    if needs_rebuild; then
      echo "ERROR: required index artifacts still missing or zero-length after rebuild." >&2
      exit 1
    fi
  else
    echo "All required artifacts present."
  fi

  banner "Verbose retrieval smoke — canonical"
  run_retrieval "acceptance criteria" 8

  banner "Verbose retrieval smoke — external"
  run_retrieval "onboarding checklist" 8

  # quick anchor presence summary
  if [[ -f "${ROOT}/knowledge_base/anchors_index.csv" ]]; then
    banner "Anchor summary"
    {
      echo "counts:"
      echo -n "  ADR:      "; grep -c '^§ADR-' "${ROOT}/knowledge_base/anchors_index.csv" || true
      echo -n "  numbered: "; grep -c '^§[0-9]' "${ROOT}/knowledge_base/anchors_index.csv" || true
      echo -n "  external: "; grep -c '^§ext-' "${ROOT}/knowledge_base/anchors_index.csv" || true
      echo "sample:"
      sed -n '1,1p' "${ROOT}/knowledge_base/anchors_index.csv" >/dev/null 2>&1 || true
      (shuf -n 8 "${ROOT}/knowledge_base/anchors_index.csv" 2>/dev/null || head -n 8 "${ROOT}/knowledge_base/anchors_index.csv") | sed -E 's/^(.{0,120}).*$/\1.../'
    } || true
  fi

  echo -e "\nDone ✅"
}

main "$@"
