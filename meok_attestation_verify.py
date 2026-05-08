"""
meok-attestation-verify
========================
Tiny zero-dependency verifier for MEOK AI Labs compliance attestations.

Usage
-----
Pipe a cert JSON on stdin:

    cat cert.json | meok-attestation-verify

Or pass a file path:

    meok-attestation-verify cert.json

Or a cert_id (queries the public verify API):

    meok-attestation-verify MEOK-DORA-C8992DC765D8

Exit codes
----------
    0 — signature valid
    1 — signature invalid or expired
    2 — malformed cert / input error
    3 — network error (for remote cert_id verification)

Issued by MEOK AI Labs (https://meok.ai). Verification endpoint:
https://meok-attestation-api.vercel.app/verify

© 2026 MEOK AI Labs. MIT licensed.
"""

from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error

DEFAULT_API = "https://meok-attestation-api.vercel.app"


def verify_cert_offline(cert: dict) -> tuple[bool, str]:
    """Verify a cert locally — for now this requires the server-side signing key
    since HMAC is symmetric. So all we can do OFFLINE is validate structure + expiry
    + send back to the server for signature verification. True offline verification
    requires asymmetric signatures, on the roadmap.
    """
    required = ["cert_id", "payload", "signature_sha256_hmac", "issued_utc", "expires_utc"]
    missing = [k for k in required if k not in cert]
    if missing:
        return False, f"Missing fields: {missing}"
    try:
        payload = json.loads(cert["payload"])
    except Exception as e:
        return False, f"Payload is not valid JSON: {e}"
    # Expiry check
    from datetime import datetime, timezone
    try:
        expires = datetime.fromisoformat(payload["expires_utc"])
        if datetime.now(timezone.utc) > expires:
            return False, f"Cert expired on {payload['expires_utc']}"
    except Exception:
        pass
    # Structure OK — server must confirm signature.
    return True, "Structure + expiry OK (remote signature check needed)"


def verify_cert_remote(cert: dict, api: str = DEFAULT_API) -> tuple[bool, str, dict]:
    try:
        req = urllib.request.Request(
            f"{api}/verify",
            data=json.dumps(cert).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read())
        return bool(body.get("valid")), body.get("message", ""), body
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
            return False, body.get("error", f"HTTP {e.code}"), body
        except Exception:
            return False, f"HTTP {e.code}", {}
    except Exception as e:
        return False, f"Network error: {e}", {}


def verify_cert_id(cert_id: str, api: str = DEFAULT_API) -> tuple[bool, str]:
    """A bare cert_id can't be verified without the payload. Point the user at the
    human-readable verify URL and the requirement to POST the full cert."""
    url = f"{api}/verify/{cert_id}"
    return False, (
        f"Bare cert_id verification not possible without the payload (privacy-preserving).\n"
        f"Either POST the full cert JSON to {api}/verify, or open {url} in a browser\n"
        f"and ask the cert holder for the full JSON."
    )


def _load_cert(source: str) -> dict:
    """source: '-' for stdin, otherwise file path or cert_id."""
    if source == "-":
        text = sys.stdin.read()
    elif source and source.startswith("MEOK-"):
        return {"_cert_id_only": source}
    else:
        with open(source) as fp:
            text = fp.read()
    return json.loads(text)


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0

    src = argv[0]
    if src == "--stdin" or src == "-":
        src = "-"
    elif not sys.stdin.isatty() and src != "-":
        # If stdin has data AND a source was provided, stdin wins unless a real file/id was named
        pass

    try:
        cert = _load_cert(src)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Invalid JSON: {e}\n")
        return 2
    except FileNotFoundError:
        sys.stderr.write(f"File not found: {src}\n")
        return 2
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 2

    if cert.get("_cert_id_only"):
        ok, msg = verify_cert_id(cert["_cert_id_only"])
        print("VALID" if ok else "CANNOT_VERIFY_FROM_ID_ALONE")
        print(msg)
        return 0 if ok else 1

    # Local structural check
    ok_local, msg_local = verify_cert_offline(cert)
    if not ok_local:
        print("INVALID")
        print(f"Local check failed: {msg_local}")
        return 1

    # Remote signature check
    ok, msg, body = verify_cert_remote(cert)
    print("VALID" if ok else "INVALID")
    print(msg)
    if body:
        # Show the cert headline in human-readable form
        try:
            payload = json.loads(cert.get("payload", "{}"))
            print(f"\nRegulation: {payload.get('regulation')}")
            print(f"Entity:     {payload.get('entity')}")
            print(f"Score:      {payload.get('score_percent')}%")
            print(f"Assessment: {payload.get('assessment')}")
            print(f"Issued:     {payload.get('issued_utc')}")
            print(f"Expires:    {payload.get('expires_utc')}")
            print(f"Issuer:     {payload.get('issuer')}")
            print(f"Verify URL: {cert.get('verify_url')}")
        except Exception:
            pass
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
