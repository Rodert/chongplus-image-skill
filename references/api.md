# ChongPlus Image API

- Official API base URL: `https://api.chongplus.plus`
- Client routing: the bundled client sends requests to `https://ai.chongplus.plus` and does not automatically resubmit after a network failure or timeout
- Default model: `gpt-image-2.5-flare`
- Refinement model: `gpt-image-2.5-sunburst` (use only when the user requests精细化处理)
- Generate: `POST /v1/images/generations`, JSON body with `model`, `prompt`, `size`, optional `n` (1-4), and `response_format`.
- Edit: `POST /v1/images/edits`, multipart form fields `image`, `model`, `prompt`, optional `size` and `n` (1-4).
- Auth: `Authorization: Bearer sk-...`
- Documented sizes: `1024x1024`, `2048x2048`, `1536x1024`, `1024x1536`, `3840x2160`, `2160x3840`.
- Responses contain `data` entries with either `url` or `b64_json`.

Source: https://api.chongplus.plus/tools/image-studio/docs/
