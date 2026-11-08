"""The freeze manifest of scripts/run_confirmatory.py (PREREG section 10)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_confirmatory as rc  # noqa: E402


def test_hash_ignores_crlf_and_bom(tmp_path):
    a, b, c = tmp_path / "a.txt", tmp_path / "b.txt", tmp_path / "c.txt"
    a.write_bytes(b"x = 1\ny = 2\n")
    b.write_bytes(b"\xef\xbb\xbfx = 1\r\ny = 2\r\n")
    c.write_bytes(b"x = 1\ny = 3\n")
    assert rc.sha256_lf(a) == rc.sha256_lf(b) != rc.sha256_lf(c)


def test_this_script_hashes_with_its_manifest_value_blanked(tmp_path, monkeypatch):
    src = Path(rc.__file__).read_bytes()
    assert b'MANIFEST_SHA256 = ""' in src
    filled = tmp_path / "run_confirmatory.py"
    filled.write_bytes(src.replace(b'MANIFEST_SHA256 = ""', b'MANIFEST_SHA256 = "abc123"', 1))
    monkeypatch.setattr(rc, "__file__", str(filled))
    h_filled = rc.sha256_lf(filled)
    blank = tmp_path / "blank.py"
    blank.write_bytes(src)
    assert h_filled == rc.sha256_lf(blank)


def test_every_frozen_file_exists_or_is_produced_before_the_freeze():
    produced = {"results/dev_best_configs.json", "results/mde.json", "results/worlds_check.json",
                "requirements-lock.txt", ".gitattributes"} | {
        f"results/verdicts_worlds_{w}.json" for w in ("KS0", "DA", "FW", "FLAT")}
    missing = [f for f in rc.FROZEN if not (ROOT / f).exists() and f not in produced]
    assert missing == []


def test_unfrozen_run_is_refused(monkeypatch):
    monkeypatch.setattr(rc, "MANIFEST_SHA256", "")
    try:
        rc.check_freeze()
    except SystemExit as e:
        assert "not frozen" in str(e)
    else:
        raise AssertionError("an unfrozen confirmatory run must be refused")


def test_scoring_and_fitting_code_is_frozen():
    for f in ("scripts/analyse.py", "src/p3a/study.py", "src/p3a/models.py", "scripts/run_confirmatory.py",
              "data/raw/dataset/isotherms.csv", "requirements-lock.txt", "results/mde.json"):
        assert f in rc.FROZEN
