# Evidence Review: PubMed MCP smoke test

Generated: 2026-06-18
Source: Zotero local library; PubMed: ⚠️ Tool unavailable; search not executed
Input: Smoke test for current skill: Zotero retrieval, PubMed expansion availability, and EndNote-compatible RIS generation.

## 1. Bottom Line
- Zotero MCP is reachable: semantic search, keyword search, metadata retrieval, and attachment lookup completed successfully.
- PubMed MCP is not visible in the current ZCode tool list, so PubMed expansion could not be executed in this session.
- EndNote-compatible RIS can still be generated from inspected Zotero metadata; PubMed-only RIS records were not created.

## 2. Recommended Manuscript Text
> This smoke test confirms that local Zotero evidence retrieval is operational, while PubMed expansion requires a PubMed-capable MCP server to be configured and visible in the active agent session.

## 3. Claim–Evidence Matrix
| # | Claim | Zotero evidence | PubMed evidence | Evidence status | Confidence | Caveat | Recommended citation |
|---|-------|-----------------|-----------------|-----------------|------------|--------|----------------------|
| 1 | Zotero keyword and semantic search can retrieve PCOS sedentary-behaviour literature. | Moran 2013; Tay 2020 | Not searched | Supported | High | Search output included duplicate/non-article notes that require filtering. | Moran 2013; Tay 2020 |
| 2 | PubMed expansion can be run by the skill in the current session. | — | ⚠️ Tool unavailable; search not executed | Gap | High | No PubMed-capable MCP tools are visible in this session. | — |
| 3 | EndNote-compatible RIS can be produced from inspected Zotero metadata. | Moran 2013; Tay 2020 | Not searched | Supported | High | RIS standardization used inspected Zotero metadata; PMID values were available from local Zotero/PubMed-linked records. | Moran 2013; Tay 2020 |

## 4. Citation Placement
| Sentence / location | Recommended citation | Purpose | Wording note |
|---------------------|----------------------|---------|--------------|
| Smoke-test Zotero retrieval | Moran 2013; Tay 2020 | Demonstrate local library search and metadata retrieval | Keep as operational test, not a scientific conclusion. |
| Smoke-test PubMed expansion | — | Tool availability check | State unavailable rather than completed. |

## 5. Reference Table
| # | Citation | Year | Study type | Main use | Evidence source | Zotero | PDF | DOI | PMID | Collection |
|---|----------|------|------------|----------|-----------------|--------|-----|-----|------|------------|
| 1 | Moran et al., *Human Reproduction* | 2013 | Population-based observational study | Smoke-test Zotero search/metadata/PDF/RIS export | Zotero | [Item](zotero://select/items/0_GD6Q3CC9) | [PDF](zotero://open-pdf/library/items/CV8NK8BJ) | [DOI](https://doi.org/10.1093/humrep/det256) | [PMID](https://pubmed.ncbi.nlm.nih.gov/23771201/) | HHUHJIAG; DB9JAHM6 |
| 2 | Tay et al., *Clinical Endocrinology* | 2020 | Cross-sectional study | Smoke-test Zotero search/metadata/PDF/RIS export | Zotero | [Item](zotero://select/items/0_TVKLYHVL) | [PDF](zotero://open-pdf/library/items/98WXMI77) | [DOI](https://doi.org/10.1111/cen.14205) | [PMID](https://pubmed.ncbi.nlm.nih.gov/32324293/) | DB9JAHM6 |

## 6. Zotero Search Summary
| Search route | Query | Hits | Included | Notes |
|--------------|-------|-----:|---------:|-------|
| Semantic search | sedentary behavior and polycystic ovary syndrome physical activity | 5 | 2 | Completed; retrieved Tay 2020 and Moran 2013 among top results. |
| Keyword search | sedentary behavior PCOS | 5 | 2 | Completed; returned duplicate Moran record and two note items, confirming the need for article filtering/deduplication. |
| Metadata retrieval | GD6Q3CC9; TVKLYHVL | 2 | 2 | Completed; canonical title, authors, journal, volume/issue/pages, DOI and abstract were retrieved. |
| Attachment lookup | GD6Q3CC9; TVKLYHVL | 2 parent items | 2 PDFs | Completed; PDF attachment keys CV8NK8BJ and 98WXMI77 were retrieved. |

## 7. PubMed Expansion
Date: 2026-06-18
Database: PubMed
Status: ⚠️ Tool unavailable; search not executed

Query:
```text
("polycystic ovary syndrome"[Title/Abstract] OR PCOS[Title/Abstract]) AND ("sedentary behavior"[Title/Abstract] OR "sedentary behaviour"[Title/Abstract] OR "physical activity"[Title/Abstract])
```

| # | Citation | PMID | DOI | In Zotero? | Evidence use | Recommendation |
|---|----------|------|-----|------------|--------------|----------------|
| — | — | — | — | — | PubMed-capable MCP tools are not visible in this ZCode session. | Configure/restart PubMed MCP, then rerun the package workflow for PubMed-only expansion records. |

## 8. Integrated Writing Advice
### Original claim
Can the current skill retrieve from Zotero and PubMed, and generate an EndNote reference file using PubMed MCP?

### Evidence from Zotero
- Zotero semantic search, keyword search, metadata retrieval, and attachment lookup completed successfully.

### Evidence from PubMed
- PubMed expansion was not executed because no PubMed-capable MCP tools are visible in the active session.

### Recommended revision
> The current skill can retrieve evidence from Zotero and generate EndNote-compatible RIS from inspected Zotero metadata. PubMed expansion is correctly gated by tool availability and cannot run until a PubMed MCP server is configured and visible in the current agent session.

### Why this wording is safer
It distinguishes successful Zotero execution from unavailable PubMed execution and avoids falsely claiming that PubMed was searched.

## 9. Gaps and Reviewer-risk Assessment
| Affected claim / sentence | Risk | Severity | Evidence basis | Suggested fix |
|---------------------------|------|----------|----------------|---------------|
| PubMed retrieval and PubMed-derived EndNote export | Current session lacks PubMed MCP tools, so PubMed search/export cannot be validated end-to-end. | Moderate | No PubMed/NCBI tools are visible in the active tool list. | Configure PancrePal PubMed MCP or another PubMed MCP server, restart ZCode, then rerun this smoke test. |
| RIS metadata standardization by PubMed | PMID/PubMed standardization cannot be tested without PubMed detail tools. | Moderate | RIS was generated from inspected Zotero metadata only. | After PubMed MCP is visible, run PMID detail retrieval and compare RIS standardization source. |

## 10. Metadata Quality Control
| Citation | Missing metadata | Metadata mismatch | Duplicate warning | Evidence source | RIS standardization source | RIS action |
|----------|------------------|-------------------|-------------------|-----------------|----------------------------|------------|
| Moran 2013 | none for core RIS fields | none detected in inspected Zotero metadata | Keyword search found a duplicate Zotero record for the same title; canonical item GD6Q3CC9 used. | Zotero | Zotero metadata | Include |
| Tay 2020 | none for core RIS fields | none detected in inspected Zotero metadata | none detected in this smoke test | Zotero | Zotero metadata | Include |
| PubMed-only records | PubMed not executed | PubMed not executed | PubMed not executed | PubMed unavailable | none | Exclude |

## 11. Export File
- Markdown report: `zotero-evidence-output/pubmed_mcp_smoke_test_2026-06-18_175554/pubmed_mcp_smoke_test_2026-06-18_175554_evidence_review.md`
- EndNote RIS: `zotero-evidence-output/pubmed_mcp_smoke_test_2026-06-18_175554/pubmed_mcp_smoke_test_2026-06-18_175554_references.ris`
- Evidence source: Zotero local library completed; PubMed expansion was unavailable in this session.
- RIS standardization source: inspected Zotero metadata only.
- RIS inclusion rule: final smoke-test Zotero citations only; no PubMed-only records.
- Metadata warnings: PubMed not executed; duplicate Moran record observed in keyword search and handled by selecting GD6Q3CC9 as canonical.
