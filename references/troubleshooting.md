# Troubleshooting

| Symptom | Meaning | Action |
| --- | --- | --- |
| `No ChongPlus API key is saved` | No local credential is configured. | Ask for the key and save it with `config --set-key` or safe stdin. |
| Authentication failure | The key is missing, invalid, or lacks access. | Replace the saved key or check its access and quota. |
| Authorization failure | The request was not allowed. | Check account access and quota. |
| Rate limit | The service temporarily limited requests. | Retry after a delay and lower parallelism. |
| Temporary service failure | The image service or a network route is unavailable. | Retry once after a delay. |
| Returned image size differs | The gateway selected a different supported output size. | Report the actual saved dimensions; use a documented size on the next request. |

`config --check` performs a no-cost local configuration check. It does not prove API access. No API endpoint documented by ChongPlus provides a free authentication-only health check; a real generation request can consume quota.

The client intentionally does not print upstream host names, response bodies, proxy details, or firewall details in user-facing errors.
