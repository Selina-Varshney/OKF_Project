---
type: code_concept
title: "models/comment.py"
tags: ['data-model']
resource: "models/comment.py"
timestamp: "2026-07-07T14:45:35.737922+00:00"
---

This file defines the Pydantic data models for comments, mirroring the structure found in `article.py`. It depends on `typing`, `dbmodel` for database-specific mixins, `profile` for associating comments with user profiles, and `rwmodel` as a base for API-facing schemas. The design choice to create separate models like `CommentInDB`, `CommentInCreate`, and `CommentInResponse` reflects a consistent pattern for handling data at different stages: database storage, API input, and API output, ensuring strict data validation and clear API contracts across the application.

## Related Concepts


Used by:
- [[crud_comment]]
- [[endpoints_comment]]