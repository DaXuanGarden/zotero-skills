# Assignment schema

The assignment manifest is the stable boundary between evidence review and EndNote filing. The top-level object must contain `assignments`, which is a list of paragraph objects. Each object has `section`, `paragraph_id`, and `references`. `paragraph_title` is optional but recommended.

Each reference should contain one of `doi`, `pmid`, `zotero_key`, or `title`. Optional fields are `role`, `priority`, `claim_ids`, and `note`. The bridge normalises DOI and PMID values and stops when one identifier resolves to more than one incoming record.

`priority` is an ordering hint (`P1`, `P2`, or `P3`), not an evidence grade. `role` is carried into EndNote `Keywords` and `Research Notes`; it is not rewritten into a causal claim.
