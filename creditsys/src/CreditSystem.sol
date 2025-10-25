// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "./CreditStorage.sol";
import "./ICreditSystem.sol";
import "./CreditLogic.sol";

/**
 * @title CreditSystem
 * @notice Allows users to buy "credits" using ETH, USDC, or USDT, and also
 *         claim free credits authorized by the contract owner (via signature).
 * @dev    Uses Chainlink price feeds (8 decimals), SafeERC20, and ReentrancyGuard.
 */
contract CreditSystem is CreditStorage, Ownable, ReentrancyGuard, Pausable, ICreditSystem {
    using SafeERC20 for IERC20;
    using ECDSA for bytes32;
    

    constructor(
        // address _USDC,
        // address _USDT,
        // address _ethUsdFeed,
        // address _usdcUsdFeed,
        // address _usdtUsdFeed
    ) Ownable(msg.sender) {
        // require(_USDC != address(0) && _USDT != address(0), "CreditSystem: invalid tokens");
        // require(_ethUsdFeed != address(0) && _usdcUsdFeed != address(0) && _usdtUsdFeed != address(0), "CreditSystem: invalid feeds");

        // USDC = _USDC;
        // USDT = _USDT;
        // ethUsdFeed = AggregatorV3Interface(_ethUsdFeed);
        // usdcUsdFeed = AggregatorV3Interface(_usdcUsdFeed);
        // usdtUsdFeed = AggregatorV3Interface(_usdtUsdFeed);

        USDC = 0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238;
        USDT = 0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238;
        ethUsdFeed = AggregatorV3Interface(0x694AA1769357215DE4FAC081bf1f309aDC325306);
        usdcUsdFeed = AggregatorV3Interface(0xA2F78ab2355fe2f984D808B5CeE7FD0A93D5270E);
        usdtUsdFeed = AggregatorV3Interface(0xA2F78ab2355fe2f984D808B5CeE7FD0A93D5270E);

    }

    // ===== DEPOSIT FUNCTIONS =====

    function deposit(address token, uint256 creditsAmount) external override nonReentrant whenNotPaused {
        require(creditsAmount > 0, "CreditSystem: credits must be > 0");
        require(token == USDC || token == USDT, "CreditSystem: unsupported token");

        AggregatorV3Interface feed = token == USDC ? usdcUsdFeed : usdtUsdFeed;
        uint256 tokenUsdPrice = _getLatestPrice(feed);

        uint8 decimals = IERC20Metadata(token).decimals();
        uint256 tokenAmount = CreditLogic.calculateTokenAmount(creditsAmount, creditPriceUsd, tokenUsdPrice, decimals);

        IERC20(token).safeTransferFrom(msg.sender, address(this), tokenAmount);

        users[msg.sender].credits += creditsAmount;

        emit CreditsDeposited(msg.sender, token, tokenAmount, creditsAmount, tokenUsdPrice, block.timestamp);
    }

    function depositETH(uint256 creditsAmount) external payable override nonReentrant whenNotPaused {
        require(creditsAmount > 0, "CreditSystem: credits must be > 0");

        uint256 ethUsdPrice = _getLatestPrice(ethUsdFeed);
        uint256 weiNeeded = CreditLogic.calculateETHAmount(creditsAmount, creditPriceUsd, ethUsdPrice);

        require(msg.value >= weiNeeded, "CreditSystem: not enough ETH");
        uint256 maxAllowed = weiNeeded + (weiNeeded / 100);
        require(msg.value <= maxAllowed, "CreditSystem: too much ETH sent");
        users[msg.sender].credits += creditsAmount;

        emit CreditsDepositedETH(msg.sender, weiNeeded, creditsAmount, ethUsdPrice, block.timestamp);
    }

    // ===== FREE CREDIT CLAIM =====

    function claimFree(
        uint256 amount,
        uint256 nonce,
        uint256 expiry,
        bytes calldata signature
    ) external override nonReentrant whenNotPaused {
        require(amount > 0, "CreditSystem: zero amount");
        if (expiry != 0) require(block.timestamp <= expiry, "CreditSystem: signature expired");
        require(nonce == users[msg.sender].nonce, "CreditSystem: invalid nonce");

        bytes32 message = keccak256(abi.encodePacked(msg.sender, amount, nonce, expiry, address(this)));
        bytes32 ethSigned = MessageHashUtils.toEthSignedMessageHash(message);
        address signer = ECDSA.recover(ethSigned, signature);
        require(signer == owner(), "CreditSystem: invalid signature");

        users[msg.sender].nonce += 1;
        users[msg.sender].credits += amount;

        emit FreeCreditsClaimed(msg.sender, amount, nonce, block.timestamp);
        emit UserNonceUpdated(msg.sender, users[msg.sender].nonce, block.timestamp);
    }

    // ===== CREDIT USAGE =====

    function useCredits(uint256 amount, uint256 useType, uint256 entityId) external override nonReentrant whenNotPaused {
        require(amount > 0, "CreditSystem: amount must be > 0");
        require(users[msg.sender].credits >= amount, "CreditSystem: insufficient credits");

        users[msg.sender].credits -= amount;

        emit CreditsUsed(msg.sender, amount, useType, entityId, block.timestamp);
    }

    // ===== ADMIN FUNCTIONS =====

    function updateCreditPrice(uint256 newPriceUsd) external onlyOwner {
        require(newPriceUsd >= MIN_CREDIT_PRICE && newPriceUsd <= MAX_CREDIT_PRICE, "CreditSystem: price out of range");
        uint256 oldPrice = creditPriceUsd;
        creditPriceUsd = newPriceUsd;
        emit CreditPriceUpdated(oldPrice, newPriceUsd, block.timestamp);
    }

    function withdraw(address token, uint256 amount) external onlyOwner nonReentrant {
        require(amount > 0, "CreditSystem: zero amount");
        if (token == address(0)) {
            (bool sent, ) = payable(owner()).call{value: amount}("");
            require(sent, "CreditSystem: ETH withdraw failed");
        } else {
            IERC20(token).safeTransfer(owner(), amount);
        }
        emit TokensWithdrawn(token, amount, block.timestamp);
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    // ===== VIEW FUNCTIONS =====

    function getUserCredits(address user) external view override returns (uint256) {
        return users[user].credits;
    }

    function getCurrentCreditPrice() external view returns (uint256) {
        return creditPriceUsd;
    }

    function getPriceInCurrencies(uint256 creditsAmount) external view returns (
        uint256 weiNeeded,
        uint256 usdcNeeded,
        uint256 usdtNeeded,
        uint256 usdRequired
    ) {
        require(creditsAmount > 0, "CreditSystem: credits must be > 0");

        usdRequired = (creditsAmount * creditPriceUsd) / 1e18;

        uint256 ethPrice = _getLatestPrice(ethUsdFeed);
        weiNeeded = CreditLogic.calculateETHAmount(creditsAmount, creditPriceUsd, ethPrice);

        uint256 usdcPrice = _getLatestPrice(usdcUsdFeed);
        uint8 usdcDecimals = IERC20Metadata(USDC).decimals();
        usdcNeeded = CreditLogic.calculateTokenAmount(creditsAmount, creditPriceUsd, usdcPrice, usdcDecimals);

        uint256 usdtPrice = _getLatestPrice(usdtUsdFeed);
        uint8 usdtDecimals = IERC20Metadata(USDT).decimals();
        usdtNeeded = CreditLogic.calculateTokenAmount(creditsAmount, creditPriceUsd, usdtPrice, usdtDecimals);
        return (weiNeeded, usdcNeeded, usdtNeeded, usdRequired);
    }

    // ===== INTERNAL FUNCTIONS =====

    function _getLatestPrice(AggregatorV3Interface feed) internal view returns (uint256) {
        (
            uint80 roundID,
            int256 answer,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = feed.latestRoundData();

        CreditLogic.validatePriceFeed(roundID, answer, startedAt, updatedAt, answeredInRound);
        return uint256(answer);
    }

    receive() external payable {}
}
