# Claim review workflow

SHawn EvidenceMap separates **search topics** from **claims**. Search ranking finds candidate records; it does not decide whether a paper supports or contradicts a claim.

## 1. Generate candidate records

```bash
evidencemap \
  "endometrial organoid implantation" \
  --claim "Endometrial organoid co-culture models reproduce selected implantation-related responses." \
  --cartridge bio \
  --limit 10 \
  --json \
  --no-cache > candidate-map.json
```

Every row starts with:

```json
"evidence_relation": "candidate"
```

The output preserves the candidate source sentence, abstract/title sentence position, DOI, PMID when available, source name, and source URL.

## 2. Review the public source text

Open the source URLs. Decide whether the displayed candidate sentence and its source context support, contradict, or do not resolve the supplied claim. EvidenceMap does not make this decision automatically.

Create a review file using `paper_id` values from `candidate-map.json`:

```json
{
  "schema_version": 1,
  "reviews": [
    {"paper_id": "REPLACE_WITH_FIRST_PAPER_ID", "relation": "reviewed-support"},
    {"paper_id": "REPLACE_WITH_SECOND_PAPER_ID", "relation": "reviewed-support"},
    {"paper_id": "REPLACE_WITH_AMBIGUOUS_PAPER_ID", "relation": "uncertain"}
  ]
}
```

Allowed states:

- `candidate`: machine-selected candidate; not reviewed
- `reviewed-support`: manually reviewed as supporting the supplied claim in the represented context
- `reviewed-contradict`: manually reviewed as contradicting the supplied claim in the represented context
- `uncertain`: reviewed but unresolved or contextually ambiguous

Unknown top-level or review-item fields, unknown paper IDs, and unsupported relation values fail closed. A review file also requires a non-empty `--claim`, because support and contradiction relations need an explicit claim context.

## 3. Request the bounded statement gate

```bash
evidencemap \
  "endometrial organoid implantation" \
  --claim "Endometrial organoid co-culture models reproduce selected implantation-related responses." \
  --reviews reviews.json \
  --draft-statement \
  --markdown \
  --no-cache
```

A draft is emitted only when all of the following are true:

1. a claim is supplied;
2. at least two distinct current result rows are marked `reviewed-support`;
3. no current result row is marked `reviewed-contradict`.

Otherwise the output reports `needs_check` and a specific reason. `candidate` and `uncertain` rows never count as reviewed support.

## What the draft means

The draft is a deterministic, evidence-bounded wrapper around the user-supplied claim. It does not rewrite the claim, inspect full text, grade study quality, run statistics, or produce a publication-ready manuscript sentence. A human remains responsible for claim wording, scope, citation fit, and source verification.

Review decisions are applied after search-cache retrieval and are never written into the public query cache.
