import nacl.signing
import nacl.exceptions
from http.server import BaseHTTPRequestHandler
from enum import IntEnum
import json, os

from utils import (
    calculate_elevation_by_coordinates,
    calculate_elevation
)

PUBLIC_KEY = os.environ["DISCORD_PUBLIC_KEY"]

def verify_key(body: bytes, sig: str, timestamp: str, public_key: str) -> bool:
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

#             if not verify_key(body, sig, ts, PUBLIC_KEY):
#                 self.send_error(401, "bad signature")
#                 return

            payload = json.loads(body)

            # 1. Ping
            if payload.get("type") == InteractionType.PING:
                return self._json({"type": InteractionResponseType.PONG})

            # 2. Slash Commands
            if payload.get("type") == InteractionType.APPLICATION_COMMAND:
                data = payload["data"]
                command_name = data["name"]
                options = data.get("options", [])

                # Expecting single string input like: "x1,y1,x2,y2,..."
                raw_input = options[0]["value"] if options else ""

                try:
                    values = [float(x.strip()) for x in raw_input.split(",")]
                except:
                    return self._msg("❌ Invalid input format. Use comma-separated numbers.")

                # ===============================
                # /calcPosAngle
                # ===============================
                if command_name == "calcposangle":
                    if len(values) != 6:
                        return self._msg("❌ Need 6 values: x1,y1,x2,y2,ballistic_data,elevation_diff")

                    x1, y1, x2, y2, ballistic_data, elevation_diff = values

                    # ⚠️ ballistic_data should be dict, but user gives float
                    # You MUST define or load actual ballistic table here
                    ballistic_table = {
                        100: ballistic_data,
                        200: ballistic_data + 10,
                        300: ballistic_data + 20
                    }

                    elev, deg, mils, dist = calculate_elevation_by_coordinates(
                        x1, y1, x2, y2, ballistic_table, elevation_diff
                    )

                    return self._embed({
                        "title": "Calc Position + Angle",
                        "fields": [
                            {"name": "Distance (m)", "value": str(round(dist, 2)), "inline": True},
                            {"name": "Direction (°)", "value": str(round(deg, 2)), "inline": True},
                            {"name": "Direction (mils)", "value": str(round(mils, 2)), "inline": True},
                            {"name": "Elevation (mils)", "value": str(elev), "inline": False},
                        ]
                    })

                # ===============================
                # /calcElev
                # ===============================
                elif command_name == "calcelev":
                    if len(values) != 3:
                        return self._msg("❌ Need 3 values: distance,ballistic_data,elevation_diff")

                    distance, ballistic_data, elevation_diff = values

                    ballistic_table = {
                        100: ballistic_data,
                        200: ballistic_data + 10,
                        300: ballistic_data + 20
                    }

                    elev = calculate_elevation(
                        distance, ballistic_table, elevation_diff
                    )

                    return self._embed({
                        "title": "Calc Elevation",
                        "fields": [
                            {"name": "Distance (m)", "value": str(distance), "inline": True},
                            {"name": "Elevation (mils)", "value": str(elev), "inline": True},
                        ]
                    })

                else:
                    return self._msg("Unknown command.")

            self.send_error(400, "unknown interaction")

        except Exception as e:
            print("🔥 Exception:", e)
            self._msg("❌ Internal error occurred.")

    # =============================
    # Helpers
    # =============================

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

    def _embed(self, embed):
        return self._json({
            "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "embeds": [embed]
            }
        })


# =============================
# Enums
# =============================

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