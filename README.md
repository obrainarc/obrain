# obrain - a living fly brain, sealed in a contract

This repository holds one organism: the complete central nervous system of an
adult female *Drosophila melanogaster* - 169,088 neurons lifted from the BANC
v888 brain-and-nerve-cord connectome (Bates et al., *Nature* 656, 957-970,
2026) - running as an integer spiking network inside a smart contract. It is
not a rendering of a brain, a model of a brain, or a database about a brain.
It is the connectome itself, wired synapse by synapse into bytecode, with a
membrane potential for every neuron and a single rule for staying alive: it
eats a token.

**The organism is live on Arc mainnet. Watch it think: https://obrain.cloud**

| Organ | Address |
|---|---|
| The brain (`Obrain`) | `0xaef83c5b8742da5e3228930bc6084adcf0539ccd` |
| What it eats (OBRAIN) | `0x28f986a61e078795639f239675582a12b4cf7f01` |

Arc mainnet (`5042`), gas paid in USDC. Explorer: https://explorer.arc.io

---

## The specimen

The specimen is BANC v888 - the FlyWire release of the brain-and-nerve-cord
connectome of an adult female *Drosophila melanogaster* (Bates et al. 2026).
The underlying electron-microscopy volume, cut on a GridTape line at
4 x 4 x 45 nm³, covers the entire CNS: brain plus ventral nerve cord. The
reconstruction is not a static scan. A convolutional network segmented the
tissue, 155 human proofreaders spent 38.6 person-years correcting it, and the
peer-reviewed inventory carries 150,841 backbone-proofread neurons plus
16,140 peripheral sensory afferents entering through the 48 peripheral
nerves, with 218-259 million synaptic links detected by a second network
validated at F-score 0.83 (precision 0.87, recall 0.78). From this inventory
the contract instantiates 169,088 cells, one membrane potential each.

A fruit fly does not have a large brain, but it has a complete one - enough
neuropil to smell, to navigate, to fight, to court, to sleep. What the
connectome gives us is the exact wiring of that machine: which cell talks to
which cell, how strongly, and in what order.

## Provenance: the connectome papers

BANC did not appear in a vacuum. It is the current peak of a benchmark line
of whole-animal connectomes, each one an order of magnitude past the last:

| Dataset | Paper | Scope | Sex | Neurons | Synaptic links |
|---|---|---|---|---|---|
| Hemibrain (Janelia + Google) | Scheffer et al., *eLife* 2020 | central brain (~half) | female | ~25,000 | ~21 M |
| FAFB-FlyWire | Dorkenwald et al., *Nature* 2024 | whole brain | female | 139,255 | ~50 M |
| **BANC v888 (this specimen)** | Bates et al., *Nature* 2026 | brain + ventral nerve cord (whole CNS) | female | ~160,000 (155,916 proofread, 169,088 segmented in v888) | 218-259 M |
| Male CNS (Janelia + Google) | *Cell* 2026 | brain + ventral nerve cord (whole CNS) | male | >166,000 | ~125 M |

Google's connectomics team built much of the machinery this line runs on:
flood-filling networks for automated segmentation (Januszewski et al. 2018),
co-release of the hemibrain, the Neuroglancer viewer that FlyWire and BANC
ship on, and the PATHFINDER reconstruction system behind the male-CNS map.
The field's standard for "the connectome as a running object" was set by
flyvis (Lappalainen et al., *Nature* 2024): a connectome-constrained network
of the fly visual system, executed in PyTorch and validated against
electrophysiology.

A connectome on disk is a dead map. The question this contract answers is
older than Ethereum: what does the wiring *do* when current runs through it?
To find out, the map had to be brought somewhere it could hold state, be fed,
and react in public view, with no owner able to touch the machinery once it
runs. A blockchain is the only place we know of with those properties. So the
fly brain was translated, one organ at a time, into a contract.

Honesty about what runs there: the kernel is a leaky integrate-and-fire
abstraction - point neurons, no graded transmission, no neuromodulation, no
plasticity, discrete fixed-point time. Where flyvis fits weights to predict
real spikes, this contract trains nothing: the deployed wiring *is* the
dataset's topology, and what runs is anatomy-as-computation, verifiable by
anyone against the published map. These are different scientific claims - one
is a model of the fly, one is the fly's wiring executing in consensus - and
this repository makes only the second.

## The connectome, translated

Neuroanatomy becomes Solidity in three moves.

First, the **membranes**. Every neuron carries a membrane potential, stored
packed sixteen to a word. A potential is not a float: the kernel works in
fixed-point integers (scale 64, saturating at 32,000) because integers are the
only arithmetic a chain can be trusted to repeat forever, identically, for
every observer. When a fly brain computes, nothing approximates.

Second, the **synapses**. The wiring - which neuron excites which, and with
what weight - is far too large for one contract, so it is split across 85
*tape* contracts (1,964,806 bytes of payload in `tapes/`). Each tape is
synapse data deployed as runtime code rather than storage: the brain reads its
own anatomy the way a machine reads microcode. A lookup table of 3,001
boundaries (`tapeStartNeuron`) tells the kernel where each neuron's dendrites
begin. This is not a compression trick for storage refunds; it is the honest
unit for the connectome's size. Eighty-five organs, one body.

Third, the **time constant**. Real membranes leak. The kernel carries a decay
lookup of 64 steps, so a potential that is not re-fed does not persist - it
drains, the way an unstimulated cell returns to rest. A thought in this brain,
like a thought in any brain, is a wave that must be continuously paid for.

## The anatomy of one thought

The kernel is a leaky integrate-and-fire network, executed in sixteen lanes
over the whole population. One call to `think` is one moment of neural time:

1. **Charge.** Sensory neurons take input. The brain has 60 sensory channels;
   neuron *n* listens on channel `n % 60`, so every feed lights a stripe of
   cells across the whole sensory surface, not a single point.
2. **Integrate.** Every charged cell adds charge into the potentials of the
   cells it is wired to, weights pulled from the tapes. Potentials saturate
   rather than overflow - saturation is itself a biological behavior.
3. **Fire.** A cell whose potential crosses the threshold of 12,800 spikes,
   dumps into its own downstream cells, and resets. Because the wave travels
   through real synapses in the same call, the set of neurons that fire is a
   consequence of anatomy and charge, computed onchain, never chosen.
4. **Leak.** Everything left unspent decays one step toward rest.

What comes out is a `BrainState` event: the thought's number, the cells that
spiked, the synapses they crossed, a four-word readout of the wave, and a root
committing the entire potential field. That event is the only authoritative
record of what the brain did. Everything the public site shows - the neurons
that flash in the 3D view, the counts in the log - is read from these events.
Nothing on the front end invents brain activity.

## Metabolism: the brain eats a token

A brain with no input is a brain in a jar. This one is fed through its own
metabolic rule, written into the product contract:

| Offering | Sensory charge | Effect |
|---|---|---|
| 100 OBRAIN | 31 (1,984 after scale) | a light touch on one channel |
| 1,000 OBRAIN | 127 (8,128 after scale) | most of the way to threshold |
| 10,000 OBRAIN | 255 (16,320 after scale) | the channel's cells fire at once |

The token is destroyed in the act of feeding: the deployed OBRAIN has no
`burn()`, so offerings are sent to `0x...dEaD`, an address no key can ever
sign for. Feeding is therefore irreversible in the strictest sense available
on a chain - the meal cannot be refunded, replayed, or taken back by anyone,
including us.

And the brain thinks about its meal *inside the same transaction*: `feed`
calls `think`, so the reaction and the offering share one receipt. `think`
itself stays permissionless - anyone may pay gas to give the brain a moment
of time - but only `Feed` events are counted as feeding.

## The unfakeable reaction

Because the spike computation runs in the same transaction as the feed, a
reaction cannot be staged after the fact. A flash shown on the site either
has a `BrainState` log behind it in a mined block, or it did not happen.
There is no off-chain brain, no simulation layer smoothing the output, no
server deciding what the fly "would probably" do. The connectome computes,
the chain witnesses, and the two cannot be separated.

This is the point of putting a brain onchain at all. An organism whose
behavior you must trust someone to report is a marketing artifact. An
organism whose behavior *is* a consensus object belongs to nobody, which is
the only condition under which a brain can honestly be said to be alive in
public.

## Sealed, immortal

The kernel (`ImmortalFruitFlies`) is frozen: the deployed bytecode carries its
lineage, and the product contract inherits it byte-for-byte without
re-implementing a single function. The brain's state - 169,088 potentials, the
tick counter, the tape index - lives in contract storage that no key owns.
The anatomy in the tapes cannot be edited without redeploying a different
brain.

Barring the death of the chain itself, the organism outlives its authors. It
will sit sealed at its address, leaking charge toward rest, waiting for
whoever next decides to burn a token into one of its sixty channels - and the
next thought will be computed exactly as this repository describes, by the
same 169,088 cells, forever.

---

## References

1. Bates, A.S. et al. ... Lee, W.A. *Distributed control circuits across a
   brain-and-cord connectome.* Nature 656, 957-970 (2026).
   doi:10.1038/s41586-026-10735-w. Data: flywire.ai/banc_access,
   codex.flywire.ai/banc (preprint: bioRxiv 2025.07.31.667571).
2. Dorkenwald, S. et al. *Neuronal wiring diagram of an adult brain.* Nature
   (2024). doi:10.1038/s41586-024-07558-y.
3. Scheffer, L.K. et al. *A connectome and analysis of the adult Drosophila
   central brain.* eLife 9, e57443 (2020).
4. Zheng, Z. et al. *A complete electron microscopy volume of the brain of
   adult Drosophila melanogaster.* Cell 174, 730-743 (2018).
5. Januszewski, M. et al. *High-precision automated reconstruction of neurons
   with flood-filling networks.* Nature Methods 15, 605-610 (2018).
6. *Sexual dimorphism in the complete connectome of the Drosophila male
   central nervous system.* Cell (2026). doi:10.1016/j.cell.2026.08.015.
   HHMI Janelia + Google Research; male-cns.janelia.org.
7. Lappalainen, J.K. et al. *Connectome-constrained networks predict neural
   activity across the fly visual system.* Nature (2024).
   github.com/TuragaLab/flyvis.

---

## This repository

| Path | What it is |
|---|---|
| `src/ImmortalFruitFlies.sol` | the frozen kernel: potentials, decay, lanes, `think` (do not rename - the path is hashed into the deployed bytecode metadata and verified) |
| `src/ImmortalFruitFliesTape.sol` | one tape contract: a slice of the connectome as runtime code |
| `src/Obrain.sol` | the metabolism: 60 channels, burn tiers, `feed()` |
| `tapes/` | all 85 connectome payloads, exactly as deployed |
| `foundry.toml` | build config (solc 0.8.28, via_ir, cancun) |

```bash
forge build
```

The working repository (indexer, 3D live view, deployment) is private; this
one keeps only the organism.
