# Fidelity-first transfer gate

## Transfer scopes

| Scope | Meaning | Allowed action |
|---|---|---|
| `preserve` | Current study facts and author intent | Must remain unchanged |
| `adapt` | Reader path, paragraph function, information order, terminology, transition, or claim calibration | May be transferred with evidence and location |
| `author_decide` | More than one structure or emphasis is scientifically reasonable | Provide options and an author check |
| `reject_transfer` | The pattern would import peer facts, strengthen evidence, or erase the study's own logic | Do not use |

## Mandatory checks

Every revision must answer:

1. Does it still describe the current study accurately?
2. Are design, numbers, units, direction, and results unchanged?
3. Is claim strength unchanged unless `claim_delta` is explicit?
4. Is the evidence boundary preserved?
5. Does the revision improve a specific reader problem?
6. Is the change more than a synonym substitution?
7. Does it preserve the author's contribution and voice?

If a target-venue pattern conflicts with the first seven checks, use `transfer_scope: reject_transfer`.

## Revision card

```yaml
revision_id: R01
draft_segment_id: D03
rhetorical_job: ""
target_reader_question: ""
current_reader_problem: ""
recommended_writing_action: reorder | split | merge | add_bridge | narrow_claim | finding_first | clarify_term | calibrate_verb | retain
before: ""
after_options: []
reasoning_gain: ""
source_pattern_ids: []
transfer_scope: preserve | adapt | author_decide | reject_transfer
claim_delta: none | weaker | stronger | changed
priority: P0 | P1 | P2
author_check: ""
selection_status: pending | selected | rejected
```
