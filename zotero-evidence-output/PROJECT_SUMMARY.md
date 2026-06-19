# Zotero Evidence Output Project Summary

生成日期：2026-06-19  
范围：当前 `zotero-evidence-output/` 下 9 个 evidence package。  
用途：帮助科研写作者快速判断“该用哪份报告、可写入哪里、有哪些风险、RIS 是否可用”。

## 1. Executive Dashboard

| Topic | Folder | Status | Main conclusion | Use in manuscript | Main risk | RIS file |
|---|---|---|---|---|---|---|
| Epidemiology of sedentary behavior and PCOS | `sedentary_behavior_pcos_2026-06-19_004230/` | Caution | Epidemiological evidence supports cautious sedentary behavior / PCOS framing, but direct genetic overlap is not established. | Introduction / Discussion | Direct sedentary-PCOS shared genetic architecture is not externally replicated. | `sedentary_behavior_pcos_2026-06-19_004230_references.ris` |
| LST-PCOS MR and BMI caveat | `sedentary_behavior_pcos_2026-06-19_005628/` | Caution | LST-PCOS MR evidence can be discussed, but BMI mediation/confounding must be acknowledged. | Discussion | BMI-independent association is not supported as written. | `sedentary_behavior_pcos_2026-06-19_005628_references.ris` |
| MST1R candidate gene | `mst1r_sedentary_pcos_2026-06-19_011400/` | Caution | MST1R/RON biology supports inflammatory and metabolic plausibility, not a proven PCOS mechanism. | Candidate gene discussion | No direct MST1R-PCOS ovarian evidence found. | `mst1r_sedentary_pcos_2026-06-19_011400_references.ris` |
| TANK and TSKU candidate genes | `tank_tsku_pcos_2026-06-19_012712/` | Partial | TANK/TSKU are plausible candidates, but the evidence package is incomplete. | Candidate gene discussion | TSKU PubMed query failed / Too Many Requests. | `tank_tsku_pcos_2026-06-19_012712_references.ris` |
| LST-PCOS multisystem mechanisms | `lst_pcos_multisystem_2026-06-19_014935/` | Caution | Multisystem interpretation is plausible when framed as convergence rather than proof. | Discussion | Cerebellar, PI3K-Akt, AMPK, and immune claims need hedging. | `lst_pcos_multisystem_2026-06-19_014935_references.ris` |
| PCOS multisystem / PMOS framing | `sedentary_behavior_pcos_2026-06-19_015320/` | Partial | PCOS multisystem framing is usable, but PMOS terminology is unresolved. | Discussion | PMOS concept not verified; one export path was absolute. | `sedentary_behavior_pcos_2026-06-19_015320_references.ris` |
| Single-cell ovarian context | `sedentary_behavior_pcos_2026-06-19_0155/` | Caution | Granulosa/macrophage context is plausible but should not overstate present-study genetic signals. | Results / Discussion | BMI-independent genetic claim is current-study only. | `sedentary_behavior_pcos_2026-06-19_0155_references.ris` |
| Limitations paragraph | `sedentary_behavior_pcos_2026-06-19_020100/` | Ready | Limitation wording is cautious and directly usable for manuscript limitations. | Limitations | Propensity score matching lacks a dedicated methods citation. | `sedentary_behavior_pcos_2026-06-19_020100_references.ris` |
| GWAS architecture final review | `sedentary_behavior_pcos_gwas_2026-06-19_021111/` | Caution | Sedentary behavior and PCOS may show convergent genetic/biological architecture, but direct horizontal pleiotropy is unresolved. | Discussion | Avoid claiming shared causal variants or direct pleiotropy as established. | `sedentary_behavior_pcos_gwas_2026-06-19_021111_references.ris` |

## 2. Recommended Use Order

1. Use `sedentary_behavior_pcos_2026-06-19_020100/` first for a manuscript-ready limitations paragraph.
2. Use `sedentary_behavior_pcos_gwas_2026-06-19_021111/` as the canonical GWAS architecture package, with cautious wording.
3. Use `mst1r_sedentary_pcos_2026-06-19_011400/` for MST1R candidate-gene discussion, only as biological plausibility plus present-study prioritization.
4. Use `sedentary_behavior_pcos_2026-06-19_004230/` and `sedentary_behavior_pcos_2026-06-19_005628/` for epidemiology and MR caveats.
5. Use `lst_pcos_multisystem_2026-06-19_014935/` and `sedentary_behavior_pcos_2026-06-19_0155/` for broader discussion only after separating present-study findings from external evidence.
6. Do not use `tank_tsku_pcos_2026-06-19_012712/` or `sedentary_behavior_pcos_2026-06-19_015320/` as final evidence packages until the unresolved PubMed/PMOS issues are addressed.

## 3. High-risk Claims

| High-risk claim | Safer replacement | Relevant package | Status |
|---|---|---|---|
| Sedentary behavior and PCOS share causal variants. | Sedentary behavior and PCOS may have partly convergent genetic and biological architectures. | `sedentary_behavior_pcos_gwas_2026-06-19_021111/` | Caution |
| LST-PCOS association is BMI-independent. | BMI may partly mediate or confound the LST-PCOS association; BMI-independent effects require cautious interpretation. | `sedentary_behavior_pcos_2026-06-19_005628/` | Caution |
| MST1R is implicated in ovarian function or PCOS mechanism. | MST1R/RON biology is consistent with inflammatory and metabolic contexts relevant to PCOS, and present analyses prioritize MST1R for follow-up. | `mst1r_sedentary_pcos_2026-06-19_011400/` | Caution |
| TSKU evidence is complete. | TSKU remains a candidate requiring rerun PubMed search and direct verification. | `tank_tsku_pcos_2026-06-19_012712/` | Partial |
| PMOS is a verified clinical concept. | PCOS has multisystem reproductive, metabolic, inflammatory, and cardiometabolic dimensions. | `sedentary_behavior_pcos_2026-06-19_015320/` | Partial |
| Cerebellar enrichment is externally validated. | Cerebellar enrichment is a present-study signal requiring external validation. | `lst_pcos_multisystem_2026-06-19_014935/` | Caution |

## 4. Reports Marked Partial or Superseded

| Folder | Status | Reason | Required fix |
|---|---|---|---|
| `tank_tsku_pcos_2026-06-19_012712/` | Partial | TSKU PubMed query failed with rate-limit / Too Many Requests. | Rerun PubMed search and update claim-level evidence before final use. |
| `sedentary_behavior_pcos_2026-06-19_015320/` | Partial | PMOS concept not verified; export path included an absolute local path. | Remove or verify PMOS terminology and keep all paths relative. |

No report is currently marked `Superseded`. Canonical-use mapping is handled through the recommended use order above rather than by renaming or deleting folders.

## 5. Reference and Metadata Notes

- Use PubMed-standardized metadata when reports identify malformed or inconsistent Zotero fields.
- Exclude known duplicate/replaced Zotero records from final RIS exports, including duplicate Zhao 2025 and Moran/Zhang/Pesonen replacements noted in package QC sections.
- Treat PubMed-only records as useful but consider importing important final references into Zotero before manuscript submission.
- Keep RIS files as plain RIS records only; do not add Markdown headings or explanatory prose.
- Do not cite external evidence as proof of present-study findings such as colocalization, TWAS, SMR, or single-cell enrichment.

## 6. Next Actions

1. Use `REPORT_TEMPLATE.md` for all newly generated evidence reviews.
2. Maintain `evidence_claims_master.tsv` and `reference_qc_master.tsv` as the project-level registries.
3. Generate `quick_use.md` and `search_log.json` for each package, starting with the three priority packages.
4. Run `scripts/evidence_output_audit.py` before using outputs in a manuscript.
5. Revisit `Partial` packages after failed PubMed searches or unresolved terminology are fixed.
