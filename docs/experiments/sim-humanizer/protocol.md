# Humanizer pilot protocol

Frozen before editing or grading, 25 November 2026. Base repository revision `75ff2523f380ba572a79bb37384d229f8ef68c4a`, canonical humanizer Git blob `916e03028d18e6ed3d34dd142e37252722b39154`. This is a one-pair adaptation of [Self-Improvement Memory](https://arxiv.org/abs/2611.18856).

Two isolated proposers get the same base, the first source passage in `tests/fixtures/humanizer_editorial_cases.json` and the same brief. They may insert up to 60 words or keep the base. Only proposer two sees H1 in `tests/fixtures/humanizer_hypotheses.json`. Both record their predictions before accessing the new cases. Each gets one attempt. The original skill is a third comparison condition. Existing rules may already capture part of the lesson.

The six new synthetic inputs and three binary, equally weighted checks per input are fixed in [cases.json](cases.json). The first four involve an actual question to peers. The other two check transfer to writing with a different purpose. They are convenience samples written by the coordinator, with no intended claim about prevalence.

One editor receives anonymized effective instructions (base plus insertion at its anchor), the common editing brief and the input texts only. Use each of the six possible orderings of three variants once across cases. The editor handles all outputs in one session, which controls the editor identity but allows carryover between variants. One independent proposer per arm also leaves proposal quality confounded with sampling noise.

For grading, independently shuffle the three outputs within each case and hide candidate IDs, order of execution, proposals, predictions and history attribution. The coordinator knows the cases and the research hypothesis. Grade each output against the three frozen checks, including ties. Lock scores before revealing assignments. Report target cases separately from controls, with any lost meaning or regression on a previously passing check called out even when totals improve. Compare memory vs. no memory first and both against the existing skill second. Record observed cost or mark it unknown.

A gain over both comparisons on target cases with controls preserved would justify a replication in a different mechanism or skill. A tie, regression or ambiguous result keeps this hypothesis experimental. One run cannot justify promotion or a general effect size. No edits to the installed or canonical skill are part of this pilot.
