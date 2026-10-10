# art50pulse

Local **EU AI Act Article 50** transparency pre-audit for product and legal teams.

## Install

```bash
pip install .
```

## Quick start

```bash
# HTML fixture with chat widget but no disclosure → exit 2
art50pulse audit --html testdata/html/chat_no_disclosure.html

# Compliant sample → exit 0
art50pulse audit --html testdata/html/chat_with_disclosure.html

# Require C2PA/JUMBF markers on marketing assets
art50pulse audit --media ./hero.jpg --require-c2pa
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | No policy violations |
| 1 | Runtime / IO error |
| 2 | Article 50 transparency violation detected |

## JSON output

```bash
art50pulse audit --html page.html --output json
```

## Scope

This CLI checks **heuristic** signals (chat-widget fingerprints, disclosure copy, C2PA binary markers).
It does not replace legal counsel or full C2PA signing. Hosted fleet monitoring is a separate product.

## License

MIT — see [LICENSE](LICENSE).
