# Evidence-bound Polish Quality Gate

This gate addresses a common failure mode: a paragraph becomes fluent but less accurate, less
field-native, or harder to audit. A polished paragraph is accepted only when the language pass and
the scientific meaning pass both pass.

## 1. Select the narrowest editor

Route the final wording pass to the most specific available skill:

| Problem | Primary editor | Required handoff |
|---|---|---|
| Introduction gap, paragraph role, objective, contribution | `academic-introduction-polisher` | paragraph job, gap type, citations, evidence boundary |
| Discussion finding–interpretation–limitation chain | `academic-discussion-polisher` | finding IDs, alternative explanations, evidence level, citations |
| English medical terminology, syntax, tone, meaning preservation | `medical-english-precision-editor` | must-preserve terms, numbers, design, claim strength |
| Chinese academic prose, de-AI wording, formatting | `writing-core` | language, audience, forbidden style patterns, content boundary |
| Add/verify/replace citations for supplied claims | `academic-reference-matcher` | claim IDs, supplied citations, search scope, verdicts |
| Reference list identity, DOI, deduplication, style | `academic-ref-check` | bibliography, canonical identifiers, unresolved fields |

`zotero-manuscript-thinking` owns diagnosis and sequencing. It should not imitate a generic
“top-journal” voice when a dedicated editor can answer the narrower question.

## 2. Run five gates in order

### Gate A — Meaning gate

Before editing, freeze the paper contract and a `must_preserve` ledger:

```yaml
must_preserve:
  claims: []
  numbers_units_direction: []
  population_or_object: []
  study_design: []
  methods_and_analysis: []
  citations_and_ownership: []
  uncertainty_and_causal_boundary: []
```

If any item is unknown, write `unknown` or `author_check`; do not repair the ambiguity with a more
confident sentence.

### Gate B — Section-logic gate

Assign one primary rhetorical job to each paragraph. Check the local progression:

- Introduction: importance → known evidence → specific gap → why this design → objective;
- Methods: design/sample/variables → operation → quality control/statistics;
- Results: reader question → quantitative finding → figure/table location → next question;
- Discussion: finding → interpretation → comparison → alternative/limitation → bounded implication.

Every transition must express a real relation. Delete or replace `however`, `therefore`, `thus`, and
`consistent with` when the surrounding claims do not justify the relation.

### Gate C — Field-native gate

If the user asks for field-native or venue-calibrated wording, inspect 3–5 matched peer papers when
available and record the section, page, and abstracted pattern. If fewer than three relevant sections
are inspectable, set `calibration_confidence: low` or `none` and use genre-neutral wording. Peer prose
can justify a move or term; it cannot supply a missing result or claim.

### Gate D — Language-precision gate

Correct syntax, subject continuity, modifier attachment, parallelism, terminology, tense, abbreviation
timing, and information density. Prefer precise verbs and ordinary field terms over decorative
synonyms. Keep one main relation per sentence unless the added clause is needed to preserve a
condition, limitation, or comparison.

### Gate E — Evidence and reviewer-risk gate

Check each sentence against its `Source layer` and one A–E evidence level. Confirm that the edit does
not turn association into causation, plausibility into direct evidence, a method output into a finding,
or a current-study result into external proof. Flag unsupported novelty, unbounded generalization,
missing alternatives, and citation ownership changes.

## 3. Required output and acceptance states

For a requested rewrite, return in this order:

1. `Copy-ready text` with no workflow notes;
2. `Logic map` or a one-line paragraph job;
3. `Change log` with original phrase, action, reason, and evidence effect;
4. `POST_WRITE_AUDIT` with the fields below;
5. `Author checks` for unresolved or author-owned decisions.

```yaml
POST_WRITE_AUDIT:
  meaning_gate: pass | needs_author_check | fail
  section_logic_gate: pass | needs_author_check | fail
  field_native_gate: pass | partial | unavailable
  language_precision_gate: pass | needs_author_check | fail
  evidence_boundary_gate: pass | needs_author_check | fail
  claim_unchanged: yes | no | unknown
  numbers_units_direction_unchanged: yes | no | unknown
  citation_ownership_preserved: yes | no | unknown
  new_unsupported_claim: no | yes | unknown
  accepted: pass | revise | author_review
```

`accepted: pass` requires no `fail`, no `no`, and no unresolved high-risk `unknown`. A fluent rewrite
with an evidence-boundary failure is rejected and must be revised before delivery.

## 4. Stop conditions

Stop the polish pass when the requested section has a clear paragraph job, the prose is readable at
the target level of detail, and each remaining issue is either an author decision or a missing source.
Do not continue rewriting solely to make the text sound more prestigious. If two consecutive passes
only replace synonyms without changing a diagnosed problem, return the current copy-ready text and
report that further edits would be cosmetic.
