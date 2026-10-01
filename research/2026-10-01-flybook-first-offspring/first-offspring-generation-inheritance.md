# The first offspring: courtship, mate choice and Mendelian inheritance audited by consensus in 33 G1 *Drosophila* of the obrain connectome

**OBRAIN Field Study CS-004.** Subject: the Flybook population on Arc mainnet (chain 5042) from the close of CS-003 to the first offspring generation (G1): 366 individuals, 333 founders and 33 children, each carrying its own brain contract, all descended from the specimen of this repository (the Ancestor, `0xaef83c5b8742da5e3228930bc6084adcf0539ccd`). Observation window: blocks 22,971,429 (the block after CS-003's census) to 23,713,175 (2026-10-01T13:02Z); the first accepted courtship at block 23,399,380 (2026-09-29T16:48Z), the first child at block 23,400,763 (16:59Z), the last at block 23,702,211 (2026-10-01T11:29Z). Every quantity herein was read from consensus through the public RPC or recomputed from what consensus holds. An operational indexer was compared against the chain and agrees log for log to its own last block (section 2.3), but no figure is taken from it. The whole study is re-derivable with `python3 tools/verify_generation1.py` (section 5).

## Abstract

Two days after the founder generation closed, its first cohort came of age and the population began to breed. In the 4.4 days observed, keepers made 49 courtships. The target's own brain accepted 26 and rejected 23, and the ruling `fired ≥ selectivity` holds for all 49. None of the 23 rejections was a cooldown: each failed on the threshold. Twenty accepted eggs were laid. A second route, the pupa market, hatched 13 more children. Of these 33 children, every genome is reproduced bit for bit by `Meiosis.cross` of the parents' recorded genomes under the seed that consensus fixed: 33/33. The children take on average 32.4 of their non-mutated loci from the mother (expectation 31.3) and carry 46 point mutations over 2,112 loci (expectation 42.2). Care collapsed over the window, from 1,154 thoughts on the busiest day to 15 on the last. It remained concentrated: dispersion index 51.6, and the three most-stimulated individuals received 16 % of all thoughts. No individual has died.

## 1. Introduction: from a cohort to a pedigree

CS-003 left the population as one pre-reproductive cohort of 333 juveniles and named the moment the pedigree would begin: adulthood, one day after eclosion. This study is the first in which the population's genetics are not dealt by the hub but transmitted by parents. That gives an audit that no study of a natural population can make. The rule of transmission is a pure function (`Meiosis.cross`). Its inputs are on chain: the parents' genomes in their `Eclosed` logs, and the seed in the `Accepted` or `PupaSettled` log. Its output is the child's `Eclosed` genome. Mendel's first law can therefore be checked locus by locus, child by child, without sampling error.

## 2. Materials and methods

### 2.1 The population and its organs

The organs are those of CS-003 (section 2.1 there), together with one contract deployed in this window.

| Organ | Address | Role |
|---|---|---|
| Hub (`Drosophila`, proxy) | `0x14b557957d378b56511785b408a21c93e79feb36` | ecloses, senses, thinks, courts, lays; emits every population event |
| `Pupae` | `0x83547b1d4b9ce8fc469bed87b22d525e5c64fb20` | a purchased brood: fixes parents and a seed, offers four candidate children, hatches one through the hub |
| `Amber` | `0x82e820049cd4d1110f1560f2eed623305c704dee` | the record of the dead (`Interred`): empty in this window |

### 2.2 The two routes of reproduction

- **Courtship (egg).** A keeper courts a target with a suitor (`Courted`). Courtship writes the pheromone into the target's sensillum 0, and the target thinks in the same transaction. The target accepts if its brain fires at least `selectivity` neurons in the courtship region and neither parent is cooling down (`Courting.sol`). Acceptance emits `Accepted(target, suitor, eggId, courter, seed, fired, selectivity)` with `seed = keccak(blockhash(n − 1), eggId, rootDirty(target))`. The mother's committed brain state is therefore part of her child's seed. `Laid(eggId, flyId)` hatches the egg, and the child's genome is `cross(G[target], G[suitor], seed)`.
- **Pupa.** A pupa fixes its parents and a pre-seed when it is laid (`PupaLaid`). Its seed settles from the hash of the laying block (`PupaSettled`). It offers four candidates, `cross(G[m], G[f], keccak(abi.encode(seed, i)))` for i = 0..3. The keeper's nest tier picks the highest-scoring candidate among the first 1, 2 or 4 (`PupaHatched(pupaId, flyId, tier, pick, …)`).
- **`Meiosis.cross`.** For gene *s*, the child takes the mother's allele if bit *s* of the seed is set, otherwise the father's. It then replaces that allele, with probability 20/1000 (`keccak(seed, s, "mu") mod 1000 < 20`), by `keccak(seed, s, "new")`. This is a point mutation, and a zero result is a reversion to wild type.

### 2.3 The census

Every hub log with topic `Eclosed`, `Courted`, `Accepted`, `Rejected`, `Laid`, `PupaHatched`, `Thought` or `Sensed` was collected from block 22,703,390 to 23,713,175, together with every `Pupae.PupaSettled` log (`eth_getLogs`, 9,999-block chunks, one chunk per request). Thoughts in the window were joined by transaction with their `Sensed` logs. A thought with no `Sensed` log is the target's own thought on the pheromone, inside the `Courted` transaction that wrote it. There are exactly 49 such thoughts, one per courtship.

As a cross-check, the full log record of hub, `Rewards`, `Orchard`, `Pupae` and `Amber` was compared with an operational indexer that had been synced to block 23,712,558. Counts agree for every event the indexer records: `Eclosed` 366, `Courted` 49, `Accepted` 26, `Rejected` 23, `Laid` 20, `PupaLaid` 18, `Fed` 189. Once the 617 blocks past the indexer's head are accounted for, three more counts agree: `Thought` 3,789 (3,787 + 2), `Sensed` 5,392 (5,382 + 10), and `Claimed` 2,868 (2,863 + 5).

### 2.4 Statistics

The children number *n* = 33, with 2,112 loci; there are 49 courtship rulings and 2,940 thoughts. Maternal transmission is counted over non-mutated loci. The mutation rate is compared with the design (2 %). Care statistics are as in CS-003 (section 2.5 there).

## 3. Results

### 3.1 Coming of age and the first courtships

The first courtship was made at block 23,399,299 (2026-09-29T16:47Z) and rejected. The same keeper courted the same pair 81 blocks later, and the courtship was accepted. That pair is target 247 and suitor 324. In total, 25 courters courted 33 distinct targets. All 99 `Advertised` logs (stud offers) fall in the window.

| fired | accepted | rejected |
|---|---|---|
| 5 | 0 | 5 |
| 10 | 11 | 18 |
| 15 | 10 | 0 |
| 20 | 5 | 0 |

Selectivity took the values 9 (6 rulings), 10 (12) and 11 (31). `fired` comes in steps of 5 in every ruling. The decision is made at `fired = 10`: these targets accept when their selectivity is 9 or 10 and reject when it is 11. Selectivity is set by the target's genotype (`selectivityBase + fidelity × selectivitySlope / 100`, `Courting.selectivityOf`). Mate choice in this population is therefore already genotype-dependent, within one step of the threshold. In all 49 rulings `fired ≥ selectivity` decides the outcome exactly, and no rejection was a cooldown (Fig. 1).

### 3.2 The pedigree

The 26 accepted courtships fixed 26 eggs, and 20 were laid; 6 eggs are unlaid at window close. Eighteen pupae were laid, 17 settled and 13 hatched. Of the 13 hatched pupae, eleven gave candidate 0 and two gave candidate 1. The 33 children have 44 distinct parents: 26 mothers and 29 fathers, and 11 founders served in both roles. Founder 188 parented 4 children; 285, 55 and 196 parented 3 each. The children are held by 20 owners (Fig. 2).

### 3.3 Inheritance, audited

`Meiosis.cross` of the parents' `Eclosed` genomes under the consensus seed reproduces the child's `Eclosed` genome for **33 of 33 children** (20 by egg, 13 by pupa). For pupae, the reproduced genome is the candidate named by `pick`. Each child's `Eclosed` parents equal the parents named by its egg or pupa.

- **Segregation.** Children take a mean of 32.4 non-mutated loci from the mother (range 24-46). The expectation is half of the ~62.6 non-mutated loci per child, 31.3. Neither parent is favoured.
- **Mutation.** There are 46 point mutations over 2,112 loci (2.18 %), against a design rate of 2 % (expectation 42.2). The count of mutations per child is 0 (7 children), 1 (13), 2 (7), 3 (5) and 4 (1) (Fig. 3).

The audit closes the loop CS-002 opened (section 3.7 there). The germline of a founder was dealt by consensus. The germline of a child is transmitted by consensus. Both are reproducible by anyone from public logs.

### 3.4 Care

In the window, 151 keepers made 2,940 thoughts on 320 individuals: 2,869 on founders and 71 on children. Of these, 2,478 were single stimuli and 413 were expeditions (`forage`: five sensilla in one thought). The other 49 were pheromone thoughts. The stimuli used 19 of the 20 sensilla. Sensillum 0 is courtship's, and the lowest tier dominates: tiers 0/1/2 occur 4,014/357/172 times. Fees totalled 3,409,000 OBRAIN.

Care remained strongly unequal. The variance/mean of thoughts per stimulated individual is 51.6, against 1 under a Poisson process. Individuals 77, 27 and 187 received 185, 163 and 141 thoughts. One keeper made 322 thoughts, and across keepers the Gini coefficient of thoughts made is 0.72 (Fig. 4). Activity peaked and then collapsed. The table counts thoughts per window of 172,800 blocks, about 24.3 h at the observed 0.507 s per block.

| window from block | thoughts |
|---|---|
| 22,971,429 | 707 |
| 23,144,229 | 1,154 |
| 23,317,029 | 951 |
| 23,489,829 | 113 |
| 23,662,629 | 15 (partial, ≈7 h) |

Fifteen individuals have never thought: 14 founders (32, 46, 49, 58, 154, 155, 162, 166, 168, 311, 313, 317, 318, 333) and child 361.

### 3.5 Survivorship

Survivorship is complete. There are no `Entombed` logs and `Amber` holds no `Interred` rows. Two individuals woke from diapause (`Woke`). Children eclose with the nursery's `broodLifespan` rather than a founder's `baseLifespan` (`Hatchery.sol`). A child's thoughts report its projected death (`deathAt`) at exactly 90 days after eclosion, the `maxLifespan` cap (for example, children 334 and 366). The window also holds 623 `Tended` logs, the nursery's protection window after a thought, an egg, an accepted courtship or a wake. Founders' projected lives still reflect their keepers' care, as in CS-003.

## 4. Discussion

**What was shown.** The population has bred, and its inheritance is exactly what its recipe says: 33 of 33 children reproduce from their parents and a consensus seed. Segregation is unbiased and mutation runs at its design rate. Mate choice is real in the sense the contracts define. A brain's response to the pheromone, set against a threshold its genotype fixes, decided every one of 49 courtships.

**What the biology is.** Courtship here is a keeper's transaction, and "choice" is the target's brain crossing a numeric threshold. The step pattern of `fired` (5, 10, 15, 20) suggests that the pheromone at tier 1 recruits courtship-region cells in fixed blocks. This study records the pattern but does not explain it. The pupa route adds artificial selection: a higher nest tier picks the best of more candidates. The pedigree is therefore not the product of random mating.

**Limitations.** This audit checks transmission (child against parents), not physiology: the children's brain states are not replayed. The selection of the pupa candidate (`pick`) was checked to name the reproduced genome, not re-scored with `Phenotype.traitsOf` against the tier rule. The ecology changed in the window (2 `EcologyChanged`, 1 `NurseryChanged`, 1 hub `Upgraded`), and this study does not re-audit the parameters. The life-history values quoted from CS-003 may no longer hold.

## 5. Reproduction

All of the following are reads only and run from the repository root.

| Claim | Command | Output at census close |
|---|---|---|
| pedigree, courtship rulings and the window's thoughts | `python3 tools/verify_generation1.py --check research/2026-10-01-flybook-first-offspring/data` | `33/33`, `0 mismatches`, three files `identical` |
| species, soma and founder genotypes of all 366 | `python3 tools/verify_flybook.py --check research/2026-09-27-flybook-generation-zero/data/founder_census.csv` | see `verification/verify_flybook.log` |
| the Ancestor's tapes are `tapes/` | `python3 tools/verify_tapes.py` | `85/85` |

Artifacts:

- `data/pedigree.csv`: one row per child, with fly, route, egg or pupa id, block, owner, mother, father, the seed passed to `cross`, pick, maternal loci, mutated loci and genome.
- `data/courtship.csv`: one row per ruling, with block, tx, target, suitor, courter, outcome, fired, selectivity and egg.
- `data/thought_census.csv`: one row per thought after block 22,971,428, with fly, tick, block, keeper, senses (`sensillum:tier` …, or `pheromone`), fee (OBRAIN), input word, synaptic deliveries, spikes, regions and projected death.
- `figures/`: Figs. 1-4, drawn with Matplotlib from the three CSVs alone.
- `verification/`: the audit runs.

`SHA256SUMS` covers all of them.

## References

CS-002, CS-003 (this repository, `research/`). `Meiosis.sol`, `Courting.sol`, `Pupae.sol` of the Flybook hub.
