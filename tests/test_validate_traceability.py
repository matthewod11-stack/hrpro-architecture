import csv

from tools import validate_traceability_md as vtm


def test_valid_refs_pass(tmp_path):
    prd = tmp_path / "prd.md"
    prd.write_text("# 1 Title\n## 1.1 Section A\n")
    arch = tmp_path / "arch.md"
    arch.write_text("# 1 Title\n## 1.1 Section B\n")
    ui = tmp_path / "ui.md"
    ui.write_text("# 1 Title\n## 1.1 Section C\n")

    trace = tmp_path / "trace.xlsx"
    vtm._write_test_xlsx(
        trace, [{"PRD Ref": "§1.1", "Arch Ref": "§1.1", "UI Ref": "§1.1"}]
    )

    out = tmp_path / "out.csv"
    code = vtm.main(
        [
            "--prd",
            str(prd),
            "--arch",
            str(arch),
            "--ui",
            str(ui),
            "--trace",
            str(trace),
            "--out",
            str(out),
        ]
    )
    assert code == 0
    rows = list(csv.DictReader(open(out)))
    assert rows[0]["PRD Status"] == "OK"


def test_missing_ref_fails(tmp_path):
    prd = tmp_path / "prd.md"
    prd.write_text("# 1 Title\n## 1.1 Section A\n")
    arch = tmp_path / "arch.md"
    arch.write_text("# 1 Title\n")
    ui = tmp_path / "ui.md"
    ui.write_text("# 1 Title\n")

    trace = tmp_path / "trace.xlsx"
    vtm._write_test_xlsx(
        trace, [{"PRD Ref": "§1.1", "Arch Ref": "§1.2", "UI Ref": "§9.9"}]
    )

    out = tmp_path / "out.csv"
    code = vtm.main(
        [
            "--prd",
            str(prd),
            "--arch",
            str(arch),
            "--ui",
            str(ui),
            "--trace",
            str(trace),
            "--out",
            str(out),
        ]
    )
    assert code == 1
    rows = list(csv.DictReader(open(out)))
    assert rows[0]["Arch Status"] == "MISSING"
    assert rows[0]["UI Status"] == "MISSING"
