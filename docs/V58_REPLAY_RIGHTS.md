# Kaggriculture public replay and action-trace reuse

Checked against Kaggle’s published competition rules and Terms of Use on 2026-09-26. This is a source-based reading for this project, not a definitive legal opinion. The official competition is [Kaggriculture](https://www.kaggle.com/competitions/kaggriculture), competition ID 147734. Kaggle’s rules API page ID 742993 and the SHA-256 of the fetched rules text are recorded in [`experiments/v58_rights/source_manifest.json`](../experiments/v58_rights/source_manifest.json); the text itself is not mirrored here.

## Decision

| Use | Finding | Basis |
|---|---|---|
| View or download a public episode replay and inspect its actions for analysis | **Yes** | Kaggriculture Rule 2.11 says episode replays may be publicly available and downloadable. The official Kaggriculture getting-started guide documents `kaggle competitions replay` “for visualization or analysis.” |
| Use replay observations to derive general strategic ideas and implement an independently designed, observation-conditioned policy | **Yes, with ordinary rule and rights constraints** | Rule 2.6 permits qualifying external data that is publicly and equally accessible at no cost (or meets the stated reasonableness standard). The replay is an official public/downloadable source. The resulting submission must still satisfy Rule 3.14’s originality and non-infringement warranties. |
| Copy another player’s complete 719-action sequence or a substantial route tape into our submitted agent | **Uncertain; do not do this without explicit permission or a clearly applicable license** | The rules permit replay availability and broad Competition Data use, but do not expressly say that another participant’s action sequence may be copied into, redistributed as, or submitted as one’s own agent policy. Rule 3.14 requires the submission to be the participant’s original work and warrants sole/exclusive ownership and rights to grant required licenses. Kaggle’s Terms also say that download functionality does not remove Content restrictions. |
| Publish or redistribute raw replay files outside the competition | **No, unless the material is confirmed not to be Competition Data or permission is obtained** | Kaggriculture Rule 2.4(b) prohibits transmitting, duplicating, publishing, or redistributing Competition Data to people who are not participants. The scope of “Competition Data” as applied to generated replay files is not separately defined, so keep raw replays private/ignored rather than mirror them. |

## What the first-party text says

The competition-specific rules identify the **Data Access and Use license as Apache 2.0** and separately identify **CC-BY 4.0 as the winner license**. Rule 2.4(a) says Competition Data may be used for any purpose, commercial or non-commercial; Rule 2.4(b) restricts providing Competition Data to non-participants. Rule 2.6 allows external data that is publicly available and equally accessible to all participants at no cost, subject to its reasonableness criteria. [Official Kaggriculture rules](https://www.kaggle.com/competitions/kaggriculture/rules)

Rule 2.11 says replays may be publicly available and downloadable and include actions taken by a submission. Rule 2.12 says an evaluated submission cannot pull in or use information external to the submission and environment, or send information out. That is a runtime boundary; it does not itself grant copyright or redistribution rights in a route copied from a replay. [Official Kaggriculture rules](https://www.kaggle.com/competitions/kaggriculture/rules)

Rule 3.14 requires the participant to warrant that the submission is original, that the participant is its sole and exclusive owner/rightsholder, and that the participant has authority to grant the required licenses; it also bars infringement of third-party rights. Rule 2.5’s CC-BY 4.0 winner obligation applies to the winner’s own winning submission and source code used to generate it. It does not expressly license other players’ replay traces. The competition-specific code-sharing rule also says public Competition Code sharing must be on the Kaggle competition forum or notebooks and under an OSI-approved license that does not limit commercial use. [Official Kaggriculture rules](https://www.kaggle.com/competitions/kaggriculture/rules)

Kaggle’s [official getting-started guide](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/AGENTS.md) documents replay downloads for visualization or analysis and submission mechanics. Kaggle’s [Terms of Use, §§4–5](https://www.kaggle.com/terms) treat site materials as protected Content, prohibit copying/storing a significant portion, and say that a download feature alone does not suspend those restrictions. Section 8 says an environment episode’s agent activity may be available for viewing and download. Section 9 gives other service users rights in publicly shared submissions only “as permitted by the functionality of the Services.” These provisions support viewing and analysis through the replay feature, but they do not expressly resolve embedding another player’s complete action tape in a competition entry.

## Practical path for this project

Use public replays to measure states, action frequencies, economics, and route constraints. Record the episode ID and cite the replay when discussing findings. Then implement the strategy as a new policy derived from the game rules and current observation—for example, a price-gated wheat-production rule or feed-reserve-aware sell rule—rather than storing an episode’s step-by-step actions, seed-specific route, or replay-derived action tape. Keep downloaded replays out of public repositories and submission bundles unless Kaggle or the relevant author gives clear permission for that use.

If the team wants to submit a literal action-sequence imitation policy, the public-replay clauses alone leave the reuse question unresolved. Obtain explicit permission from the relevant participant and a clear license covering use in a competition submission, or ask Kaggle for clarification before including the trace.

## Primary sources

- [Kaggriculture competition rules](https://www.kaggle.com/competitions/kaggriculture/rules) — especially Competition-Specific Rules 2.4–2.6, 2.11–2.12, 2.5, and General Rules 3.14.
- [Kaggriculture competition overview](https://www.kaggle.com/competitions/kaggriculture/overview) and [official getting-started guide](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/AGENTS.md) — replay and submission commands.
- [Kaggle Terms of Use](https://www.kaggle.com/terms) — §§4–5, 8–9.
- [Kaggle competition citation/CLI guide](https://www.kaggle.com/competitions/kaggriculture/overview/citation) — joining, downloading, submission and replay commands.
