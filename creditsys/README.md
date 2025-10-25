# CreditSystem

A comprehensive credit system for chat applications that allows users to purchase credits using ETH, USDC, or USDT, and claim free credits authorized by the contract owner.

## Features

- **Multi-token Support**: Purchase credits using ETH, USDC, or USDT
- **Dynamic Pricing**: Real-time price feeds via Chainlink oracles
- **Free Credits**: Owner-signed free credit claims with signature verification
- **Access Control**: Role-based permissions for different operations
- **Security**: ReentrancyGuard, Pausable, and comprehensive input validation
- **Modular Design**: Separated storage, interfaces, and logic for maintainability

## Architecture

The system follows a modular architecture inspired by SecondOrder.fun:

### Core Contracts

- **`src/core/CreditSystem.sol`**: Main contract implementing the credit system
- **`src/core/CreditStorage.sol`**: Storage contract containing all state variables
- **`src/core/ICreditSystem.sol`**: Interface defining the contract's public API

### Libraries

- **`src/lib/CreditTypes.sol`**: Structs and types used throughout the system
- **`src/lib/CreditLogic.sol`**: Utility functions for calculations and validations

### Scripts

- **`scripts/DeployCreditSystem.s.sol`**: Deployment script
- **`scripts/DepositCredits.s.sol`**: Script for depositing credits
- **`scripts/UseCredits.s.sol`**: Script for using credits

## Project Structure

```
creditsys/
├── src/
│   ├── core/
│   │   ├── CreditSystem.sol      # Main contract
│   │   ├── CreditStorage.sol     # Storage contract
│   │   └── ICreditSystem.sol     # Interface
│   └── lib/
│       ├── CreditTypes.sol       # Types and structs
│       └── CreditLogic.sol       # Utility functions
├── scripts/
│   ├── DeployCreditSystem.s.sol  # Deployment
│   ├── DepositCredits.s.sol      # Deposit script
│   └── UseCredits.s.sol          # Usage script
├── tests/
│   └── CreditSystem.t.sol        # Test suite
├── foundry.toml                  # Foundry configuration
└── README.md                     # This file
```

## Usage

### Setup

1. Install dependencies:
```bash
forge install OpenZeppelin/openzeppelin-contracts
forge install smartcontractkit/chainlink-brownie-contracts
```

2. Set environment variables:
```bash
export PRIVATE_KEY="your_private_key"
export USDC_ADDRESS="0x..."
export USDT_ADDRESS="0x..."
export WETH_ADDRESS="0x..."
export ETH_USD_FEED="0x..."
export USDC_USD_FEED="0x..."
export USDT_USD_FEED="0x..."
```

### Deployment

```bash
forge script scripts/DeployCreditSystem.s.sol --rpc-url $RPC_URL --broadcast
```

### Depositing Credits

#### Using USDC/USDT
```bash
export CREDIT_SYSTEM_ADDRESS="0x..."
export TOKEN_ADDRESS="0x..." # USDC or USDT address
export CREDITS_AMOUNT="100000000000000000000" # 100 credits

forge script scripts/DepositCredits.s.sol --rpc-url $RPC_URL --broadcast
```

#### Using ETH
```bash
export CREDIT_SYSTEM_ADDRESS="0x..."
export TOKEN_ADDRESS="0x0000000000000000000000000000000000000000" # ETH
export CREDITS_AMOUNT="100000000000000000000" # 100 credits

forge script scripts/DepositCredits.s.sol --rpc-url $RPC_URL --broadcast
```

### Using Credits

```bash
export CREDIT_SYSTEM_ADDRESS="0x..."
export CREDITS_TO_USE="10000000000000000000" # 10 credits
export USE_TYPE="1" # Chat usage
export ENTITY_ID="123" # Chat room ID

forge script scripts/UseCredits.s.sol --rpc-url $RPC_URL --broadcast
```

## API Reference

### Core Functions

#### `deposit(address token, uint256 creditsAmount)`
Purchase credits using USDC or USDT tokens.

#### `depositETH(uint256 creditsAmount)`
Purchase credits using ETH.

#### `useCredits(uint256 amount, uint256 useType, uint256 entityId)`
Spend credits for a specific purpose (e.g., chat, premium features).

#### `claimFree(uint256 amount, uint256 nonce, uint256 expiry, bytes signature)`
Claim free credits with owner authorization.

### View Functions

#### `getUserCredits(address user)`
Get user's current credit balance.

#### `getCurrentCreditPrice()`
Get current price of one credit in USD.

#### `getPriceInCurrencies(uint256 creditsAmount)`
Get the cost of credits in all supported currencies.

#### `getUserStats(address user)`
Get comprehensive user statistics.

### Admin Functions

#### `updateCreditPrice(uint256 newPriceUsd)`
Update the price of credits (admin only).

#### `withdraw(address token, uint256 amount)`
Withdraw tokens from the contract (admin only).

#### `pause()` / `unpause()`
Pause/unpause the contract (admin only).

## Security Features

- **Access Control**: Role-based permissions using OpenZeppelin's AccessControl
- **Reentrancy Protection**: ReentrancyGuard prevents reentrancy attacks
- **Pausable**: Contract can be paused in emergency situations
- **Price Feed Validation**: Comprehensive validation of Chainlink price feeds
- **Signature Verification**: ECDSA signature verification for free credit claims
- **Input Validation**: Extensive validation of all inputs

## Testing

Run the test suite:

```bash
forge test
```

Run specific tests:

```bash
forge test --match-test testDepositUSDC
forge test --match-test testUseCredits
```

## Gas Optimization

The contract is optimized for gas efficiency:

- **Storage Separation**: Storage variables separated into base contract
- **Library Usage**: Common logic moved to libraries
- **Efficient Calculations**: Optimized mathematical operations
- **Event Optimization**: Minimal event data for gas savings

## License

MIT License - see LICENSE file for details.

