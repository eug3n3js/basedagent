from eth_account import Account
from eth_account.messages import encode_defunct
from exceptions.wallet_exceptions import WalletVerificationError


def verify_signature(wallet_address: str, message: str, signature: str) -> bool:
    try:
        wallet_address = wallet_address.lower()

        message_hash = encode_defunct(text=message)

        recovered_address = Account.recover_message(message_hash, signature=signature)
        recovered_address = recovered_address.lower()

        return recovered_address == wallet_address

    except Exception as e:
        raise WalletVerificationError(f"Failed to verify signature: {str(e)}")


def is_valid_ethereum_address(address: str) -> bool:
    try:
        if not address.startswith('0x') or len(address) != 42:
            return False

        hex_part = address[2:]
        int(hex_part, 16)
        return True
    except (ValueError, TypeError):
        return False
