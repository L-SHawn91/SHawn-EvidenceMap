import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "public_safety_scan.py"


def run_scan(path: Path):
    return subprocess.run([sys.executable, str(SCRIPT), str(path)], text=True, capture_output=True)


def test_public_safety_scan_accepts_safe_public_tree(tmp_path):
    (tmp_path / "README.md").write_text("Public scholarly metadata and toy examples only.\n")
    result = run_scan(tmp_path)
    assert result.returncode == 0
    assert "PUBLIC_SAFETY_OK" in result.stdout


def test_public_safety_scan_rejects_secret_like_assignment(tmp_path):
    secret_name = "api" + "_key"
    secret_value = "A" * 24
    (tmp_path / "bad.txt").write_text(f"{secret_name} = '{secret_value}'\n")
    result = run_scan(tmp_path)
    assert result.returncode == 1
    assert "PUBLIC_SAFETY_FAIL" in result.stdout


def test_public_safety_scan_rejects_personal_gmail_contact(tmp_path):
    address = "personal" + "@gmail.com"
    (tmp_path / "landing.html").write_text(f"Contact: {address}\n")
    result = run_scan(tmp_path)
    assert result.returncode == 1
    assert "PUBLIC_SAFETY_FAIL" in result.stdout
