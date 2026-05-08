# meok-attestation-verify

Tiny zero-dependency verifier for MEOK AI Labs compliance attestations.

Pipe a cert on stdin — get VALID or INVALID back. Nothing installed, nothing to configure.

## Install

```bash
pip install meok-attestation-verify
```

## Verify a cert

```bash
# Via stdin
cat cert.json | meok-attestation-verify

# Via file
meok-attestation-verify cert.json

# Via cert ID only (opens the public verify page)
meok-attestation-verify MEOK-DORA-C8992DC765D8
```

Exit code `0` = valid, `1` = invalid/expired, `2` = malformed input, `3` = network error.

## Why does this exist?

MEOK AI Labs issues HMAC-signed attestations for EU compliance frameworks (DORA, NIS2, CRA, EU AI Act, CSRD, AI-BOM, geospatial data provenance). Each cert carries:

- `cert_id` — unique identifier
- `payload` — canonical signed JSON
- `signature_sha256_hmac` — cryptographic binding
- `verify_url` — public verify page

Auditors, boards, and procurement teams can verify a cert **without contacting MEOK** by POSTing the cert to the public verify endpoint at <https://meok-attestation-api.vercel.app/verify>.

This CLI wraps that verify flow for humans and CI pipelines.

## Get a signed attestation

Signed attestations are issued by these MCP servers (Pro tier, £199/mo):

- [`dora-compliance-mcp`](https://pypi.org/project/dora-compliance-mcp/)
- [`nis2-compliance-mcp`](https://pypi.org/project/nis2-compliance-mcp/)
- [`cra-compliance-mcp`](https://pypi.org/project/cra-compliance-mcp/)
- [`eu-ai-act-compliance-mcp`](https://pypi.org/project/eu-ai-act-compliance-mcp/)
- [`ai-bom-mcp`](https://pypi.org/project/ai-bom-mcp/)
- [`csrd-compliance-mcp`](https://pypi.org/project/csrd-compliance-mcp/)
- [`gods-eye-geospatial-mcp`](https://pypi.org/project/gods-eye-geospatial-mcp/)

Subscribe: <https://buy.stripe.com/14A4gB3K4eUWgYR56o8k836>

## Full Compliance Platform

**[councilof.ai](https://councilof.ai)** — the complete EU regulatory compliance platform. EU AI Act, DORA, NIS2, CRA, CSRD from £29/mo.

→ **[Get started at councilof.ai](https://councilof.ai)**

## License

MIT — [MEOK AI Labs](https://meok.ai), 2026.

<!-- mcp-name: io.github.CSOAI-ORG/meok-attestation-verify -->
