# Decision: submitting the frozen V57 replay-derived reset

**Verdict: no-go on the current record; the legal position is uncertain, and attribution by itself does not clear it.** Do not submit the frozen V57 reset as a literal replay-route agent unless Kaggle/the sponsor confirms in writing that the Competition Data Apache 2.0 grant covers another participant's replay actions and that this use is compatible with Rule 3.14, or the relevant rights-holder supplies an explicit license and Kaggle confirms the originality warranty can still be made. A fresh observation-conditioned policy is the cleaner path.

This is a rules and provenance assessment, not legal advice. No agent was changed, no submission was made, and no replay was published by this check.

## What the frozen artifact contains

`experiments/v57_broad/v57_reset_candidate.py` has SHA-256 `4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e`. Its embedded `_ACTIONS` value has 719 entries and is exactly equal, after JSON parsing, to `experiments/v57/lizs_route.json` (SHA-256 `2a251049edd2026d9894b6e387d3192792f8bb187822ae3bd987a2a79c1b6bea`). The actions trace to the public Lizs game, episode 112896760, as recorded in `docs/RESEARCH_LOG.md`. The reset artifact's own docstring says its farm route was adapted from the public Lizs replay. The reset fix and later V57 controls do not remove that embedded route dependency.

That evidence makes this a direct reuse question, rather than a case where public replay analysis merely influenced a newly authored policy. Attribution should identify Lizs and episode 112896760, but it would not itself provide a license or turn the copied sequence into independently authored strategy.

## Official rules fetched through Kaggle's API

I fetched the published `rules` page for Kaggriculture (`competition_id=147734`, PageService page ID `742993`) using the authenticated Kaggle API client’s `competition_list_pages("kaggriculture", page_name="rules")`. The current content hash is `79ef510e2623d1fd836e900937a01847bd9ab78ba89ce08b9afced8c569679c9` (37,388 UTF-8 bytes), matching the previously recorded hash in [`source_manifest.json`](../experiments/v58_rights/source_manifest.json). This records the API response version reviewed; the [official rules page](https://www.kaggle.com/competitions/kaggriculture/rules) remains authoritative if later changed.

The numbering needs care because the official page distinguishes the competition metadata, competition-specific provisions, and general rules:

- The Competition-Specific Terms label Data Access and Use as Apache 2.0 (the `1.7` metadata item). Rule 2.4(a) separately permits use of Competition Data “for any purpose,” while 2.4(b) bars making Competition Data available to non-participants. Rule 3.18(a) defines Competition Data broadly to include data or datasets available from the competition website for competition use, including prototype or executable code.
- Rule 2.11 says an episode replay, including the actions taken by a submission, may be public and downloadable. This clearly supports viewing and downloading the route for analysis. It does not expressly state that public availability is a separate copyright license or that action traces are free to embed in another participant’s agent.
- General Rule 3.6(b) permits public code sharing only on Kaggle’s competition forum or a notebook associated with the competition, and deems shared code licensed under an OSI-approved license without commercial-use restrictions. Rule 3.6(c) requires qualifying OSI-approved licenses for open-source code used in a submission. These govern code sharing and code dependencies; they are not a direct license to copy a third party’s replay data.
- Rule 3.14 requires the entrant to warrant that the Submission is their own original work, that they are its sole and exclusive owner and rights-holder, and that they can grant required licenses; it also prohibits infringement of third-party rights. Rule 2.5 separately identifies CC-BY 4.0 for a winning submission. A submitter must be able to honor that obligation without purporting to relicense material they do not control.

Thus Rules 2.4/2.11 support access and competition use of the replay, but do not remove the need to satisfy Rule 3.14 or resolve who owns/licensed the participant-authored action stream. The `Apache 2.0` data-use label is meaningful evidence for permission to use Competition Data, not an unambiguous statement that replay contributors assigned or licensed every action sequence to the sponsor for derivative agent submissions.

## Apache 2.0 and the unresolved rights holder

The primary [Apache License 2.0 text](https://www.apache.org/licenses/LICENSE-2.0) grants a broad but **non-exclusive** copyright license to reproduce and prepare derivatives. Section 4 requires a copy of the license to recipients, prominent modification notices, and retention of applicable source notices and NOTICE attributions. It does not convey ownership. If the trace is covered by the sponsor's Apache grant, this license likely removes the need for a separate permission from Lizs for copyright acts within that grant, provided its conditions are met. But the rules page does not attach a replay-specific copyright notice, name the replay contributor as a licensor, or explicitly resolve whether the sponsor's data-use license reaches participant-created action traces.

Even if Apache covers copyright reuse, a literal 719-turn tape leaves a separate Rule 3.14 problem: it is difficult to represent the copied route as the entrant's own original work and to claim sole and exclusive rights in it. Attribution is necessary where applicable, but it does not answer that warranty. Nor does the fact that the agent wraps the sequence with online helpers change the source of the principal farm route.

## Kaito notebook precedent

Kaito Fukami’s Kaggle notebook, [“103/128 Fresh Public | v43 Sparse Shop Hybrid”](https://www.kaggle.com/code/kaitofukami/103-128-fresh-public-v43-sparse-shop-hybrid?scriptVersionId=344404785), version 13, displayed a public score of 2882.0 at the time of the prior source audit and states Apache 2.0. Its published source uses medoid action routes derived from public Kaggriculture replays and credits multiple sources; the local source snapshot and NOTICE are described in [`V58_LICENSED_BASELINES.md`](V58_LICENSED_BASELINES.md) and [`V58_OPEN_AGENT_SOURCES.md`](V58_OPEN_AGENT_SOURCES.md).

This is a useful precedent showing that an Apache-labeled, replay-derived notebook was publicly shared and scored. It is not a Kaggle ruling, written permission from the upstream replay authors, proof that Kaito owned every medoid trace, or a waiver of Rule 3.14 for another entrant. Public score and a notebook license are not evidence that Kaggle approved the underlying replay-route rights.

## Permission and recommended decision

**Does author permission remain?** There are two conditional answers:

1. If Kaggle confirms that its Apache 2.0 Competition Data grant covers the public replay’s participant-authored actions and the intended embedding, Apache 2.0 likely means separate author permission is not required for those licensed copyright uses. The conditions and attribution obligations would still need to be met.
2. Without that confirmation, explicit permission from the replay rights-holder (Lizs / the author of the source submission) remains the prudent way to clear the trace’s copyright and reuse rights. The current local provenance names the player and episode but does not contain a direct author license or replay-specific license notice.

In either case, author permission alone does not settle Rule 3.14’s “own original work” and sole-rights representation. The safest decision for the frozen tape artifact is **do not submit**. Ask Kaggle/sponsor for a written interpretation if preserving the tape is essential, or replace it with a policy that computes each action from the live observation and uses the replay only as research evidence. If a licensed derivative is ever prepared, include the exact upstream attribution and episode reference, the applicable Apache license text, applicable notices, and prominent modification notices; keep the literal route and raw replay out of public artifacts unless their redistribution rights are separately clear.

## Sources

- [Official Kaggriculture rules](https://www.kaggle.com/competitions/kaggriculture/rules); exact API response metadata/hash: [`source_manifest.json`](../experiments/v58_rights/source_manifest.json).
- [Apache License 2.0, official text](https://www.apache.org/licenses/LICENSE-2.0).
- [Kaito Fukami, notebook v13](https://www.kaggle.com/code/kaitofukami/103-128-fresh-public-v43-sparse-shop-hybrid?scriptVersionId=344404785); its runtime provenance and licensing caveat are recorded in [`V58_LICENSED_BASELINES.md`](V58_LICENSED_BASELINES.md) and [`V58_OPEN_AGENT_SOURCES.md`](V58_OPEN_AGENT_SOURCES.md).
- Local route provenance and exact tape comparison: `docs/RESEARCH_LOG.md`, `experiments/v57/lizs_route.json`, and `experiments/v57_broad/v57_reset_candidate.py`.
