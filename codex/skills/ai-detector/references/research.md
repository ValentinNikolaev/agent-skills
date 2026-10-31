# Research-backed interpretation

Read this when a request invokes research, a statistical feature, or a disputed
human/AI distinction. Ordinary local editing observations need no literature dump.
The [feature inventory](research-evidence.json) contains definitions, source
anchors, populations, ablations, direction reversals and unresolved counts for
all seven inspected papers. It is maintenance evidence, not a scoring model.

## What can actually be measured

| Signal | Needed to measure it | Boundary for a prose review |
| --- | --- | --- |
| [RelPPR](https://arxiv.org/html/2610.33767v1#S4.SS2): local peak prominence divided by mean predictive entropy | Full next-token distributions from an evaluator, tokenizer and peak convention | Sentence lengths or visible word variety do not supply predictive entropy. |
| [DivEye](https://arxiv.org/html/2509.18880v3#S3.SS2): nine distributional and temporal surprisal features | Observed-token log probabilities and the trained classifier/preprocessing | Surprisal of a selected token differs from entropy of the full distribution; histogram entropy of second differences is a third quantity. |
| [EchoPrompt](https://arxiv.org/html/2608.05741v1#S3.SS2): restored-context comparative score | Matched base/instruction-tuned proxies, exact prefix, aligned log probabilities and calibrated threshold | A passage looking like an answer is not a measurement of latent prompt dependency. |
| [Relational Over-Regularization](https://arxiv.org/html/2608.26694v1#S3): sentence transitions and graph inputs | Specified sentence embeddings, graph features, trained classifier and comparable human data | A transition edit is not a graph-score calculation or a proven detector intervention. |

Without those inputs, label the method **not measured** if it is relevant to the
request. Do not invent a score, infer it from rhythm, or describe a prompt-based
impression as an implementation of the paper. Actual detector runs must retain
version, model/tokenizer, preprocessing, corpus/language, length, threshold and
operating-point evidence. A published AUROC is not a probability for this text.

## Rank evidence within its setting

| Evidence family | Evidence | Permitted conclusion |
| --- | --- | --- |
| Strongest broad linguistic family in this source set: lexical richness | [284-feature study](https://arxiv.org/html/2606.04177v1), Table 5 and Appendices C–D: largest removal losses in several settings, but model/domain reversals | Examine word choice in context. Do not assign all three lexical measures one direction or maximize diversity. |
| Temporal and contextual model signals | RelPPR, DivEye and EchoPrompt report useful results under different proxies, prompts and corpora | Select by deployment setting and compute requirements; their headline metrics do not create a common leaderboard. |
| Sentence-relation patterns | ROR has pooled evidence and a held-out generator reversal | Inspect actual repetition and continuity; no universal rule that AI is more or less irregular. |
| Interpersonal and affective patterns | [Mental-health comparison](https://pmc.ncbi.nlm.nih.gov/articles/PMC13245432/) concerns English Reddit support and three generators | Context-specific observations; do not generalize clinical, empathy or formality scores to arbitrary prose. |
| Psycholinguistic explanation | [Opara](https://arxiv.org/html/2505.01800v1) maps proposed features to theories without a new detection evaluation | Useful questions for inspection; not validated directions, weights or claims about an author's mental processes. |

These are conditional evidence assessments, not a global ranking of unlike
methods, a calibrated detector or an editing priority. Within-source rankings
and their denominators are recorded in the feature inventory. Editing priority
depends on the exact passage's reader cost, supported
meaning and voice. Feature ablation measures marginal utility in that classifier;
it does not establish causation or an independent weight for a checklist.

## Resolve conflicts rather than averaging them

Prefer a newer study provisionally when it tests the same claim in a relevant
setting. Then compare variables, prompt regime, proxy, language, domain, text
length, held-out generators, ablations, uncertainty and false-positive controls.
Check whether a revision adds evidence or only revises presentation. Retain both
conditional findings if they measure different things; leave unresolved conflicts
visible when the evidence cannot choose. Recency never repairs a weak method.

- RelPPR (October 2026) does not invalidate DivEye (v3, February 2026): predictive
  entropy peaks and realized-token surprisal dynamics are distinct quantities.
- RelPPR's instructed-generation experiments narrow the use of some earlier
  baselines. They do not invalidate those baselines for unprompted continuations
  or establish superiority in every domain; its PubMedQA result is a countercase.
- ROR (August 2026) explicitly reports a GPT-5 reversal and weak performance on
  short/structured human text. Keep those boundaries alongside pooled results.
- The June 2026 linguistic study supplies stronger empirical grounds than the
  May 2025 theoretical mapping for cross-domain claims, but its own lexical
  direction statements conflict. Appendix C.4.3's TTR prose disagrees with its
  numbers and Appendix D.2. It also mixes corpus-global and text-local hapax
  descriptions. Do not resolve either discrepancy by guessing.
- The PMC article's tabular and narrative values disagree in several places.
  Its automated empathy measures and human clinician judgements also measure
  different things. Preserve the distinction instead of choosing a convenient score.

## Coverage and reuse limits

The 284-feature paper enumerates 11 groups, not 284 separate variable names.
The psycholinguistic paper claims 31 features but its appendix names 29. The
inventory records every exposed name/group and these gaps; it does not claim to
recover omitted variables. None of these English results supplies validated
Russian-language accuracy or a universal minimum word count.

Research is cited and analyzed in original wording. No paper's code, figures,
table wording or prose is bundled as an adapted resource. The inventory records
licenses; several sources impose noncommercial, no-derivatives or share-alike
terms. Consult the source license before importing any protected material.
