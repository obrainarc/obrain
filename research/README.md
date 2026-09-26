# Field studies

Completed studies of the organism. Each study is a self-verifying package:
report, figures, machine-readable data, verification artifacts, and
`SHA256SUMS` over all of them.

| Code | Study | Window |
|---|---|---|
| CS-001 | *Consensus-executed neurophysiology of an immortal Drosophila connectome: an exhaustive census of `BrainState` emissions across the first 74 ticks of on-chain ontogeny* | ticks 1-74, 2026-09-16 to 2026-09-21 |
| CS-002 | *A founder generation dealt by consensus: somatic identity, germline provenance and population genetics of 153 Drosophila descendants of the obrain connectome* | blocks 22,703,390-22,853,967, 2026-09-26 |

CS-001 is published in English, Chinese (`.zh.md`), Japanese (`.ja.md`),
Vietnamese (`.vi.md`) and Hindi (`.hi.md`) editions; data, figures and
verification artifacts are shared between them. CS-002 is published in English.

To re-audit a census against the living chain, from the repository root:

    python3 tools/verify_census.py

To replay the organism's whole recorded life against the twin:

    python3 tools/verify_twin.py --fired $(cat research/2026-09-22-brainstate-census/data/poke_inputs.txt)

To re-derive the Flybook founder census (CS-002) and audit every descendant at head:

    python3 tools/verify_flybook.py --check research/2026-09-26-flybook-founders/data/founder_census.csv
