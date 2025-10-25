// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title CreditTypes
 * @notice Library containing all structs and types used in the credit system
 */
library CreditTypes {
    /**
     * @notice Information about a user credit info
     */
    struct UserInfo {
        uint256 credits;  // credits amount 
        uint256 nonce;  // user nonce
    }

}


