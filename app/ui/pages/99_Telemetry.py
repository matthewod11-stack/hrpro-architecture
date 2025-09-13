import json
from pathlib import Path

import streamlit as st

try:
    import numpy as np
except ImportError:
    np = None

st.title("Telemetry (Local)")
adv = Path("telemetry/advisor.jsonl")
exp = Path("telemetry/export.jsonl")

st.subheader("Advisor Finals (last 200)")
st.dataframe(finals[-200:])
st.subheader("Exports (last 200)")
st.dataframe(e[-200:])


def tail(p: Path, n=200):
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text().splitlines()[-n:] if x.strip()]


a = tail(adv, 500)
e = tail(exp, 200)

finals = [x for x in a if x.get("event") == "final"]
ttfa = [x["ms"] for x in a if x.get("event") == "ttfa"]


def pct(n, d):
    return 0 if d == 0 else round(100 * n / d, 1)


if not finals:
    st.info("No events yet.")
else:
    st.metric(
        "Citation Rate (last 50)",
        f"{pct(sum(1 for x in finals[-50:] if x.get('has_citations')), min(50,len(finals)))}%",
    )
    if ttfa:
        if np:
            st.metric("TTFA p50 (ms)", int(np.percentile(ttfa[-50:], 50)))
            st.metric("TTFA p95 (ms)", int(np.percentile(ttfa[-50:], 95)))
        else:
            ttfa_sorted = sorted(ttfa[-50:])
            n = len(ttfa_sorted)

            def percentile(data, perc):
                if not data:
                    return 0
                k = int(round((perc / 100) * (n - 1)))
                return data[k]

            st.metric("TTFA p50 (ms)", int(percentile(ttfa_sorted, 50)))
            st.metric("TTFA p95 (ms)", int(percentile(ttfa_sorted, 95)))
    st.subheader("Advisor Finals (last 200)")
    st.dataframe(finals[-200:])
    st.subheader("Exports (last 200)")
    st.dataframe(e[-200:])
import numpy as np

from app.services import telemetry

st.title("Telemetry (Local)")
adv = telemetry.tail("advisor", 500)
exp = telemetry.tail("export", 200)

finals = [x for x in adv if x.get("event") == "final"]
ttfas = [x["ms"] for x in adv if x.get("event") == "ttfa"]


def pct(n, d):
    return 0 if d == 0 else round(100 * n / d, 1)


has_cit = sum(1 for x in finals if x.get("has_citations"))
st.metric(
    "Citation Rate (last 50)",
    f"{pct(sum(1 for x in finals[-50:] if x.get('has_citations')), min(50,len(finals)))}%",
)
if ttfas:
    st.metric("TTFA p50 (ms)", int(np.percentile(ttfas[-50:], 50)))
    st.metric("TTFA p95 (ms)", int(np.percentile(ttfas[-50:], 95)))

st.subheader("Advisor Events")
st.dataframe(finals[-200:])

st.subheader("Export Events")
st.dataframe(exp[-200:])
