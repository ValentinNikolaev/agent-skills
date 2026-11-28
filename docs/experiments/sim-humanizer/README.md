# Does edit history help improve the humanizer?

25 November 2026. The current humanizer and both proposed edits passed all 18 checks. Keep H1 experimental. This pilot gives no observed quality gain to justify adding either insertion to the canonical skill or creating a general skill from this result.

| Version | Four peer-question cases | Two controls | Inputs changed |
| --- | ---: | ---: | ---: |
| Pinned humanizer | 12/12 | 6/6 | 1/6 |
| [Proposal without history](one.json) | 12/12 | 6/6 | 1/6 |
| [Proposal with H1 history](two.json) | 12/12 | 6/6 | 1/6 |

Five passages came back verbatim in all three conditions. The printer-slip passage contained two copies of the same genuine question. The base and the proposal without history kept the opening question. The history-informed proposal kept the closing question after the evidence. All three removed the stock invitation, asked once and kept the reason the writer had started saving slips. Only this passage required a clear repair. The observed difference in placement is consistent with the second proposal's emphasis on context. The rubric gives neither placement a preference.

## What to carry forward

Both proposers independently chose the same insertion point. The first focused on keeping an invitation open and answerable. The second asked the editor to read the invitation beside the sentence leading into it. Both predicted some improvement over the base. The base already satisfied every acceptance check. These results leave little room to distinguish the proposals. The predicted change in how natural the transition feels to readers also remains unmeasured by any human preference test.

Keep the two predictions with their outcomes, including this tie. If a new incident exposes an actual failure around question placement, that case could distinguish these earlier proposals. A new pilot would need fresh held-out passages and isolated editor sessions per condition before a broader inference. Neither a repeat nor a release is part of this run.

## Evidence and replay

- [Protocol](protocol.md), [frozen cases and scoring criteria](cases.json) and [unblinded outputs with per-check scores](results.json). Each result retains its masked grading label and its execution order.
- The historical source is [H1](../../../tests/fixtures/humanizer_hypotheses.json), based on multiple versions of the same post. The two proposers read the same [original passage](../../../tests/fixtures/humanizer_editorial_cases.json). H1 was the additional input in the second condition. Research basis: [Yu et al., sections 3.2–3.3 and appendix D](https://arxiv.org/pdf/2611.18856).
- Two isolated GPT-6.2 Sol medium proposers produced one candidate each. A third GPT-6.2 Sol medium editor processed 18 outputs in one session. The six orders of the three conditions each occurred once. The coordinator scored anonymized outputs before opening the mapping. The editor could compare instructions and remember earlier outputs, and the coordinator wrote the rubric. These are six synthetic passages, one pair of proposals and one editor session. Token usage and per-arm latency were unavailable. About 37 seconds elapsed between writing the editor packet and writing the outputs, including dispatch and file handling.
- From this directory, run `python replay.py prepare RUN` with a new directory and the baseline Git object available. Give only `RUN/editor.json` to the editor, and save its mapping of job IDs to texts as `RUN/outputs.json`. Run `python replay.py blind RUN`. Grade only `RUN/blind.json`, then save `RUN/scores.json` with keys such as `receipts-A` and three binary values in the frozen check order. Run `python replay.py results RUN` to join scores to conditions. New runs randomize order and masking.
