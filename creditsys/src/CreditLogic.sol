// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

/**
 * @title CreditLogic
 * @notice Library containing utility functions for credit calculations and validations
 */
library CreditLogic {
    /**
     * @notice Calculate token amount needed for desired credits
     * @param creditsAmount Amount of credits to purchase
     * @param creditPriceUsd Price of one credit in USD (18 decimals)
     * @param tokenUsdPrice Token price in USD (8 decimals from Chainlink)
     * @param tokenDecimals Token decimals
     * @return uint256 Token amount needed
     */
    function calculateTokenAmount(
        uint256 creditsAmount,
        uint256 creditPriceUsd,
        uint256 tokenUsdPrice,
        uint8 tokenDecimals
    ) internal pure returns (uint256) {
        uint256 usdRequired = (creditsAmount * creditPriceUsd) / 1e18;
        uint256 tokenDecimalsFactor = 10 ** uint256(tokenDecimals);
        return (usdRequired * tokenDecimalsFactor * 1e8) / tokenUsdPrice;
    }

    /**
     * @notice Calculate ETH amount needed for desired credits
     * @param creditsAmount Amount of credits to purchase
     * @param creditPriceUsd Price of one credit in USD (18 decimals)
     * @param ethUsdPrice ETH price in USD (8 decimals from Chainlink)
     * @return uint256 ETH amount needed in wei
     */
    function calculateETHAmount(
        uint256 creditsAmount,
        uint256 creditPriceUsd,
        uint256 ethUsdPrice
    ) internal pure returns (uint256) {
        uint256 usdRequired = (creditsAmount * creditPriceUsd) / 1e18;
        return (usdRequired * 1e26) / ethUsdPrice;
    }

    /**
     * @notice Validate Chainlink price feed data
     * @param roundID Round ID from price feed
     * @param answer Price answer from feed
     * @param startedAt When the round started
     * @param updatedAt When the round was updated
     * @param answeredInRound Round in which the answer was computed
     */
    function validatePriceFeed(
        uint80 roundID,
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    ) internal view {
        require(answer > 0, "CreditLogic: invalid price");
        require(startedAt != 0 && startedAt <= updatedAt, "CreditLogic: invalid startedAt");
        require(updatedAt != 0 && updatedAt <= block.timestamp, "CreditLogic: invalid updatedAt");
        require(answeredInRound >= roundID, "CreditLogic: stale round");
        // require(block.timestamp - updatedAt < 1 hours, "CreditLogic: price too old");
    }
}
