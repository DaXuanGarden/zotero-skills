# Assignment schema

The assignment manifest is the stable boundary between evidence review and EndNote filing. The top-level object must contain `assignments`, which is a list of paragraph objects. Each object has `section`, `paragraph_id`, and `references`. `paragraph_title` is optional but recommended.

Each reference should contain one of `doi`, `pmid`, `zotero_key`, or `title`. Optional fields are `role`, `priority`, `claim_ids`, and `note`. The bridge normalises DOI and PMID values and stops when one identifier resolves to more than one incoming record.

Paragraph IDs are section-specific. Use `Introduction-01` through `Introduction-03` for the three Introduction paragraphs; use named Discussion IDs such as `Discussion-Observational-evidence`; use named Methods modules such as `Methods-Overview` or `Methods-Bidirectional-mendelian-randomisation`. A generic `Paragraph-01` is accepted only for Introduction and is normalized to `Introduction-01`; the same generic ID in Discussion or Methods is rejected so their taxonomies cannot silently collapse into the Introduction taxonomy.

`priority` is an ordering hint (`P1`, `P2`, or `P3`), not an evidence grade. `role` is carried into EndNote `Keywords` and `Research Notes`; it is not rewritten into a causal claim.
