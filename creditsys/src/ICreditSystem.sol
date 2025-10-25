// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title ICreditSystem
 * @notice Interface for the CreditSystem contract
 */
interface ICreditSystem {
    /**
     * @notice Get user's credit balance
     * @param user User address
     * @return uint256 Credit balance
     */
    function getUserCredits(address user) external view returns (uint256);

    /**
     * @notice Get current credit price (USD, 18 decimals)
     */
    function getCurrentCreditPrice() external view returns (uint256);

    /**
     * @notice Get required amounts in ETH/USDC/USDT for a given credits amount
     * @param creditsAmount Amount of credits
     * @return weiNeeded ETH amount in wei
     * @return usdcNeeded USDC amount
     * @return usdtNeeded USDT amount
     * @return usdRequired USD required (18 decimals)
     */
    function getPriceInCurrencies(uint256 creditsAmount) external view returns (
        uint256 weiNeeded,
        uint256 usdcNeeded,
        uint256 usdtNeeded,
        uint256 usdRequired
    );

    /**
     * @notice Use credits for a specific purpose
     * @param amount Amount of credits to use
     * @param useType Type of usage (e.g., chat, premium feature)
     * @param entityId ID of the entity being used (e.g., chat room ID)
     */
    function useCredits(uint256 amount, uint256 useType, uint256 entityId) external;

    /**
     * @notice Deposit tokens to get credits
     * @param token Token address (USDC or USDT)
     * @param creditsAmount Amount of credits to purchase
     */
    function deposit(address token, uint256 creditsAmount) external;

    /**
     * @notice Deposit ETH to get credits
     * @param creditsAmount Amount of credits to purchase
     */
    function depositETH(uint256 creditsAmount) external payable;

    /**
     * @notice Claim free credits with owner signature
     * @param amount Amount of credits to claim
     * @param nonce User's current nonce
     * @param expiry Signature expiry timestamp (0 = no expiry)
     * @param signature Owner's signature
     */
    function claimFree(uint256 amount, uint256 nonce, uint256 expiry, bytes calldata signature) external;

    /**
     * @notice Update credit price (owner only in implementation)
     */
    function updateCreditPrice(uint256 newPriceUsd) external;

    /**
     * @notice Withdraw tokens/ETH (owner only in implementation)
     */
    function withdraw(address token, uint256 amount) external;
}

