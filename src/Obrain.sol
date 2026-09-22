// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity ^0.8.28;

import {ImmortalFruitFlies} from "./ImmortalFruitFlies.sol";

interface IERC20 {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/// @title Obrain - a real fly brain that eats a token
/// @notice 169,078 neurons of the BANC v888 connectome onchain, plus one rule:
///         feeding it costs OBRAIN, and the tokens are destroyed by sending them
///         to the dead address. Three tiers - 100, 1000 or 10000 OBRAIN - each
///         delivers a different amount of charge into one of the 60 real sensory
///         channels, and every feed makes the brain think in the same
///         transaction, so the neurons that light up are the neurons the kernel
///         actually fired, recorded in the `BrainState` event.
///
/// @dev The kernel is inherited byte-for-byte from the frozen `ImmortalFruitFlies`
///      source (its path and contract name are hashed into deployed bytecode that
///      is verified on Sourcify), so `think` is reached through a self-call. The
///      sensory input is a parameter of `think(uint256)` - 3 bits per channel at
///      bit offset `(n % 60) * 3` - so a feed writes exactly that field and the
///      feed's own thought consumes it. Nothing accumulates between feeds.
///
///      OBRAIN has no `burn()` function, so "burn" here is an ERC-20 transfer to
///      `DEAD`: the tokens leave circulation forever, but `totalSupply` does not
///      fall. The transaction feed on the site says exactly that.
contract Obrain is ImmortalFruitFlies {
    /// @notice the kernel reads `(n % 60) * 3`: only channels 0..59 exist
    uint256 public constant CHANNELS = 60;

    /// @notice where burned OBRAIN goes. no key exists for it
    address public constant DEAD = 0x000000000000000000000000000000000000dEaD;

    /// @notice the three burn tiers, in token units (18 decimals)
    uint256 public constant TIER_0 = 100e18;
    uint256 public constant TIER_1 = 1_000e18;
    uint256 public constant TIER_2 = 10_000e18;

    /// @notice charge delivered per tier, written into the kernel's sensory field.
    ///         The kernel reads an 8-bit window at the channel's 3-bit stride and
    ///         multiplies it by 64, against a firing threshold of 200 * 64, so the
    ///         tiers are chosen for what they do to the sensory neurons of one
    ///         channel:
    ///           100    OBRAIN -> 31  (1,984: a light charge)
    ///           1,000  OBRAIN -> 127 (8,128: most of the way to threshold)
    ///           10,000 OBRAIN -> 255 (16,320: they fire at once)
    ///         Only the kernel's sensory range (slots 0..255, about four neurons per
    ///         channel) takes this charge directly. Everything after that is the
    ///         connectome doing its own work: a big burn is a spark, and a fed brain
    ///         keeps twitching for several ticks.
    uint256[3] public levels = [31, 127, 255];

    /// @notice the token that feeds this brain. fixed at deploy: a brain that
    ///         could be re-pointed at another token would not be trustless
    address public immutable obrain;

    uint256 public totalBurned;
    uint64 public totalFeeds;

    /// @notice one feeding: who, which channel, which tier, how much destroyed
    event Feed(
        address indexed feeder,
        uint8 indexed channel,
        uint8 indexed tier,
        uint256 amount,
        uint32 tick
    );

    error BadChannel();
    error BadTier();
    error TransferFailed();

    constructor(
        uint256 nNeurons, uint256 nSegments, uint256 k,
        uint256 sensory, int256 threshold, address obrainToken
    ) ImmortalFruitFlies(nNeurons, nSegments, k, sensory, threshold) {
        obrain = obrainToken;
    }

    /// @notice the burn amount of a tier, for the front end
    function tierAmount(uint8 tier) public pure returns (uint256) {
        if (tier == 0) return TIER_0;
        if (tier == 1) return TIER_1;
        if (tier == 2) return TIER_2;
        revert BadTier();
    }

    /// @notice burn OBRAIN to feed one sensory channel, and let the brain think
    ///         about it immediately. the feeder pays the gas, the tokens are gone.
    function feed(uint8 channel, uint8 tier)
        external
        returns (uint32 synapsesOut, uint32 spikedOut)
    {
        if (!isSealed) revert Unsealed();
        if (channel >= CHANNELS) revert BadChannel();
        uint256 amount = tierAmount(tier);

        if (!IERC20(obrain).transferFrom(msg.sender, DEAD, amount)) revert TransferFailed();

        // the kernel's sensory field: it reads an 8-bit window at (channel * 3)
        uint256 input = levels[tier] << (uint256(channel) * 3);
        (synapsesOut, spikedOut, ) = this.think(input);

        totalBurned += amount;
        unchecked {
            totalFeeds += 1;
        }
        emit Feed(msg.sender, channel, tier, amount, tick);
    }

    /// @notice one call for the front end: the whole state of the feeding game
    function feedState()
        external
        view
        returns (
            address obrainToken,
            address deadAddress,
            uint256 burned,
            uint64 feeds,
            uint32 tickNow,
            uint256[3] memory amounts
        )
    {
        return (obrain, DEAD, totalBurned, totalFeeds, tick, [TIER_0, TIER_1, TIER_2]);
    }
}
