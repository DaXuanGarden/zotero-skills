# WRITING_OPTIONS_CARD

This reference defines the shared multi-option contract used by the Zotero writing skills. It turns a rewrite request into a small, auditable choice set rather than an unlabelled “best” sentence.

## When to activate

Activate this contract when the user asks for multiple versions, different ways to phrase a sentence, a more field-native expression, alternative paragraph logic, or a choice between conservative and more structural revisions. For a routine evidence check with no rewrite request, keep the ordinary evidence output and do not create options.

Default to at most three options. Use two for a short sentence and four or more only when the user explicitly requests a larger set.

## Required sequence

```text
meaning gate
→ section/rhetorical job
→ peer-style or evidence calibration
→ option generation
→ claim/evidence audit
→ option comparison
→ author selection
→ selected-text POST_WRITE_AUDIT
```

Do not silently treat Option A as the final answer. If the user has not selected an option, set `selection_status: pending` and keep all alternatives visible.

## Required fields

Every option must contain:

```text
option_id          # stable within one task: A, B, C
option_name        # Conservative, Field-native, Logic-forward, or a section-specific name
rhetorical_angle   # the information or reasoning angle
target_section     # Introduction, Methods, Results, Discussion, or other
rhetorical_job     # what this sentence/paragraph does for the reader
copy_ready_text    # manuscript-ready text only
claim_delta        # none, or a precise description of any changed claim
evidence_level     # A, B, C, D, or E
citation_set       # citation IDs actually used by this option
style_basis        # peer pattern IDs, genre-neutral, or none
why_this_works     # one or two concrete reasons
when_to_choose     # the situation for which this option is best
risks              # meaning, evidence, style, or transition risks
author_check       # unresolved decision the author must confirm
```

The card itself also contains:

```text
task_id
input_scope
corpus_status
calibration_confidence
selection_status   # pending, selected, or author-rejected
selected_option_id
```

## Default option families

| Section | Preferred angles |
|---|---|
| Introduction | context-first; gap-forward; objective/contribution-forward |
| Methods | reproducibility-first; compact-procedural; design-rationale-first |
| Results | finding-first; analysis-first; quantitative-anchor-first |
| Discussion | finding-to-interpretation; comparison-with-literature; alternative-explanation/limitation; bounded-implication |

The generic three-option set is:

1. **Conservative** — preserve meaning, order, numbers, and claim strength while improving clarity.
2. **Field-native** — use inspected peer patterns for terminology, claim verbs, information rhythm, and citation ownership without copying prose.
3. **Logic-forward** — reorder information to make the paragraph’s rhetorical job and reader path explicit.

## Evidence and RIS rules

- All options share the same facts, numbers, units, directions, study design, and evidence boundary unless `claim_delta` says otherwise.
- A citation may appear in an option only when its ledger row supports that option’s exact wording or its explicitly labelled background role.
- The selected option’s supported citations receive `RIS action = Include`.
- Citations used only by unselected options receive `RIS action = Optional` until the author selects that option.
- Uninspected, contradictory, or not-addressed citations remain `Verify` or `Exclude`.
- A change from association to causation, plausibility to mechanism, or current-study observation to general claim is a high-risk `claim_delta` and requires `author_check`.

## Comparison table

```markdown
| Option | Rhetorical angle | What changes | Claim delta | Evidence level | Citation set | When to choose | Main risk |
|---|---|---|---|---|---|---|---|
| A | ... | ... | none | ... | ... | ... | ... |
```

## Selection handoff

After the author chooses, record `selected_option_id`, copy the selected text into the ordinary manuscript output, update the Citation Support Ledger and RIS actions, and run the minimum `POST_WRITE_AUDIT`:

```text
claim_unchanged
numbers_units_direction_unchanged
citation_ownership_preserved
methods_results_aligned
new_unsupported_claim
author_check
```

## Safety boundary

Peer papers provide abstracted writing patterns and evidence locations, not sentences to copy. “More native” never means stronger. If the corpus is unavailable, use `style_basis: genre-neutral` and lower `calibration_confidence`; do not claim field calibration was completed.
