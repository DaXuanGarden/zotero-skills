# Writing-first contract

## Purpose

`zotero-literature-learning` learns how peer papers organize problems, evidence, claims, and reader paths, then maps those decisions to the author's manuscript. Markdown is the delivery format; formatting is outside the default scope.

## Required contract

```yaml
mode: corpus_learning | manuscript_review | both
target_section: introduction | methods | results | discussion | whole_paper
target_venue: ""
article_type: original_research | review | methods | protocol | unspecified
rhetorical_job: ""
reader_question: ""
writing_goal:
  - argument
  - paragraph_function
  - reader_path
  - information_order
  - claim_calibration
  - terminology
  - wording_if_reasoning
must_preserve:
  - study_design
  - numbers
  - units
  - direction
  - claim_strength
  - citations
  - author_contribution
formatting_scope: excluded
output_mode: markdown_report_only
```

## Priority order

```text
argument architecture
→ paragraph role
→ reader path
→ information order
→ claim/evidence calibration
→ terminology and transitions
→ surface language
```

## Scope boundary

The skill does not inspect fonts, margins, Word styles, heading layout, reference formatting, or figure formatting unless the user explicitly says the format changes reader comprehension. It does not write to Word, PDF, TeX, or Zotero.
