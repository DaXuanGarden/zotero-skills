# Methods Language Calibration

## 目标

Methods 的语言应该让读者准确知道研究做了什么、输入是什么、输出是什么，以及哪些结论仍需在 Results 或 Discussion 中解释。词汇选择必须服从实际操作，不能为了“像高分论文”使用更大的词。

## `annotation` 的使用边界

使用 `annotation` 的前提是：研究确实把变异、基因、位点或其他对象映射到功能标签、区域、类别或生物学上下文。仅仅做基因分析、组织表达富集、通路富集或候选优先级排序时，`annotation` 往往太宽泛。

| 如果实际做的是 | 优先表达 | 不要默认写成 |
|---|---|---|
| 对变异/基因赋予功能标签 | `functionally annotated variants/genes` | `performed annotation` |
| 基因、组织和通路三个层级的统计分析 | `performed gene-, tissue-, and pathway-level analyses` | `applied gene-, tissue-, and pathway-level annotation` |
| 组织表达或通路富集 | `conducted tissue-expression and pathway-enrichment analyses` | `annotated tissues and pathways` |
| 多组学整合后排序候选 | `integrated ... data to prioritize candidate genes/cell types` | `identified causal genes/cell types` |
| 汇总结果并解释生物学意义 | `characterized the biological processes and tissues implicated by ...` | `demonstrated the mechanism of ...` |

## 句式压缩规则

优先使用一个清楚的主语和一组并列谓语：

```text
We combined X with Y, using Z for validation. We evaluated A, performed B, integrated C to prioritize D, and applied E to assess F.
```

这类句式适合 Methods overview 或 abstract methods sentence。它把研究设计、分析层级和目的分开，避免把所有动作压在一个长句中。若 `for discovery` 和 `for validation` 修饰对象不同，要把修饰对象紧邻对应的数据或分析，避免读者误解。

## 用户示例的保守改写

如果确实执行的是基因、组织和通路层面的分析，而不是给对象添加功能标签，可以写：

> We combined an updated observational meta-analysis with cross-trait analyses of UK Biobank insomnia and FinnGen MASLD summary statistics, using an independent MASLD GWAS for validation. We characterized genome-wide and regional genetic sharing, performed gene-, tissue-, and pathway-level analyses, integrated liver single-cell data to prioritize candidate cell populations, and applied Mendelian randomization to assess causal relationships.

如果具体方法是富集分析，则将中间部分改成：

> ... conducted gene-based, tissue-expression, and pathway-enrichment analyses, integrated liver single-cell data to prioritize candidate cell populations, and applied Mendelian randomization to assess causal relationships.

两版都必须由作者核对：`cross-trait analyses` 的具体方法、`genetic sharing` 的统计定义、单细胞数据的用途，以及 Mendelian randomization 是否真的用于因果评估。
