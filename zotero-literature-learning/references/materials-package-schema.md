# Materials Package Schema

这是 `zotero-literature-learning` 的结构化输出约定。它描述记录什么，不替代当前会话中真实可见的 Zotero MCP tool schema。

## Status values

| Field | Allowed values | Meaning |
|---|---|---|
| `corpus_status` | `Ready`, `Partial`, `Caution`, `Unavailable` | 整个素材包的可用性 |
| `metadata_status` | `inspected`, `partial`, `unavailable` | 是否实际读取 Zotero metadata |
| `access_status` | `metadata-only`, `abstract-only`, `full-text-partial`, `full-text-inspected`, `pdf-page-inspected`, `inaccessible` | 实际读取层级 |
| `calibration_confidence` | `high`, `medium`, `low`, `none` | peer corpus 对目标 section 的匹配信心 |
| `support_level` | `direct`, `partial`, `context-only`, `not-inspected`, `contradictory` | source 对 claim 的支持关系 |

## Candidate record

```yaml
source_id: S01
zotero_item_key: ""
title: ""
authors: []
year: null
venue: ""
doi: "unknown"
pmid: "unknown"
relevance_reason: ""
article_type_match: true
section_match: true
design_or_method_match: true
metadata_status: inspected
access_status: pdf-page-inspected
evidence_usable: true
style_usable: true
argument_usable: true
inspection_basis: "Introduction, PDF pp. 2-3"
source_locations:
  - section: "Introduction"
    pages: "2-3"
    zotero_link: "zotero://open-pdf/library/items/..."
selection_decision: peer-corpus | evidence-candidate | background | verify | exclude
exclusion_or_uncertainty: ""
next_action: ""
```

## Evidence profile row

```yaml
claim_id: C01
claim: ""
source_id: S01
source_layer: Zotero external evidence | Current study | Interpretive bridge
support_level: direct
usable_fact: ""
evidence_location: ""
boundary: ""
risk: low | medium | high
```

## Style profile row

```yaml
pattern_id: P01
source_id: S01
source_location: "Introduction, PDF p. 2"
pattern_type: rhetorical_move | sentence_function | claim_verb | terminology | information_rhythm | citation_ownership | evidence_boundary | figure_table_integration | reproducibility_move | result_narration_move
short_source_fragment: ""
abstracted_pattern: ""
safe_action: adopt_move | reorder | clarify_subject | calibrate_verb | replace_nonstandard_term | compress_repetition | add_bridge | retain | do_not_adopt
do_not_adopt: ""
author_check: ""
```

## Handoff record

```yaml
next_owner: zotero-evidence-review | zotero-manuscript-thinking | evidence-driven-writing | paper-argument-reconstructor | thinking-model-router
input_files: []
main_action: ""
open_risks: []
done_when: ""
```

## Writing-block card

```yaml
writing_block_type: wording | paragraph_role | method_naming | result_narration | evidence_gap | structure
rhetorical_job: ""
target_text: ""
must_preserve: [study_design, numbers, units, direction, claim_strength, citations]
source_ids: []
candidate_versions:
  - label: conservative | compressed | field_native
    text: ""
    why: ""
    evidence_boundary: ""
    author_check: ""
terminology_decision:
  term_considered: "annotation"
  chosen_term: ""
  reason: ""
  method_check: ""
post_write_audit: claim_unchanged | author_check
```

## Learning decision

```yaml
decision_id: D01
observation: ""
source_ids: [S01]
safe_action: adopt_move | reorder | clarify_subject | calibrate_verb | replace_nonstandard_term | compress_repetition | add_bridge | retain | do_not_adopt
meaning_check: ""
next_owner: zotero-manuscript-thinking | zotero-evidence-review | evidence-driven-writing | author
done_when: ""
```

## File privacy

The package may contain unpublished manuscript text, local Zotero links, notes, and search terms. Keep it outside Git unless the user explicitly asks to share a sanitized fixture.
