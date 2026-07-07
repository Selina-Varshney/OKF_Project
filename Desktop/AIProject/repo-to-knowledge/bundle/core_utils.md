---
type: code_concept
title: "core/utils.py"
tags: []
resource: "core/utils.py"
timestamp: "2026-07-07T14:44:35.644653+00:00"
---

This utility module provides a specialized function for formatting API responses. Its sole responsibility is to generate `starlette.responses.JSONResponse` objects from `pydantic` models, specifically ensuring that model fields are serialized using their defined aliases (e.g., `user_id` becomes `userId`). This design choice leverages `fastapi.encoders` to bridge internal Pythonic naming conventions with external API naming requirements, promoting consistency in the API contract and improving developer experience by allowing `snake_case` internally while presenting `camelCase` externally.

## Related Concepts


Used by:
- [[endpoints_article]]
- [[endpoints_comment]]