// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "./CreditTypes.sol";
/**
 * @title CreditStorage
 * @notice Holds all storage variables, structs, and events for the CreditSystem contract.
 * @dev Separating storage into a base contract is a pattern to avoid contract size limits.
 */
abstract contract CreditStorage {

    // ===== IMMUTABLE ADDRESSES =====
    address public immutable USDC;
    address public immutable USDT;

    // ===== CHAINLINK PRICE FEEDS =====
    AggregatorV3Interface public immutable ethUsdFeed;
    AggregatorV3Interface public immutable usdcUsdFeed;
    AggregatorV3Interface public immutable usdtUsdFeed;
    
    mapping(address => CreditTypes.UserInfo) public users;

    // ===== PRICING =====
    uint256 public creditPriceUsd = 1e18; // 1 USD per credit
    uint256 public constant MIN_CREDIT_PRICE = 1e16; // 0.01 USD
    uint256 public constant MAX_CREDIT_PRICE = 10e18; // 10 USD

    // ===== EVENTS =====
    event CreditsDeposited(address indexed user, address indexed token, uint256 tokenAmount, uint256 creditsMinted, uint256 usdRate, uint256 timestamp);
    event CreditsDepositedETH(address indexed user, uint256 ethAmount, uint256 creditsMinted, uint256 ethUsdRate, uint256 timestamp);
    event FreeCreditsClaimed(address indexed user, uint256 amount, uint256 nonce, uint256 timestamp);
    event CreditsUsed(address indexed user, uint256 amount, uint256 useType, uint256 entityId, uint256 timestamp);
    event CreditPriceUpdated(uint256 oldPrice, uint256 newPrice, uint256 timestamp);
    event TokensWithdrawn(address indexed token, uint256 amount, uint256 timestamp);
    event UserNonceUpdated(address indexed user, uint256 newNonce, uint256 timestamp);
}
