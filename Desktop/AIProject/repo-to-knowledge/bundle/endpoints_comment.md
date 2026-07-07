---
type: code_concept
title: "api/api_v1/endpoints/comment.py"
tags: ['api-endpoint']
resource: "api/api_v1/endpoints/comment.py"
timestamp: "2026-07-07T14:36:03.719588+00:00"
---

This module manages comment-related API operations for articles. It allows for creating, retrieving, and deleting comments associated with specific articles. It utilizes JWT for authenticated user access and core utilities for request processing. Dependencies include CRUD operations for comments and users, MongoDB for storage, and data models for comments and users. The nested route structure for comments under articles (`/articles/{slug}/comments`) indicates a clear hierarchical relationship.

## Related Concepts

Depends on:
- [[core_jwt]]
- [[core_utils]]
- [[crud_comment]]
- [[crud_shortcuts]]
- [[db_mongodb]]
- [[models_comment]]
- [[models_user]]