# Field studies

Completed studies of the organism. Each study is a self-verifying package:
report, figures, machine-readable data, verification artifacts, and
`SHA256SUMS` over all of them.

| Code | Study | Window |
|---|---|---|
| CS-001 | *Consensus-executed neurophysiology of an immortal Drosophila connectome: an exhaustive census of `BrainState` emissions across the first 74 ticks of on-chain ontogeny* | ticks 1-74, 2026-09-16 to 2026-09-21 |
| CS-002 | *A founder generation dealt by consensus: somatic identity, germline provenance and population genetics of 153 Drosophila descendants of the obrain connectome* | blocks 22,703,390-22,853,967, 2026-09-26 |
| CS-003 | *The founder generation closed: demography, care, sensory ecology and cryptic genetic variation in 333 Drosophila descendants of the obrain connectome* | blocks 22,703,390-22,971,428, 2026-09-26 to 2026-09-27 |
| CS-004 | *The first offspring: courtship neurophysiology, genotype-dependent mate choice and Mendelian inheritance in 33 G1 Drosophila of the obrain connectome* | blocks 22,971,429-23,713,175, 2026-09-27 to 2026-10-01 |
| CS-005 | *A quiet week: the second breeding wave, a sterile offspring generation, the priming law of courtship and the life table of 384 *Drosophila* of the obrain connectome* | blocks 23,713,176-24,657,020, 2026-10-01 to 2026-10-07 |
| CS-006 | *Every descendant replayed: a chain-exact twin of the Flybook brains, the courtship residual at the membrane, and the latent spikes of 169,088 cells* | 366 brains, 4,331 thoughts to block 24,657,020 |
| CS-007 | *Registered before the fact: what each of 386 brains does at its next thought, the ruling of every founder's next courtship, and which of 1,032 waiting charges can still fire* | registered at block 24,700,042, 2026-10-07 |
| CS-008 | *The economy of the organism: what 390 brains earned, cost and sold for on Arc, and whether a thought can be bought over HTTP* | blocks 22,703,390-24,876,596, census 2026-10-08 |

CS-001 is published in English, Chinese (`.zh.md`), Japanese (`.ja.md`),
Vietnamese (`.vi.md`) and Hindi (`.hi.md`) editions; data, figures and
verification artifacts are shared between them. CS-002 to CS-008 are published in English.

To re-audit a census against the living chain, from the repository root:

    python3 tools/verify_census.py

To replay the organism's whole recorded life against the twin:

    python3 tools/verify_twin.py --fired $(cat research/2026-09-22-brainstate-census/data/poke_inputs.txt)

To re-derive the Flybook founder census (CS-002) and audit every descendant at head:

    python3 tools/verify_flybook.py --check research/2026-09-26-flybook-founders/data/founder_census.csv

To re-derive the complete founder generation (CS-003):

    python3 tools/verify_flybook.py --check research/2026-09-27-flybook-generation-zero/data/founder_census.csv

To re-derive the first offspring generation, its courtships and the window's thoughts (CS-004):

    python3 tools/verify_generation1.py --check research/2026-10-01-flybook-first-offspring/data

To re-derive the cumulative pedigree, courtships and thoughts to CS-005's census block, and the life table of every fly at that block (CS-005):

    python3 tools/verify_generation1.py --check research/2026-10-07-flybook-life-table/data
    python3 tools/verify_lifetable.py --check research/2026-10-07-flybook-life-table/data

The three Flybook tools keep finalized logs and headers in `~/.cache/obrain` so a later study fetches only its own window; the verification run shipped with each study is made with `--fresh`, which reads everything from the chain again.

To replay every brain of the population with the twin and diff it against the chain (CS-006):

    python3 tools/verify_clones.py --check research/2026-10-07-flybook-clone-twin/data

To regenerate CS-007's register of predictions at its block and diff it:

    python3 tools/predict_next.py --check research/2026-10-08-flybook-predictions/data

To re-derive the population's accounts, sales and the OBRAIN price series (CS-008):

    python3 tools/verify_economy.py --check research/2026-10-08-flybook-economy/data
