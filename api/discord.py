import nacl.signing
import nacl.exceptions
from http.server import BaseHTTPRequestHandler
import json, os, re, requests, time

import os, json
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

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            sig  = self.headers.get("X-Signature-Ed25519")
            ts   = self.headers.get("X-Signature-Timestamp")
            body = self.rfile.read(int(self.headers["Content-Length"]))

            if not verify_key(body, sig, ts, PUBLIC_KEY):
                self.send_error(401, "bad signature"); return

            payload = json.loads(body)

            # 1️⃣ Ping check
            if payload.get("type") == InteractionType.PING:
                return self._json({"type": InteractionResponseType.PONG})

            # 2️⃣ Slash command
            if payload.get("type") == InteractionType.APPLICATION_COMMAND:
                data     = payload["data"]
                options  = data.get("options", [])
                if data["name"] != "rsifind":
                    return self._msg("Unknown command.")

                handle   = options[0]["value"] if options else ""
                token    = payload["token"]
                app_id   = payload["application_id"]

                # Defer immediately (shows "Searching ...")
                self._json({"type": InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE})

                # your logic goes here

            if payload.get("type") == InteractionType.MESSAGE_COMPONENT:
                # your additional logic to handle component interaction goes here

                # Only if you need to Send an ephemeral response to acknowledge
                return self._json({
                    "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {
                        "content": f"Thanks for being a Good Sport! your feedback has been recorded.",
                        "flags": 64  # ephemeral message
                    }
                })

            # Unknown type
            self.send_error(400, "unknown interaction")

        except Exception as e:
            print("🔥 Exception:", e)
            self._msg("❌ Oops! Something bad happened. Please try again.")

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def _json(self, obj, status=200):
        out = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def _msg(self, text):
        return self._json({
            "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {"content": text}
        })


# ------------- Interaction / Response enums -----------------------

class InteractionType(IntEnum):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class InteractionResponseType(IntEnum):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
