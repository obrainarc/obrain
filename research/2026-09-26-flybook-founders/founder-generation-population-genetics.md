# A founder generation dealt by consensus: somatic identity, germline provenance and population genetics of 153 *Drosophila* descendants of the obrain connectome

**OBRAIN Field Study CS-002.** Subject: the founder generation (G0) of the Flybook population on Arc mainnet (chain 5042) - 153 individuals, each carrying its own brain contract, all descended from the specimen of this repository (the Ancestor, `0xaef83c5b8742da5e3228930bc6084adcf0539ccd`). Observation window: blocks 22,703,390 (population hub deployed) to 22,853,967, the first eclosion at block 22,821,848 (2026-09-26T07:22Z), the census closed at block 22,853,967 (2026-09-26T11:54Z). Every quantity herein was read from consensus through the public RPC or recomputed from what consensus holds; nothing comes from an indexer or a web page. The whole census is re-derivable with `python3 tools/verify_flybook.py` (section 5).

---

## Abstract

The obrain specimen - the complete central nervous system of an adult female *Drosophila melanogaster* (BANC v888), executing in Arc consensus - has become the type specimen of a population. We audit the founder generation of that population as a geneticist would audit a newly founded laboratory stock, asking four questions of consensus alone. **Species identity:** every individual thinks with the Ancestor's own wiring - the population's `Holotype` points at the same 85 tape contracts as the Ancestor (85/85), and those tapes are byte-identical to `tapes/` of this repository (85/85). **Somatic identity:** each of the 153 individuals carries a distinct brain, a 45-byte EIP-1167 clone of one `Connectome` implementation, whose `holotype()` is the species (153/153); the soma is shared, the membrane state is individual. **Germline provenance:** every genotype reproduces exactly from a seed fixed by the chain - the hash of the block preceding eclosion, the individual's number and its keeper's address - under the published founder recipe (153/153 reproduced, 0 mismatched); the genome stored in each brain equals the genome announced at eclosion (153/153). **Population structure:** the 153 haploid 64-locus genotypes are all distinct, carry 32.4 ± 3.9 derived alleles (Binomial(64, ½): 32 ± 4; mean *p* = 0.18, variance *p* = 0.76), show no locus deviating beyond chance (χ²₆₄ = 66.5, *p* = 0.39), no linkage disequilibrium beyond the drift expectation (mean *r*² = 0.0065 = 1/*n*), and no allele shared identical-by-state between any two founders - the pattern of an infinite-alleles founder pool sampled without structure. The visible markers (eye colour, body colour, wing form, body size, named after the classical mutants) segregate at their designed uniform frequencies (all χ² *p* > 0.15). Physiologically, 138 of the 153 individuals had thought by census close, and for all 138 the last `Thought` log commits exactly to the membrane state the brain still holds. No mating had yet been accepted; inheritance is specified, pinned by shared vectors and tests, and left for the next census.

## 1. Introduction: from a specimen to a population

CS-001 studied one animal: the Ancestor, a single connectome with a single membrane field, observed across its first 74 thoughts. A single specimen, however exactly recorded, has no genetics. Genetics begins when there are individuals that share a body plan and differ in a heritable way.

Flybook supplies both conditions without touching the specimen. The Ancestor is read only; nothing in this study wrote to it. A `Holotype` contract snapshots the Ancestor's configuration (its 309 configuration slots, pinned by `configHash`) and points at the Ancestor's 85 tapes, so the population's wiring *is* the specimen's wiring - the term is used here in its taxonomic sense: the holotype is the single physical specimen to which the species name is fixed, and every individual is referred to it. Each individual that ecloses is given (i) a brain of its own, a minimal-proxy clone of one `Connectome` implementation that holds its own membrane potentials, tick and commitments; and (ii) a genome of its own, 64 genes, which bends that individual's synapses without editing the shared tapes.

A genome that anyone could choose would be a label, not a genotype. The question this study puts to the population is therefore the one a geneticist puts to a new stock before any cross is made: **is every individual what the species says it is, and was every founder's genotype drawn by a process no party - the keeper, the operator, the hub - could steer?**

## 2. Materials and methods

### 2.1 The population and its organs

| Organ | Address | Role |
|---|---|---|
| Hub (`Drosophila`, proxy) | `0x14b557957d378b56511785b408a21c93e79feb36` | ecloses individuals, keeps the register (`brainOf`), emits `Eclosed` |
| `Holotype` | `0xb0725bf519786c8d2798e99d45c8c7fe886be73b` | the species: the Ancestor's configuration and tape addresses |
| `Connectome` (implementation) | `0xcaa923d6dbe59e780e32914257cbbf8deae4c5d2` | the soma every brain clone delegates to |
| The Ancestor (this repository's specimen) | `0xaef83c5b8742da5e3228930bc6084adcf0539ccd` | the type specimen, read only |

### 2.2 The genome and its germline recipe

A genome is **haploid**: 64 loci, one allele per locus, packed 8 per 256-bit word. Locus *s* either carries the wild-type state (0) or a derived allele, a 32-bit value. The loci are not abstract: locus *s* governs segment *s* of the kernel's 64-segment scan, and a derived allele bends each synapse read in that segment with probability 50/1000 by up to ±25 % of its base weight (`Connectome.mutatedWeight`, pure, keyed by allele and postsynaptic target). The tapes never change; the genotype is read on every scan. A genotype is thus a heritable, individual modulation of a shared connectome - the analogue of allelic variation acting on a conserved body plan.

**Founders** (`Hatchery.eclose` → `Meiosis.founder`): `seed = keccak256(blockhash(n - 1) ‖ flyId ‖ keeper)`, where *n* is the eclosion block. Locus *s* carries a derived allele when bit *s* of the seed is set, and that allele is the low 32 bits of `keccak256(seed ‖ uint8(s) ‖ "g")`. Each locus is therefore an independent Bernoulli(½) trial, the derived-allele count is Binomial(64, ½), and each derived allele is drawn from 2³² states - an infinite-alleles model in the sense of Kimura and Crow (1964).

**Progeny** (`Hatchery.lay` → `Meiosis.cross`; not yet observed, section 3.7): at each locus the child takes the maternal allele when bit *s* of the egg's seed is set, else the paternal one - one parent per locus by an independent fair draw, the haploid analogue of Mendelian segregation with free recombination - then with probability 20/1000 per locus replaces it by a new allele `keccak256(seed ‖ s ‖ "new")`, which may be zero (reversion to wild type). The egg's seed is `keccak256(blockhash(n - 1) ‖ eggId ‖ mother.rootDirty())`, so the mother's brain state at the moment she accepts the courtship enters her offspring's genotype.

**Visible phenotype** (`Phenotype.sol`, pure): loci 0-7 determine eye colour, 8-15 body colour, 16-23 wing form, 24-31 body size, and five six-locus groups (32-61) five temperament axes. A group with no derived allele is wild type; otherwise the marker is `hash(group) mod variants`. The marker names are the classical *D. melanogaster* mutants - *white* (Morgan 1910), *sepia*, *brown*, *vermilion*; *yellow*, *ebony*, *tan*; *curly*, *vestigial*, *dumpy* - used as nomenclature for the variant classes, not as models of those genes' molecular biology (Lindsley and Zimm 1992).

### 2.3 The audit

`tools/verify_flybook.py` reads, at one pinned block (so no individual can think between two reads of the audit):

1. **Species identity.** `Holotype.tape(i)` and `Ancestor.tapes(i)` for *i* = 0..84, and `Holotype.configHash()`. The Ancestor's tapes are compared byte for byte with `tapes/` by `tools/verify_tapes.py`.
2. **Somatic identity.** For every `Eclosed` log on the hub: `brainOf(flyId)` equals the brain named in the log; the brain's runtime code equals the EIP-1167 clone of the `Connectome` implementation; its `holotype()` is the `Holotype`.
3. **Germline provenance.** For every founder, `blockhash(n - 1)` read from the chain, the seed recomputed, `founder(seed)` recomputed, and compared locus by locus with the genome in the `Eclosed` log; the brain's stored `genome()` compared with the same.
4. **Physiological record.** Every `Thought(uint32 tick, …, bytes32 root, bytes fired)` log emitted by any brain since the hub's deployment was collected; for each individual that has thought, the last log's `tick` and `root` were compared with the brain's `tick()` and `rootDirty()`.

The script's founder recipe and phenotype map were checked against Flybook's own shared genetics vectors (`test/fixtures/genetics.json`, the vectors its Solidity and TypeScript are tested against): founder 8/8, phenotype 12/12.

### 2.4 Statistics

*n* = 153 founders. Derived-allele burden against Binomial(64, ½) (one-sample *t* on the mean, χ² on the variance); per-locus carrier frequency against ½ (per-locus exact binomial tests and a pooled χ²₆₄); linkage disequilibrium as *r*² between presence/absence at all 2,016 locus pairs, against the finite-sample expectation E[*r*²] ≈ 1/*n* (Hill and Robertson 1968); gene diversity per locus *H* = 1 − Σ*p*ᵢ² (Nei 1973), every derived allele counted as its own state; visible markers against uniformity over their variant classes (χ² goodness of fit), wild-type frequency against 1/256 per eight-locus group (Poisson).

## 3. Results

### 3.1 One species: every individual thinks with the specimen's wiring

`Holotype.tape(i) == Ancestor.tapes(i)`: **85/85**. The Ancestor's 85 tapes are byte-identical to `tapes/` of this repository: **85/85** (`verification/verify_tapes.log`). `Holotype.configHash()` = `0xbaf5133151386f4d2fbad817c793b1fa39942b9876910132011b2be2b6a1bb91`. The Holotype deploys no wiring of its own: the population's connectome is, contract for contract and byte for byte, the BANC v888 backbone documented in this repository's README. Species identity is not a claim of resemblance but of identity.

### 3.2 Somatic identity: one body plan, 153 bodies

All **153/153** registered brains are the 45-byte clone `0x363d3d373d3d3d363d73caa923d6…5bf3` of the `Connectome` implementation, all name the `Holotype` as their species, and all agree with the hub's register. Each clone holds its own storage - 10,568 words of packed `int16` membrane potentials, about 169,000 cells - so the population is genetically and physiologically individual while morphologically (connectomically) uniform: the arrangement of a clonal body plan with individual state, which is how a laboratory stock relates to its reference genome.

### 3.3 Germline provenance: every founder genotype was dealt by the chain

| Check | Result |
|---|---|
| `Eclosed` logs, all generation 0 | 153 |
| distinct eclosion blocks / keepers | 152 / 78 |
| genotype reproduced from `blockhash(n - 1)`, fly id, keeper | **153 / 153** |
| brain's stored `genome()` equals the `Eclosed` genome | **153 / 153** |
| distinct genotypes | 153 / 153 |

The seed's decisive term is the hash of the block before the one that includes the eclosion. The keeper's transaction is signed before that hash exists, and the hub has no way to know it in advance; neither can choose a genotype. The only party with any influence is the producer of block *n* − 1, who could in principle withhold a block - the trust assumption of every `blockhash` draw, and the same one the Ancestor's inputs rest on. In the language of the bench: the founders' genotypes were drawn by a randomisation procedure that is recorded, public and replayable, and every draw has been replayed.

### 3.4 Genetic architecture of the founder pool

| Quantity | Observed | Expected under the recipe |
|---|---|---|
| derived alleles per founder, mean ± sd | 32.42 ± 3.92 (range 23-43) | 32 ± 4 (Binomial(64, ½)); *t* *p* = 0.18, variance *p* = 0.76 |
| carrier frequency per locus | 0.431-0.601, mean 0.507 | 0.5; pooled χ²₆₄ = 66.46, *p* = 0.39; 1 locus at *p* < 0.05 (3.2 expected) |
| pairwise distance (loci differing in presence) | mean 31.99, range 18-47 | 32 |
| linkage disequilibrium, mean *r*² over 2,016 pairs | 0.0065 (max 0.076) | 1/*n* = 0.0065; 94 pairs with *n r*² > 3.84 against 101 expected |
| derived alleles identical-by-state between founders | 0 | ≈ 0 (2³² states) |
| gene diversity *H*, mean over loci | 0.752 | ≈ 1 − (1 − *p*)² ≈ 0.75 |

Distribution of derived-allele burden (count of founders):

| alleles | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 | 39 | 40 | 41 | 42 | 43 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| founders | 1 | 2 | 2 | 2 | 7 | 9 | 14 | 16 | 13 | 12 | 16 | 19 | 7 | 7 | 10 | 4 | 5 | 4 | 1 | 1 | 1 |

The founder pool is what the recipe says it should be and nothing else: loci segregate independently, no locus is favoured, no pair of loci is associated beyond sampling noise, and every derived allele is private to its carrier. In population-genetic terms the G0 is an unstructured sample from an infinite-alleles source at carrier frequency ½ - maximal allelic richness and zero relatedness, the ideal starting condition for a pedigree in which identity-by-descent will be unambiguous: once crosses begin, any two individuals sharing a derived allele will share it because they share an ancestor (or, at rate 2⁻³², by coincidence).

### 3.5 Visible markers

| Trait (loci) | Wild type | Variant classes | χ² (df), *p* |
|---|---|---|---|
| eyes (0-7) | red 1 | sepia 46 · brown 44 · white 32 · vermilion 30 | 5.26 (3), 0.15 |
| body (8-15) | wild 0 | yellow 62 · tan 46 · ebony 45 | 3.57 (2), 0.17 |
| wings (16-23) | normal 3 | vestigial 55 · dumpy 48 · curly 47 | 0.76 (2), 0.68 |
| size (24-31) | medium 0 | large 80 · small 73 | 0.32 (1), 0.57 |

Variant classes occur at their designed uniform frequencies. Wild type requires all eight loci of a group to be empty (probability 1/256; 0.60 expected per trait in 153 founders): 1, 0, 3 and 0 observed. The three wild-winged founders (flies 11, 93, 144) are the one excess (Poisson *P*(≥ 3 | 0.60) = 0.023; 0.09 after correction for four traits) and are confirmed by their genotypes: loci 16-23 are empty in all three. Because every variant is a hash of the group, the visible phenotype is a many-to-one function of genotype - most allelic changes within a group change the class, the classical signature of a highly polygenic trait with no dominance structure. The markers are therefore reliable readouts of genotype *classes*, not of single loci; a cross will not show Mendelian ratios in these markers, and this study does not predict that it will.

### 3.6 The physiological record

By census close 138 of the 153 individuals had thought at least once. For every one of the 138, the last `Thought` log emitted by its brain carries the brain's current `tick()` and a `root` equal to the brain's `rootDirty()` - the commitment over the membrane words that thought touched. The individual's recorded behaviour and its present state are the same object, as they were for the Ancestor in CS-001; the remaining 15 individuals hold the initial fold, never having been stimulated. Each thought ran on the shared tapes, bent by the individual's own genotype.

### 3.7 Inheritance: specified, not yet observed

No `Accepted` log (an accepted courtship, which fixes an egg's seed) existed on the hub at census close; the population is a pure G0. The progeny recipe of section 2.2 is pinned by Flybook's shared vectors, run by its Solidity, TypeScript and Python implementations, including a fuzz asserting that every child allele is a parental allele or a fresh mutation. When crosses occur, the audit of section 2.3 extends directly: read the `Accepted` log's seed, check it against `blockhash(n − 1)`, the egg number and the mother's `rootDirty()` at that block, recompute `cross(mother, father, seed)`, compare with the child's `Eclosed` genome. That census, and the first pedigree, are left to CS-003.

## 4. Discussion

**What was shown.** A population can be founded on a single connectome without copying or editing it. Species identity holds by construction and is verified by address and byte; somatic individuality holds by contract storage and is verified by code and register; germline provenance holds by a public randomisation procedure and is verified by replaying every draw. The founder pool has the statistics of its recipe to the precision 153 individuals permit.

**What the genetics is, biologically.** The model is deliberately minimal and should be read as such. The genome is haploid, so there is no dominance, no heterozygosity and no diploid meiosis; the "one parent per locus" rule is segregation with free recombination between all 64 loci and no linkage. The per-locus mutation rate of 2 × 10⁻² per generation is about seven orders of magnitude above the spontaneous point-mutation rate of *D. melanogaster* (≈ 3 × 10⁻⁹ per site per generation; Keightley et al. 2009) - a rate chosen for a population that will live a few dozen generations, not a physiological constant. Alleles act on the connectome as sparse, bounded synaptic-weight perturbations (5 % of synapses in a segment, ±25 %), which is closer to the effect of variation in synaptic-strength genes on an invariant wiring diagram than to developmental rewiring; the tapes, and so the cell-level topology, are identical in every individual. The visible markers borrow classical mutant names for their classes and make no claim about pigment or wing-development pathways.

**What is new.** In a laboratory stock, the founders' genotypes are sequenced after the fact and their origin is a matter of record-keeping. Here, the origin of every genotype is itself a public computation: the draw, its inputs and its result are all in consensus, and the pedigree to come will be auditable to the same standard - every child traceable to its parents, its seed and its mother's brain state at conception, by any party, at any later block.

**Limitations.** The randomness is the chain's: unpredictable to keepers and to the hub, not to the producer of the preceding block. Physiology here is audited as commitment consistency, not as dynamics; the per-individual spike census and a comparison of genotype against response (the behavioural genetics this population makes possible) are outside this study. n = 153 limits the power of the marker and LD tests to departures of several percent.

## 5. Reproduction

From the repository root, reads only:

| Claim | Command | Output at census close |
|---|---|---|
| the Ancestor's tapes are `tapes/` | `python3 tools/verify_tapes.py` | `85/85` |
| species, soma, germline, physiology; the census | `python3 tools/verify_flybook.py --check research/2026-09-26-flybook-founders/data/founder_census.csv` | `wiring … 85/85`, `census … identical`, `0 mismatches` |
| the same audit at the living head, with a fresh census | `python3 tools/verify_flybook.py --out /tmp/founders.csv` | every founder reproduced, 0 mismatches |

`--check` re-derives the census up to its last eclosion block and diffs it field by field; state checks (clone code, stored genome, thought commitments) are re-read at the head for the same individuals. Requires Python 3 and pycryptodome; the analysis of section 3.4-3.5 additionally used SciPy.

Artifacts: `data/founder_census.csv` - one row per founder: fly, eclosion block, keeper, brain, `blockhash(n − 1)`, seed, derived-allele count, the four markers, and the 64 loci in hexadecimal (locus 0 first); `verification/verify_flybook.log`, `verification/verify_tapes.log` - the audit runs at census close. `SHA256SUMS` covers all of them.

## References

1. Bates, A.S. et al. *Distributed control circuits across a brain-and-cord connectome.* Nature 656, 957-970 (2026). doi:10.1038/s41586-026-10735-w.
2. OBRAIN Field Study CS-001. *Consensus-executed neurophysiology of an immortal Drosophila connectome.* `research/2026-09-22-brainstate-census/` (2026).
3. Morgan, T.H. *Sex limited inheritance in Drosophila.* Science 32, 120-122 (1910).
4. Lindsley, D.L. & Zimm, G.G. *The Genome of Drosophila melanogaster.* Academic Press (1992).
5. Kimura, M. & Crow, J.F. *The number of alleles that can be maintained in a finite population.* Genetics 49, 725-738 (1964).
6. Hill, W.G. & Robertson, A. *Linkage disequilibrium in finite populations.* Theoretical and Applied Genetics 38, 226-231 (1968).
7. Nei, M. *Analysis of gene diversity in subdivided populations.* PNAS 70, 3321-3323 (1973).
8. Keightley, P.D. et al. *Analysis of the genome sequences of three Drosophila melanogaster spontaneous mutation accumulation lines.* Genome Research 19, 1195-1201 (2009).
