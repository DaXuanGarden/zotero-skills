# Argument-first full-text reading

## Reading spine

For each peer paper, build:

```text
context
→ known problem
→ concrete gap
→ question/objective
→ method fit
→ finding
→ interpretation
→ limitation/boundary
→ implication
```

## Paragraph record

```yaml
source_id: S01
section: Introduction
source_location: "PDF pp. 2-3"
reader_question: ""
paragraph_function: context | gap | objective | design | result | interpretation | contrast | limitation | implication | transition
main_claim: ""
evidence_anchor: ""
claim_strength: observed | associated | predictive | suggestive | causal
claim_verb_or_hedge: ""
information_order: ""
transition_to_next: ""
abstracted_pattern: ""
```

## Pattern confidence

| Observation | Label | Use |
|---|---|---|
| Appears in one paper | `single_paper_observation` | Inspiration only |
| Appears in two matched papers | `tentative_pattern` | Candidate action with caveat |
| Appears in three or more matched papers | `recurring_genre_pattern` | Higher-confidence transferable action |

Patterns describe writing decisions, not sentences to copy. They cannot import a peer paper's data, results, contribution, or causal interpretation into the current manuscript.
