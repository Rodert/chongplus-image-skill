# Troubleshooting

| Symptom | Meaning | Action |
| --- | --- | --- |
| `No ChongPlus API key is saved` | No local credential is configured. | Ask for the key and save it with `config --set-key` or safe stdin. |
| `HTTP 401` | The key is missing or invalid. | Replace the saved key. |
| `HTTP 403` with `error code: 1010` | Cloudflare blocked the request before the API application processed it. | Keep the bundled `User-Agent`; ask the ChongPlus operator to inspect Cloudflare firewall events for the request time. |
| Other `HTTP 403` | The key lacks model access, has no quota, or is otherwise forbidden. | Check account access and quota. |
| `HTTP 429` | The service rate-limited the request. | Retry after a delay and lower parallelism. |
| `HTTP 500`, `502`, or `504` | Upstream service or gateway failed. | Retry once after a delay; retain the status and response body for support. |
| Returned image size differs | The gateway selected a different supported output size. | Report the actual saved dimensions; use a documented size on the next request. |

`config --check` performs a no-cost local configuration check. It does not prove API access. No API endpoint documented by ChongPlus provides a free authentication-only health check; a real generation request can consume quota.
