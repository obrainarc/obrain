# Field studies

Completed studies of the organism. Each study is a self-verifying package:
report, figures, machine-readable data, verification artifacts, and
`SHA256SUMS` over all of them.

| Code | Study | Window |
|---|---|---|
| CS-001 | *Consensus-executed neurophysiology of an immortal Drosophila connectome: an exhaustive census of `BrainState` emissions across the first 74 ticks of on-chain ontogeny* | ticks 1-74, 2026-09-16 to 2026-09-21 |

Studies are published in English, Chinese (`.zh.md`), Japanese (`.ja.md`),
Vietnamese (`.vi.md`) and Hindi (`.hi.md`) editions; data, figures and
verification artifacts are shared between them.

To re-audit a census against the living chain, from the repository root:

    python3 tools/verify_census.py

To replay the organism's whole recorded life against the twin:

    python3 tools/verify_twin.py --fired $(cat research/2026-09-22-brainstate-census/data/poke_inputs.txt)
