import os, requests
import nacl

PUBLIC_KEY          = os.environ["DISCORD_PUBLIC_KEY"]
DISCORD_API_BASE    = "https://discord.com/api/v10"
CLIENT_ID = ''
CLIENT_SECRET = ''


def refresh_token(refresh_token):
    data = {
    'grant_type': 'refresh_token',
    'refresh_token': refresh_token
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % DISCORD_API_BASE, data=data, headers=headers, auth=(CLIENT_ID, CLIENT_SECRET))
    r.raise_for_status()
    return r.json()

def verify_key(body: bytes, sig: str, timestamp: str, public_key: str) -> bool:
    """Return True if the Ed25519 signature is valid for the given body."""
    try:
        verify_key = nacl.signing.VerifyKey(bytes.fromhex(public_key))
        verify_key.verify(f"{timestamp}".encode() + body, bytes.fromhex(sig))
        return True
    except (nacl.exceptions.BadSignatureError, ValueError):
        return False

