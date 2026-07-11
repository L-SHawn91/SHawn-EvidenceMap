#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap

from PIL import Image, ImageDraw, ImageFont

from evidencemap.refdb import ReferenceStore
from evidencemap.refdb.interchange import export_bibtex, export_csv, export_ris, parse_csv


REPO_URL = "https://github.com/L-SHawn91/SHawn-EvidenceMap"
PILOT_URL = f"{REPO_URL}/discussions/9"
BG = "#f8fafc"
INK = "#18202a"
MUTED = "#5d6978"
TEAL = "#0f766e"
PURPLE = "#7c3aed"
LINE = "#d9e0e8"
WHITE = "#ffffff"


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu") / name,
        Path("/usr/share/fonts/dejavu") / name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    raise RuntimeError("DejaVu Sans is required to build the pilot demo")


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int], *, size: int, fill: str = INK, bold: bool = False, spacing: int = 10) -> int:
    x1, y1, x2, _ = box
    fnt = font(size, bold=bold)
    average = max(1, int((x2 - x1) / (size * 0.58)))
    lines: list[str] = []
    for paragraph in text.splitlines():
        lines.extend(textwrap.wrap(paragraph, width=average, replace_whitespace=False) or [""])
    y = y1
    for line in lines:
        draw.text((x1, y), line, font=fnt, fill=fill)
        y += size + spacing
    return y


def base_frame(step: str, title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (1280, 720), BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((44, 36, 1236, 684), radius=22, fill=WHITE, outline=LINE, width=2)
    draw.text((80, 70), step.upper(), font=font(22, bold=True), fill=TEAL)
    draw.text((80, 112), title, font=font(47, bold=True), fill=INK)
    draw.text((80, 638), "SHawn EvidenceMap · Verifiable Metadata Bridge", font=font(20, bold=True), fill=TEAL)
    draw.text((807, 641), "Public metadata · local-first · no hosted upload", font=font(16), fill=MUTED)
    return image, draw


def make_frames(summary: dict[str, int], entities: list[dict], output_dir: Path) -> list[Path]:
    frame_dir = output_dir / "demo-frames"
    shutil.rmtree(frame_dir, ignore_errors=True)
    frame_dir.mkdir(parents=True)
    frames: list[Path] = []

    image, draw = base_frame("01 / 06", "A 60-second executable walkthrough")
    draw_wrapped(draw, "Turn a messy DOI and PMID spreadsheet into an auditable research handoff.", (80, 205, 1110, 400), size=36, fill=MUTED)
    draw.rounded_rectangle((80, 410, 1190, 560), radius=16, fill="#ecfdf5")
    draw_wrapped(draw, "Normalize → detect collisions → preserve provenance → export CSV / RIS / BibTeX / JSON", (115, 447, 1150, 545), size=28, fill=TEAL, bold=True)
    frames.append(save_frame(image, frame_dir, 1))

    image, draw = base_frame("02 / 06", "BEFORE · six inconsistent input rows")
    draw_wrapped(draw, "• DOI URL with uppercase characters\n• PMID for the same paper on another row\n• Repeated DOI using a doi: prefix\n• One deliberate cross-entity identifier collision\n• One public dataset accession", (95, 205, 1160, 555), size=29, fill=INK, spacing=17)
    frames.append(save_frame(image, frame_dir, 2))

    image, draw = base_frame("03 / 06", "RUN · the same public CLI users install")
    draw.rounded_rectangle((80, 205, 1200, 555), radius=16, fill="#111827")
    command = (
        "$ python -m evidencemap.refdb ingest --db bridge.sqlite3 \\\n"
        "    --input dirty_records.csv --format csv\n\n"
        "$ python -m evidencemap.refdb verify --db bridge.sqlite3\n\n"
        "$ python -m evidencemap.refdb export --db bridge.sqlite3 \\\n"
        "    --out records.ris --format ris"
    )
    draw_wrapped(draw, command, (115, 245, 1160, 530), size=25, fill="#d1fae5", spacing=12)
    frames.append(save_frame(image, frame_dir, 3))

    image, draw = base_frame("04 / 06", "AUDIT · every input receives a decision")
    labels = [("Inserted", summary["inserted"], TEAL), ("Merged", summary["merged"], PURPLE), ("Rejected", summary["rejected"], "#b45309")]
    for index, (label, value, color) in enumerate(labels):
        x1 = 80 + index * 375
        draw.rounded_rectangle((x1, 220, x1 + 330, 470), radius=18, fill="#f8fafc", outline=LINE, width=2)
        draw.text((x1 + 30, 258), label, font=font(26, bold=True), fill=color)
        draw.text((x1 + 30, 320), str(value), font=font(84, bold=True), fill=INK)
        draw.text((x1 + 30, 425), "input row(s)", font=font(20), fill=MUTED)
    draw_wrapped(draw, "The collision is rejected instead of being silently merged.", (80, 515, 1150, 590), size=25, fill=MUTED, bold=True)
    frames.append(save_frame(image, frame_dir, 4))

    image, draw = base_frame("05 / 06", "AFTER · deterministic, tool-ready handoffs")
    identifiers = []
    for entity in entities:
        for key, value in sorted(entity.get("identifiers", {}).items()):
            identifiers.append(f"{key}: {value}")
    preview = "\n".join(f"✓ {item}" for item in identifiers[:6])
    draw_wrapped(draw, preview, (95, 205, 760, 560), size=27, fill=INK, spacing=15)
    draw.rounded_rectangle((810, 220, 1175, 525), radius=18, fill="#f5f3ff")
    draw_wrapped(draw, "SQLite\nAudit JSON\nCSV\nRIS\nBibTeX", (865, 255, 1135, 500), size=30, fill=PURPLE, bold=True, spacing=15)
    frames.append(save_frame(image, frame_dir, 5))

    image, draw = base_frame("06 / 06", "Try the free CLI—or request a bounded pilot")
    draw_wrapped(draw, "Free Apache-2.0 core", (80, 210, 600, 270), size=31, fill=TEAL, bold=True)
    draw_wrapped(draw, "Use your own public DOI, PMID, OpenAlex, accession, CSV, RIS, or BibTeX records locally.", (80, 270, 600, 470), size=25, fill=MUTED)
    draw_wrapped(draw, "Metadata Audit Pilot", (670, 210, 1160, 270), size=31, fill=PURPLE, bold=True)
    draw_wrapped(draw, "Hands-on cleanup, provenance review, reproducible exports, and workflow handoff. No private PDFs, patient data, or hosted upload.", (670, 270, 1160, 495), size=25, fill=MUTED)
    draw.rounded_rectangle((80, 520, 1170, 590), radius=14, fill="#ecfdf5")
    draw.text((112, 541), PILOT_URL, font=font(22, bold=True), fill=TEAL)
    frames.append(save_frame(image, frame_dir, 6))
    return frames


def save_frame(image: Image.Image, frame_dir: Path, number: int) -> Path:
    path = frame_dir / f"frame-{number:02d}.png"
    image.save(path, optimize=True)
    return path


def render_video(frames: list[Path], output_path: Path) -> None:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required to build the 60-second MP4")
    with tempfile.TemporaryDirectory() as tmp:
        concat = Path(tmp) / "frames.txt"
        lines: list[str] = []
        for frame in frames:
            lines.extend([f"file '{frame.resolve()}'", "duration 10"])
        lines.append(f"file '{frames[-1].resolve()}'")
        concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                "-i", str(concat), "-vf", "fps=24,format=yuv420p", "-c:v", "libx264",
                "-movflags", "+faststart", str(output_path),
            ],
            check=True,
        )


def build(repo: Path) -> dict[str, object]:
    input_path = repo / "examples/pilot/dirty_records.csv"
    output_dir = repo / "web/assets"
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = output_dir / "pilot-demo.sqlite3"
    db_path.unlink(missing_ok=True)
    records = parse_csv(input_path.read_text(encoding="utf-8"))
    with ReferenceStore(db_path) as store:
        summary = store.ingest_records(
            records,
            run_id="pilot-demo-v1",
            source="public_pilot_demo",
            started_at="2026-07-12T00:00:00Z",
            finished_at="2026-07-12T00:00:01Z",
        )
        issues = store.verify()
        if issues:
            raise RuntimeError(f"pilot demo verification failed: {issues}")
        payload_text = store.export_json()
    payload = json.loads(payload_text)
    entities = payload["entities"]
    (output_dir / "pilot-demo.json").write_text(payload_text, encoding="utf-8")
    (output_dir / "pilot-demo.csv").write_text(export_csv(entities), encoding="utf-8")
    (output_dir / "pilot-demo.ris").write_text(export_ris(entities), encoding="utf-8")
    (output_dir / "pilot-demo.bib").write_text(export_bibtex(entities), encoding="utf-8")
    result = {
        "input_records": len(records),
        "summary": summary,
        "entity_count": payload["counts"]["entities"],
        "verification": "pass",
        "boundary": "One public metadata record plus explicit synthetic records; no registry resolution is claimed.",
    }
    (output_dir / "pilot-demo-summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    frames = make_frames(summary, entities, output_dir)
    shutil.copy2(frames[0], output_dir / "pilot-demo-poster.png")
    render_video(frames, output_dir / "pilot-demo-60s.mp4")
    shutil.rmtree(output_dir / "demo-frames")
    db_path.unlink()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the executable 60-second Metadata Bridge pilot demo")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = build(args.repo.resolve())
    print("PILOT_DEMO_OK " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
