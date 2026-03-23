import os, requests
import nacl

PUBLIC_KEY          = os.environ["DISCORD_PUBLIC_KEY"]
DISCORD_API_BASE    = "https://discord.com/api/v10"

def verify_key(body: bytes, sig: str, timestamp: str, public_key: str) -> bool:
    """Return True if the Ed25519 signature is valid for the given body."""
    try:
        verify_key = nacl.signing.VerifyKey(bytes.fromhex(public_key))
        verify_key.verify(f"{timestamp}".encode() + body, bytes.fromhex(sig))
        return True
    except (nacl.exceptions.BadSignatureError, ValueError):
        return False

