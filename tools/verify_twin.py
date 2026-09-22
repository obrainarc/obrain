#!/usr/bin/env python3
"""Replay the on-chain brain locally, tick by tick, byte-exact.

Given the same poke inputs in order, prints per-tick synOps/spiked/stateRoot
to compare against on-chain receipts (BrainState event + stateRoot()).
Requires: numpy. Usage:

    python3 tools/verify_twin.py 123456789012345678 9876543210

The BrainState event only carries counts, so the fired neuron ids of a past
tick exist nowhere on chain. --fired prints them (plus the abi.encode(uint256[])
keccak commitment) for every tick; the counts must still match the event.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tapes import decode_tapes  # noqa: E402
from vbrain import VBrain  # noqa: E402


def fired_commitment(ids: list[int]) -> str:
    """keccak256(abi.encode(uint256[])) - what Solidity would hash."""
    from Crypto.Hash import keccak

    buf = (32).to_bytes(32, "big") + len(ids).to_bytes(32, "big")
    for n in ids:
        buf += n.to_bytes(32, "big")
    return keccak.new(digest_bits=256, data=buf).hexdigest()


def main() -> None:
    fired = "--fired" in sys.argv[1:]
    inputs = [int(x, 0) for x in sys.argv[1:] if x != "--fired"] or [1]
    s, q, w = decode_tapes(sorted(Path(__file__).resolve().parent.parent.glob("tapes/tape_*.bin")))
    vb = VBrain(s, q, w)
    for inp in inputs:
        o, sp, ids = vb.think(inp)
        ids = [int(x) for x in ids]
        line = f"tick={vb.tick} input={inp} synapses={o} spiked={sp} stateRoot=0x{vb.state_root():064x}"
        if fired:
            star = ids[0] if ids else None
            line += f" firedCount={len(ids)} starNeuron={star} firedHash=0x{fired_commitment(ids)}"
            line += " firedIds=" + ",".join(str(n) for n in ids)
        print(line)


if __name__ == "__main__":
    main()
