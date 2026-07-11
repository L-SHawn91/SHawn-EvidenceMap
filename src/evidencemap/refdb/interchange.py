from __future__ import annotations

import csv
from dataclasses import dataclass, field
import io
import re
from typing import Any, Mapping


_DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
_PMID_RE = re.compile(r"^\d+$")
_OPENALEX_RE = re.compile(r"^W\d+$", re.IGNORECASE)
_PREFIX_RE = re.compile(r"^(doi|pmid|openalex|openalex_id|accession)\s*:\s*(.+)$", re.IGNORECASE)


class InterchangeError(ValueError):
    """Raised when a conservative interchange input cannot be parsed safely."""


@dataclass(slots=True)
class InterchangeRecord:
    kind: str
    title: str = ""
    identifiers: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    input_ref: str = ""


def normalize_identifiers(identifiers: Mapping[str, str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for raw_key, raw_value in identifiers.items():
        key = str(raw_key).strip().lower()
        value = str(raw_value or "").strip()
        if not key or not value:
            continue
        if key == "openalex_id":
            key = "openalex"
        if key == "doi":
            value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)
            value = re.sub(r"^doi:\s*", "", value, flags=re.IGNORECASE).lstrip("/").lower()
            if not _DOI_RE.fullmatch(value):
                raise InterchangeError(f"invalid DOI: {raw_value}")
        elif key == "pmid":
            value = re.sub(r"^pmid:\s*", "", value, flags=re.IGNORECASE)
            if not _PMID_RE.fullmatch(value):
                raise InterchangeError(f"invalid PMID: {raw_value}")
        elif key == "openalex":
            value = re.sub(r"^https?://openalex\.org/", "", value, flags=re.IGNORECASE).upper()
            if not _OPENALEX_RE.fullmatch(value):
                raise InterchangeError(f"invalid OpenAlex work ID: {raw_value}")
        elif key == "accession":
            value = value.upper()
            if not re.fullmatch(r"[A-Z][A-Z0-9_.-]+", value):
                raise InterchangeError(f"invalid accession: {raw_value}")
        else:
            raise InterchangeError(f"unsupported identifier type: {raw_key}")
        normalized[key] = value
    return normalized


def parse_identifiers(text: str) -> list[InterchangeRecord]:
    records: list[InterchangeRecord] = []
    for line_number, raw_line in enumerate(text.lstrip("\ufeff").splitlines(), start=1):
        value = raw_line.strip()
        if not value or value.startswith("#"):
            continue
        match = _PREFIX_RE.fullmatch(value)
        if match:
            key, raw_value = match.groups()
            identifiers = normalize_identifiers({key: raw_value})
        elif _DOI_RE.fullmatch(re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)):
            identifiers = normalize_identifiers({"doi": value})
        elif _PMID_RE.fullmatch(value):
            identifiers = normalize_identifiers({"pmid": value})
        elif _OPENALEX_RE.fullmatch(re.sub(r"^https?://openalex\.org/", "", value, flags=re.IGNORECASE)):
            identifiers = normalize_identifiers({"openalex": value})
        else:
            raise InterchangeError(
                f"line {line_number}: unrecognized identifier; use explicit accession: prefix"
            )
        kind = "dataset" if set(identifiers) == {"accession"} else "paper"
        records.append(
            InterchangeRecord(
                kind=kind,
                identifiers=identifiers,
                input_ref=f"line:{line_number}",
            )
        )
    if not records:
        raise InterchangeError("identifier input contains no records")
    return records


def parse_csv(text: str) -> list[InterchangeRecord]:
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
    if reader.fieldnames is None:
        raise InterchangeError("CSV header is required")
    records: list[InterchangeRecord] = []
    for row_number, row in enumerate(reader, start=2):
        identifiers = normalize_identifiers(
            {
                "doi": row.get("doi", ""),
                "pmid": row.get("pmid", ""),
                "openalex": row.get("openalex_id", row.get("openalex", "")),
                "accession": row.get("accession", ""),
            }
        )
        if not identifiers:
            raise InterchangeError(f"CSV row {row_number}: at least one identifier is required")
        metadata: dict[str, Any] = {}
        year = (row.get("year") or "").strip()
        if year:
            if not year.isdigit():
                raise InterchangeError(f"CSV row {row_number}: invalid year")
            metadata["year"] = int(year)
        for key in ("journal", "url"):
            value = (row.get(key) or "").strip()
            if value:
                metadata[key] = value
        authors = [item.strip() for item in (row.get("authors") or "").split(";") if item.strip()]
        if authors:
            metadata["authors"] = authors
        kind = "dataset" if set(identifiers) == {"accession"} else "paper"
        records.append(
            InterchangeRecord(
                kind=kind,
                title=(row.get("title") or "").strip(),
                identifiers=identifiers,
                metadata=metadata,
                input_ref=f"csv-row:{row_number}",
            )
        )
    if not records:
        raise InterchangeError("CSV contains no records")
    return records


def parse_ris(text: str) -> list[InterchangeRecord]:
    records: list[InterchangeRecord] = []
    current: dict[str, list[str]] | None = None
    start_line = 0
    tag_pattern = re.compile(r"^([A-Z][A-Z0-9])  -(?: ?(.*))?$")
    for line_number, raw_line in enumerate(text.lstrip("\ufeff").splitlines(), start=1):
        if not raw_line.strip():
            continue
        match = tag_pattern.fullmatch(raw_line.rstrip())
        if match is None:
            raise InterchangeError(f"RIS line {line_number}: unsupported continuation or tag syntax")
        tag, value = match.group(1), (match.group(2) or "").strip()
        if tag == "TY":
            if current is not None:
                raise InterchangeError(f"RIS line {line_number}: nested TY record")
            current = {"TY": [value]}
            start_line = line_number
            continue
        if current is None:
            raise InterchangeError(f"RIS line {line_number}: tag before TY")
        if tag == "ER":
            records.append(_record_from_ris(current, start_line))
            current = None
            continue
        current.setdefault(tag, []).append(value)
    if current is not None:
        raise InterchangeError(f"RIS record from line {start_line} is missing ER")
    if not records:
        raise InterchangeError("RIS contains no records")
    return records


def _record_from_ris(fields: Mapping[str, list[str]], start_line: int) -> InterchangeRecord:
    identifiers: dict[str, str] = {}
    if fields.get("DO"):
        identifiers["doi"] = fields["DO"][0]
    for tag in ("AN", "ID"):
        for value in fields.get(tag, []):
            match = _PREFIX_RE.fullmatch(value)
            if match:
                identifiers[match.group(1)] = match.group(2)
    for value in fields.get("UR", []):
        if re.fullmatch(r"https?://openalex\.org/W\d+", value, flags=re.IGNORECASE):
            identifiers["openalex"] = value
    normalized = normalize_identifiers(identifiers)
    if not normalized:
        raise InterchangeError(f"RIS record from line {start_line}: identifier is required")
    metadata: dict[str, Any] = {}
    authors = fields.get("AU", []) + fields.get("A1", [])
    if authors:
        metadata["authors"] = authors
    year_values = fields.get("PY", []) or fields.get("Y1", [])
    if year_values:
        match = re.match(r"^(\d{4})", year_values[0])
        if match is None:
            raise InterchangeError(f"RIS record from line {start_line}: invalid year")
        metadata["year"] = int(match.group(1))
    journal_values = fields.get("JO", []) or fields.get("JF", []) or fields.get("T2", [])
    if journal_values:
        metadata["journal"] = journal_values[0]
    if fields.get("UR"):
        metadata["url"] = fields["UR"][0]
    title_values = fields.get("TI", []) or fields.get("T1", [])
    return InterchangeRecord(
        kind="dataset" if set(normalized) == {"accession"} else "paper",
        title=title_values[0] if title_values else "",
        identifiers=normalized,
        metadata=metadata,
        input_ref=f"ris-line:{start_line}",
    )


def parse_bibtex(text: str) -> list[InterchangeRecord]:
    source = text.lstrip("\ufeff").strip()
    if re.search(r"@(string|preamble|comment)\s*[({]", source, flags=re.IGNORECASE):
        match = re.search(r"@(string|preamble|comment)", source, flags=re.IGNORECASE)
        assert match is not None
        raise InterchangeError(f"unsupported BibTeX directive: {match.group(0)}")
    records: list[InterchangeRecord] = []
    cite_keys: set[str] = set()
    position = 0
    while position < len(source):
        while position < len(source) and source[position].isspace():
            position += 1
        if position >= len(source):
            break
        header = re.match(r"@(article|misc|dataset)\s*\{", source[position:], flags=re.IGNORECASE)
        if header is None:
            raise InterchangeError(f"unsupported BibTeX entry near character {position}")
        entry_type = header.group(1).lower()
        body_start = position + header.end()
        body_end = _find_matching_brace(source, body_start - 1)
        body = source[body_start:body_end]
        key, separator, fields_text = body.partition(",")
        cite_key = key.strip()
        if not separator or not cite_key:
            raise InterchangeError("BibTeX entry requires a citation key and fields")
        if cite_key in cite_keys:
            raise InterchangeError(f"duplicate BibTeX citation key: {cite_key}")
        cite_keys.add(cite_key)
        fields = _parse_bibtex_fields(fields_text)
        if "crossref" in fields:
            raise InterchangeError(f"BibTeX entry {cite_key}: crossref is unsupported")
        records.append(_record_from_bibtex(entry_type, cite_key, fields))
        position = body_end + 1
    if not records:
        raise InterchangeError("BibTeX contains no records")
    return records


def _find_matching_brace(source: str, opening: int) -> int:
    depth = 0
    quoted = False
    escaped = False
    for index in range(opening, len(source)):
        char = source[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"' and depth == 1:
            quoted = not quoted
            continue
        if quoted:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    raise InterchangeError("unterminated BibTeX entry")


def _parse_bibtex_fields(text: str) -> dict[str, str]:
    if _contains_top_level_hash(text):
        raise InterchangeError("BibTeX string concatenation is unsupported")
    fields: dict[str, str] = {}
    position = 0
    while position < len(text):
        while position < len(text) and (text[position].isspace() or text[position] == ","):
            position += 1
        if position >= len(text):
            break
        key_match = re.match(r"([A-Za-z][A-Za-z0-9_-]*)\s*=\s*", text[position:])
        if key_match is None:
            raise InterchangeError(f"invalid BibTeX field near character {position}")
        key = key_match.group(1).lower()
        position += key_match.end()
        if position >= len(text):
            raise InterchangeError(f"missing BibTeX value for {key}")
        if text[position] == "{":
            end = _find_matching_brace(text, position)
            value = text[position + 1 : end]
            position = end + 1
        elif text[position] == '"':
            end = position + 1
            escaped = False
            while end < len(text):
                if text[end] == '"' and not escaped:
                    break
                escaped = text[end] == "\\" and not escaped
                if text[end] != "\\":
                    escaped = False
                end += 1
            if end >= len(text):
                raise InterchangeError(f"unterminated quoted BibTeX value for {key}")
            value = text[position + 1 : end]
            position = end + 1
        else:
            value_match = re.match(r"[^,\s}]+", text[position:])
            if value_match is None:
                raise InterchangeError(f"invalid BibTeX value for {key}")
            value = value_match.group(0)
            position += value_match.end()
        fields[key] = value.strip()
    return fields


def _contains_top_level_hash(text: str) -> bool:
    depth = 0
    quoted = False
    escaped = False
    for char in text:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"' and depth == 0:
            quoted = not quoted
            continue
        if quoted:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif char == "#" and depth == 0:
            return True
    return False


def _record_from_bibtex(
    entry_type: str, cite_key: str, fields: Mapping[str, str]
) -> InterchangeRecord:
    identifiers = normalize_identifiers(
        {
            "doi": fields.get("doi", ""),
            "pmid": fields.get("pmid", ""),
            "openalex": fields.get("openalex", ""),
            "accession": fields.get("accession", ""),
        }
    )
    if not identifiers:
        raise InterchangeError(f"BibTeX entry {cite_key}: identifier is required")
    metadata: dict[str, Any] = {}
    if fields.get("author"):
        metadata["authors"] = [item.strip() for item in fields["author"].split(" and ") if item.strip()]
    if fields.get("year"):
        if not fields["year"].isdigit():
            raise InterchangeError(f"BibTeX entry {cite_key}: invalid year")
        metadata["year"] = int(fields["year"])
    journal = fields.get("journal") or fields.get("booktitle")
    if journal:
        metadata["journal"] = journal
    if fields.get("url"):
        metadata["url"] = fields["url"]
    return InterchangeRecord(
        kind="dataset" if entry_type == "dataset" or set(identifiers) == {"accession"} else "paper",
        title=fields.get("title", ""),
        identifiers=identifiers,
        metadata=metadata,
        input_ref=f"bibtex:{cite_key}",
    )


_EXPORT_FIELDS = (
    "title",
    "doi",
    "pmid",
    "openalex_id",
    "accession",
    "year",
    "journal",
    "authors",
    "url",
)
_IDENTIFIER_PRIORITY = ("doi", "pmid", "openalex", "accession")


def _sorted_entities(entities: list[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    def primary(entity: Mapping[str, Any]) -> tuple[int, str]:
        identifiers = entity.get("identifiers", {})
        if not isinstance(identifiers, Mapping):
            raise InterchangeError("entity identifiers must be a mapping")
        for rank, key in enumerate(_IDENTIFIER_PRIORITY):
            value = identifiers.get(key)
            if value:
                return rank, str(value)
        raise InterchangeError("standard export requires DOI, PMID, OpenAlex, or accession")

    return sorted(entities, key=primary)


def export_csv(entities: list[Mapping[str, Any]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=_EXPORT_FIELDS, lineterminator="\n")
    writer.writeheader()
    for entity in _sorted_entities(entities):
        identifiers = entity.get("identifiers", {})
        metadata = entity.get("metadata", {})
        assert isinstance(identifiers, Mapping)
        assert isinstance(metadata, Mapping)
        authors = metadata.get("authors", [])
        writer.writerow(
            {
                "title": entity.get("title", ""),
                "doi": identifiers.get("doi", ""),
                "pmid": identifiers.get("pmid", ""),
                "openalex_id": identifiers.get("openalex", ""),
                "accession": identifiers.get("accession", ""),
                "year": metadata.get("year", ""),
                "journal": metadata.get("journal", ""),
                "authors": "; ".join(str(author) for author in authors)
                if isinstance(authors, list)
                else str(authors),
                "url": metadata.get("url", ""),
            }
        )
    return stream.getvalue()


def export_ris(entities: list[Mapping[str, Any]]) -> str:
    lines: list[str] = []
    for entity in _sorted_entities(entities):
        identifiers = entity.get("identifiers", {})
        metadata = entity.get("metadata", {})
        assert isinstance(identifiers, Mapping)
        assert isinstance(metadata, Mapping)
        lines.append("TY  - DATA" if entity.get("kind") == "dataset" else "TY  - JOUR")
        if entity.get("title"):
            lines.append(f"TI  - {entity['title']}")
        authors = metadata.get("authors", [])
        if isinstance(authors, list):
            lines.extend(f"AU  - {author}" for author in authors)
        if metadata.get("year"):
            lines.append(f"PY  - {metadata['year']}")
        if metadata.get("journal"):
            lines.append(f"JO  - {metadata['journal']}")
        if identifiers.get("doi"):
            lines.append(f"DO  - {identifiers['doi']}")
        for key in ("pmid", "openalex", "accession"):
            if identifiers.get(key):
                lines.append(f"AN  - {key}:{identifiers[key]}")
        if metadata.get("url"):
            lines.append(f"UR  - {metadata['url']}")
        lines.append("ER  -")
        lines.append("")
    return "\n".join(lines)


def export_bibtex(entities: list[Mapping[str, Any]]) -> str:
    entries: list[str] = []
    for entity in _sorted_entities(entities):
        identifiers = entity.get("identifiers", {})
        metadata = entity.get("metadata", {})
        assert isinstance(identifiers, Mapping)
        assert isinstance(metadata, Mapping)
        id_type, id_value = next(
            (key, str(identifiers[key]))
            for key in _IDENTIFIER_PRIORITY
            if identifiers.get(key)
        )
        cite_key = re.sub(r"[^a-z0-9]+", "_", f"{id_type}_{id_value}".lower()).strip("_")
        entry_type = "dataset" if entity.get("kind") == "dataset" else "article"
        fields: list[tuple[str, str]] = []
        if entity.get("title"):
            fields.append(("title", str(entity["title"])))
        authors = metadata.get("authors", [])
        if isinstance(authors, list) and authors:
            fields.append(("author", " and ".join(str(author) for author in authors)))
        if metadata.get("year"):
            fields.append(("year", str(metadata["year"])))
        if metadata.get("journal"):
            fields.append(("journal", str(metadata["journal"])))
        for key in _IDENTIFIER_PRIORITY:
            if identifiers.get(key):
                fields.append((key, str(identifiers[key])))
        if metadata.get("url"):
            fields.append(("url", str(metadata["url"])))
        rendered = [f"@{entry_type}{{{cite_key},"]
        for index, (key, value) in enumerate(fields):
            suffix = "," if index < len(fields) - 1 else ""
            rendered.append(f"  {key} = {{{_escape_bibtex(value)}}}{suffix}")
        rendered.append("}")
        entries.append("\n".join(rendered))
    return "\n\n".join(entries) + ("\n" if entries else "")


def _escape_bibtex(value: str) -> str:
    return value
