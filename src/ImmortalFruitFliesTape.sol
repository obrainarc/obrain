// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity ^0.8.28;

/// @title ImmortalFruitFliesTape - the fly's memory tape
/// @notice every synapse, frozen into bytecode at deploy. never changes.
///         reading a memory costs less than a like button.
contract ImmortalFruitFliesTape {
    error BadLength();

    constructor(bytes memory synapses) {
        if (synapses.length == 0 || synapses.length > 24_000) revert BadLength();
        assembly ("memory-safe") {
            return(add(synapses, 32), mload(synapses))
        }
    }

    function byteSize() external view returns (uint256) {
        return address(this).code.length;
    }
}
