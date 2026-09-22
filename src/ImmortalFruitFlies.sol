// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity ^0.8.28;

/// @title ImmortalFruitFlies - a real fly brain onchain
/// @notice 169,078 neurons from the BANC v888 female connectome (Bates/Phelps/Kim
///         et al., Nature 2026), running as LIF dynamics with a 64-segment
///         gated scan. not AI - just a fly.
contract ImmortalFruitFlies {
    uint256 public N_NEURONS;
    uint256 public N_WORDS;
    uint256 public N_SEGMENTS;
    uint256 public K;
    uint256 public WORDS_PER_SEGMENT;
    uint256 public SENSORY;
    uint256 public TAPES_COUNT;
    int256 public threshold;
    int256 public constant QMAX = 32000;
    int256 public constant SCALE = 64;
    uint256 public constant LANES = 16;

    int256[11000] public potentials;
    uint32[21_200] public lastActive;
    uint32 public tick;
    int256[64] public decayLUT;
    uint64[256] public gateTable;
    address[3000] public tapes;
    int256[3001] public tapeStartNeuron;

    uint256 public constant MAX_WORDS = 11_000;
    uint256 public constant MAX_LT = 21_200;
    uint256 public constant LT_WORDS = 2_650;
    uint256 public constant MAX_TAPES = 3_000;
    uint256 public constant SPIKE_CAP = 2_048;

    address public owner;
    bool public isSealed;
    bytes32 public configHash;
    uint256 public rootDirty;

    /// @notice identifies the kernel version and seeds stateFold / rootDirty
    bytes32 public constant FOLD_SEED = keccak256("ImmortalFruitFlies v2");

    bytes32 public accGates;
    bytes32 public accTapes;
    bytes32 public accDecay;

    event BrainState(
        uint32 indexed t,
        int256 p0,
        int256 p1,
        int256 p2,
        int256 p3,
        uint32 synapses,
        uint32 spiked,
        bool capped,
        bytes32 root,
        bytes32 poke,
        bytes fired
    );
    error BadTape();
    error BadRange();
    error BadCount();
    error Sealed();
    error Unsealed();
    error ConfigPending();
    error NotOwner();

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    constructor(
        uint256 nNeurons, uint256 nSegments, uint256 k,
        uint256 sensory, int256 threshold
    ) {
        require(nNeurons % 16 == 0 && nNeurons <= MAX_WORDS * 16, "N");
        require(nSegments > 0 && k >= 1 && k <= nSegments, "K");
        N_NEURONS = nNeurons;
        N_WORDS = nNeurons / 16;
        N_SEGMENTS = nSegments;
        K = k;
        SENSORY = sensory;
        WORDS_PER_SEGMENT = (N_WORDS + nSegments - 1) / nSegments;
        threshold = threshold;
        owner = msg.sender;
        rootDirty = uint256(FOLD_SEED);
    }

    uint256 public constant P_SLOT = 8;
    uint256 public constant LT_SLOT = 11008;

    function _foldState() internal view returns (uint256 acc) {
        acc = uint256(FOLD_SEED);
        unchecked {
            for (uint256 s = 0; s < N_WORDS; ++s) {
                acc += uint256(keccak256(abi.encode(P_SLOT + s, potentials[s])));
            }
            for (uint256 s = 0; s < LT_WORDS; ++s) {
                acc += uint256(keccak256(abi.encode(LT_SLOT + s, _ltWord(s))));
            }
        }
    }

    function stateFold() external view returns (uint256) {
        return _foldState();
    }

    /// @notice bulk state reads: a handful of eth_calls instead of ~10.5k storage reads
    function potentialsRange(uint256 from, uint256 to) external view returns (uint256[] memory out) {
        if (to <= from || to - from > 1_024 || to > N_WORDS) revert BadRange();
        out = new uint256[](to - from);
        for (uint256 s = from; s < to; ++s) out[s - from] = uint256(potentials[s]);
    }

    /// @notice one uint32 per potential word: the tick that word was last processed at
    function lastActiveRange(uint256 from, uint256 to) external view returns (uint256[] memory out) {
        if (to <= from || to - from > 1_024 || to > MAX_LT) revert BadRange();
        out = new uint256[](to - from);
        for (uint256 j = from; j < to; ++j) out[j - from] = uint256(lastActive[j]);
    }

    function precomputeConfigHash() external onlyOwner {
        if (isSealed) revert Sealed();
        configHash = keccak256(abi.encodePacked(accGates, accTapes, accDecay, threshold));
    }

    uint256 public foldProgress;

    function _ltWord(uint256 j) internal view returns (uint256 v) {
        unchecked {
            for (uint8 k = 0; k < 8; ++k) {
                v |= uint256(lastActive[j * 8 + k]) << (k * 32);
            }
        }
    }

    function foldSumChunk(uint256 from, uint256 to) external onlyOwner {
        if (isSealed) revert Sealed();
        require(to <= N_WORDS + LT_WORDS && from < to && from == foldProgress, "fold range");
        uint256 acc = rootDirty;
        unchecked {
            for (uint256 i = from; i < to; ++i) {
                uint256 h;
                if (i < N_WORDS) {
                    h = uint256(keccak256(abi.encode(P_SLOT + i, uint256(potentials[i]))));
                } else {
                    uint256 j = i - N_WORDS;
                    h = uint256(keccak256(abi.encode(LT_SLOT + j, _ltWord(j))));
                }
                acc += h;
            }
        }
        rootDirty = acc;
        foldProgress = to;
    }

    function sealBrain() external onlyOwner {
        if (isSealed) revert Sealed();
        if (configHash == bytes32(0)) revert ConfigPending();
        require(foldProgress == N_WORDS + LT_WORDS, "fold incomplete");
        isSealed = true;
    }

    function setDecayLUT(int256[] memory lut) external onlyOwner {
        if (isSealed) revert Sealed();
        for (uint256 i = 0; i < lut.length && i < 64; ++i) decayLUT[i] = lut[i];
        accDecay = keccak256(abi.encodePacked(accDecay, keccak256(abi.encode(lut))));
    }
    function setGates(uint256 firstBucket, uint64[] memory gates) external onlyOwner {
        if (isSealed) revert Sealed();
        for (uint256 i = 0; i < gates.length; ++i) gateTable[firstBucket + i] = gates[i];
        accGates = keccak256(abi.encodePacked(accGates, firstBucket, keccak256(abi.encode(gates))));
    }
    function setTape(uint256 idx, address b, int256 startNeuron) external onlyOwner {
        if (isSealed) revert Sealed();
        if (b.code.length == 0 || b.code.length > 24_000) revert BadTape();
        if (idx > MAX_TAPES) revert BadCount();
        tapes[idx] = b;
        tapeStartNeuron[idx] = startNeuron;
        accTapes = keccak256(abi.encodePacked(accTapes, idx, b, startNeuron));
    }
    function finalizeTapes(uint256 count) external onlyOwner {
        if (isSealed) revert Sealed();
        require(count <= MAX_TAPES && count > 0, "count");
        tapeStartNeuron[count] = int256(uint256(N_NEURONS));
        // every tape must cover exactly the range assigned to it. If a payload
        // holds fewer neurons than its range, think() would index past the tape's
        // offset table, read record bytes as offsets and loop on an underflowed
        // record count - a misconfiguration that would brick the sealed brain.
        if (tapeStartNeuron[0] != 0) revert BadTape();
        bytes memory two = new bytes(2);
        for (uint256 i = 0; i < count; i++) {
            if (tapeStartNeuron[i + 1] <= tapeStartNeuron[i]) revert BadTape();
            address tape = tapes[i];
            assembly ("memory-safe") {
                extcodecopy(tape, add(two, 32), 0, 2)
            }
            uint256 covered = (uint256(uint8(two[0])) << 8 | uint256(uint8(two[1]))) / 2 - 1;
            if (uint256(tapeStartNeuron[i + 1] - tapeStartNeuron[i]) != covered) revert BadTape();
        }
        TAPES_COUNT = count;
    }
    function setThreshold(int256 t) external onlyOwner {
        if (isSealed) revert Sealed();
        threshold = t;
    }
    function seedPotentials(int256[] memory p) external onlyOwner {
        if (isSealed) revert Sealed();
        for (uint256 s = 0; s < p.length && s < N_WORDS; ++s) potentials[s] = p[s];
    }

    function stateRoot() external view returns (bytes32) {
        bytes32 h = keccak256(abi.encode(tick));
        for (uint256 s = 0; s < N_WORDS; ++s) h = keccak256(abi.encodePacked(h, potentials[s]));
        return h;
    }

    function findTape(uint256 n) public view returns (uint256 b, uint256 g0) {
        uint256 lo = 0;
        uint256 hi = TAPES_COUNT;
        while (lo < hi) {
            uint256 mid = (lo + hi) >> 1;
            if (uint256(tapeStartNeuron[mid]) < n) { lo = mid + 1; } else { hi = mid; }
        }
        if (lo < TAPES_COUNT && uint256(tapeStartNeuron[lo]) == n) {
            b = lo;
            g0 = n;
        } else {
            b = lo - 1;
            g0 = uint256(tapeStartNeuron[lo - 1]);
        }
    }

    function think(uint256 inputAgg)
        external
        returns (uint32 synapsesOut, uint32 spikedOut, uint256[] memory firedIdsOut)
    {
        if (!isSealed) revert Unsealed();
        uint256[SPIKE_CAP] memory fires;
        uint32 t_;
        int256 po0;
        int256 po1;
        int256 po2;
        int256 po3;
        uint256 nF;
        assembly ("memory-safe") {
            t_ := add(sload(tick.slot), 1)
            sstore(tick.slot, t_)
            let TH := sload(threshold.slot)
            let NW := sload(N_WORDS.slot)
            let NN := sload(N_NEURONS.slot)
            let nExp := sload(N_SEGMENTS.slot)
            let wpe := sload(WORDS_PER_SEGMENT.slot)
            let sensoryN := sload(SENSORY.slot)
            let nTapes := sload(TAPES_COUNT.slot)
            let Kcfg := sload(K.slot)

            let mirror := mload(0x40)
            let loaded := add(mirror, mul(NW, 32))
            let dirty := add(loaded, mul(shr(3, add(NW, 255)), 32))
            let scratch := add(dirty, mul(shr(3, add(NW, 255)), 32))
            let rootScr := add(scratch, 512)
            mstore(0x40, add(add(rootScr, 128), 31))
            let fb := fires
            let r := sload(rootDirty.slot)
            nF := 0

            let bucket := mod(inputAgg, nExp)
            let gateWord := sload(add(gateTable.slot, shr(2, bucket)))
            let gate := and(shr(mul(and(bucket, 3), 64), gateWord), 0xFFFFFFFFFFFFFFFF)
            let synapses := 0
            let spiked := 0

            {
                let nEnd := sensoryN
                for { let w := 0 } lt(w, shr(4, add(nEnd, 15))) { w := add(w, 1) } {
                    if lt(w, NW) {
                        let wslot := add(potentials.slot, w)
                        let lw2 := add(loaded, mul(shr(8, w), 32))
                        let v := sload(wslot)
                        if and(shr(and(w, 255), mload(lw2)), 1) { v := mload(add(mirror, mul(w, 32))) }
                        for { let L := 0 } lt(L, 16) { L := add(L, 1) } {
                            let n := add(mul(w, 16), L)
                            if lt(n, nEnd) {
                                let sh := mul(L, 16)
                                let lane := signextend(1, shr(sh, v))
                                let addv := mul(and(shr(mul(mod(n, 60), 3), inputAgg), 0xFF), 64)
                                let c := add(lane, addv)
                                if sgt(c, QMAX) { c := QMAX }
                                v := or(and(v, not(shl(sh, 0xFFFF))), and(shl(sh, c), shl(sh, 0xFFFF)))
                            }
                        }
                        mstore(add(mirror, mul(w, 32)), v)
                        mstore(lw2, or(mload(lw2), shl(and(w, 255), 1)))
                        let dw2 := add(dirty, mul(shr(8, w), 32))
                        mstore(dw2, or(mload(dw2), shl(and(w, 255), 1)))
                        sstore(wslot, v)
                        mstore(rootScr, r)
                        mstore(add(rootScr, 32), wslot)
                        mstore(add(rootScr, 64), v)
                        r := keccak256(rootScr, 96)
                    }
                }
            }

            for { let i := 0 } lt(i, Kcfg) { i := add(i, 1) } {
                let e := and(shr(mul(i, 8), gate), 255)
                let baseWord := mul(e, wpe)
                let lastWord := add(baseWord, wpe)
                if gt(lastWord, NW) { lastWord := NW }
                let curWordSlot := 0
                let lwNew := 0

                for { let w := baseWord } lt(w, lastWord) { w := add(w, 1) } {
                    let wordSlot := add(lastActive.slot, shr(3, w))
                    if iszero(eq(wordSlot, curWordSlot)) {
                        if curWordSlot {
                            mstore(rootScr, r)
                            mstore(add(rootScr, 32), curWordSlot)
                            mstore(add(rootScr, 64), lwNew)
                            r := keccak256(rootScr, 96)
                            sstore(curWordSlot, lwNew)
                        }
                        curWordSlot := wordSlot
                        lwNew := sload(wordSlot)
                    }
                    let wslot := add(potentials.slot, w)
                    let lw := and(shr(mul(and(w, 7), 32), lwNew), 0xFFFFFFFF)
                    let wv := sload(wslot)
                    let loadedBit := and(shr(and(w, 255), mload(add(loaded, mul(shr(8, w), 32)))), 1)
                    let v := wv
                    if loadedBit { v := mload(add(mirror, mul(w, 32))) }

                    let dt := sub(t_, lw)
                    if dt {
                        let m := 0
                        switch lt(dt, 65)
                        case 1 { m := sload(add(decayLUT.slot, sub(dt, 1))) }
                        default {
                            m := sload(decayLUT.slot)
                            let rem := sub(dt, 1)
                            for { } gt(rem, 0) { } {
                                let step := rem
                                if gt(step, 64) { step := 64 }
                                let mk := sload(add(decayLUT.slot, sub(step, 1)))
                                m := sar(16, add(mul(m, mk), 32768))
                                rem := sub(rem, step)
                            }
                        }
                        let out := 0
                        for { let L := 0 } lt(L, 16) { L := add(L, 1) } {
                            let sh := mul(L, 16)
                            let x := signextend(1, shr(sh, v))
                            if x {
                                x := sar(16, add(mul(x, m), 32768))
                                out := or(out, and(shl(sh, x), shl(sh, 0xFFFF)))
                            }
                        }
                        v := out
                        mstore(add(mirror, mul(w, 32)), v)
                        let lw1 := add(loaded, mul(shr(8, w), 32))
                        mstore(lw1, or(mload(lw1), shl(and(w, 255), 1)))
                        let dw1 := add(dirty, mul(shr(8, w), 32))
                        mstore(dw1, or(mload(dw1), shl(and(w, 255), 1)))

                        for { let L := 0 } lt(L, 16) { L := add(L, 1) } {
                            let sh := mul(L, 16)
                            let pv := signextend(1, shr(sh, v))
                            if iszero(slt(pv, TH)) {
                                let n := add(mul(w, 16), L)
                                // every crossing is counted and delivered; only the
                                // emitted id list is capped at SPIKE_CAP
                                spiked := add(spiked, 1)
                                if lt(nF, SPIKE_CAP) {
                                    mstore(add(fb, mul(nF, 32)), n)
                                    nF := add(nF, 1)
                                }
                                let bn := n
                                    let blo := 0
                                    let bhi := nTapes
                                    for { } lt(blo, bhi) { } {
                                        let mid := shr(1, add(blo, bhi))
                                        let svv := sload(add(tapeStartNeuron.slot, mid))
                                        switch lt(svv, bn)
                                        case 1 { blo := add(mid, 1) }
                                        default { bhi := mid }
                                    }
                                    let tapeIdx := sub(blo, 1)
                                    let g0 := sload(add(tapeStartNeuron.slot, tapeIdx))
                                    if and(lt(blo, nTapes), eq(sload(add(tapeStartNeuron.slot, blo)), bn)) {
                                        tapeIdx := blo
                                        g0 := bn
                                    }
                                    let cont := 1
                                    for { } cont { } {
                                        cont := 0
                                        let tape := sload(add(tapes.slot, tapeIdx))
                                        let j := sub(n, g0)
                                        extcodecopy(tape, scratch, shl(1, j), 4)
                                        let off0 := or(shl(8, byte(0, mload(scratch))), byte(1, mload(scratch)))
                                        let off1 := or(shl(8, byte(2, mload(scratch))), byte(3, mload(scratch)))
                                        let len := sub(off1, off0)
                                        extcodecopy(tape, scratch, off0, len)

                                    for { let p := 0 } lt(p, len) { p := add(p, 5) } {
                                        let rp := add(scratch, p)
                                        let p32 := mload(rp)
                                        let tgt := add(shl(16, byte(0, p32)), or(shl(8, byte(1, p32)), byte(2, p32)))
                                        let wt := signextend(1, or(shl(8, byte(3, p32)), byte(4, p32)))
                                        if wt {
                                            if lt(tgt, NN) {
                                                synapses := add(synapses, 1)
                                                let tword := shr(4, tgt)
                                                let tp := add(mirror, mul(tword, 32))
                                                let lw3 := add(loaded, mul(shr(8, tword), 32))
                                                if iszero(and(shr(and(tword, 255), mload(lw3)), 1)) {
                                                    mstore(tp, sload(add(potentials.slot, tword)))
                                                    mstore(lw3, or(mload(lw3), shl(and(tword, 255), 1)))
                                                }
                                                let sbit := mul(and(tgt, 15), 16)
                                                let x := mload(tp)
                                                let lane := signextend(1, shr(sbit, x))
                                                let c := add(lane, wt)
                                                if sgt(c, QMAX) { c := QMAX }
                                                if slt(c, sub(0, QMAX)) { c := sub(0, QMAX) }
                                                mstore(tp, or(and(x, not(shl(sbit, 0xFFFF))), and(shl(sbit, c), shl(sbit, 0xFFFF))))
                                                let dw2 := add(dirty, mul(shr(8, tword), 32))
                                                mstore(dw2, or(mload(dw2), shl(and(tword, 255), 1)))
                                            }
                                        }
                                        let nextIdx := add(tapeIdx, 1)
                                        if and(lt(nextIdx, nTapes), eq(sload(add(tapeStartNeuron.slot, nextIdx)), n)) {
                                            tapeIdx := nextIdx
                                            g0 := n
                                            cont := 1
                                        }
                                    }
                                    }
                                let mp2 := add(mirror, mul(w, 32))
                                mstore(mp2, and(mload(mp2), not(shl(sh, 0xFFFF))))
                            }
                        }
                    }
                    let sh2 := mul(and(w, 7), 32)
                    lwNew := or(and(lwNew, not(shl(sh2, 0xFFFFFFFF))), shl(sh2, t_))
                }
                if curWordSlot {
                    mstore(rootScr, r)
                    mstore(add(rootScr, 32), curWordSlot)
                    mstore(add(rootScr, 64), lwNew)
                    r := keccak256(rootScr, 96)
                    sstore(curWordSlot, lwNew)
                }
            }

            let bwCount := shr(8, add(NW, 255))
            for { let w := 0 } lt(w, bwCount) { w := add(w, 1) } {
                let bm := mload(add(dirty, mul(w, 32)))
                if bm {
                    for { let b := 0 } lt(b, 256) { b := add(b, 1) } {
                        if and(shr(b, bm), 1) {
                            let word := add(mul(w, 256), b)
                            if lt(word, NW) {
                                let wslot2 := add(potentials.slot, word)
                                let nv := mload(add(mirror, mul(word, 32)))
                                sstore(wslot2, nv)
                                mstore(rootScr, r)
                                mstore(add(rootScr, 32), wslot2)
                                mstore(add(rootScr, 64), nv)
                                r := keccak256(rootScr, 96)
                            }
                        }
                    }
                }
            }

            sstore(rootDirty.slot, r)

            let x0 := sload(potentials.slot)
            if and(mload(loaded), 1) { x0 := mload(mirror) }
            po0 := signextend(1, and(x0, 0xFFFF))
            po1 := signextend(1, and(shr(16, x0), 0xFFFF))
            po2 := signextend(1, and(shr(32, x0), 0xFFFF))
            po3 := signextend(1, and(shr(48, x0), 0xFFFF))

            synapsesOut := synapses
            spikedOut := spiked
        }
        firedIdsOut = new uint256[](nF);
        bytes memory fired = new bytes(nF * 3);
        for (uint256 i = 0; i < nF; ++i) {
            firedIdsOut[i] = fires[i];
            fired[i * 3] = bytes1(uint8(fires[i] >> 16));
            fired[i * 3 + 1] = bytes1(uint8(fires[i] >> 8));
            fired[i * 3 + 2] = bytes1(uint8(fires[i]));
        }
        emit BrainState(
            t_, po0, po1, po2, po3, synapsesOut, spikedOut, spikedOut > SPIKE_CAP, bytes32(rootDirty), bytes32(inputAgg), fired
        );
    }
}
