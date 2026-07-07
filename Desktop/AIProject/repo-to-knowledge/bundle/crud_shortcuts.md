---
type: code_concept
title: "crud/shortcuts.py"
tags: ['data-access']
resource: "crud/shortcuts.py"
timestamp: "2026-07-07T14:45:09.315601+00:00"
---

This `shortcuts` module provides common utility functions to simplify CRUD operations across different entities, acting as an abstraction layer for frequent checks and retrievals. It depends on `pydantic` for data validation, `starlette` components for raising HTTP exceptions (like 404s), and directly utilizes `crud.article`, `crud.user`, and `db.mongodb` for underlying data access. A key design choice is to centralize boilerplate like checking for unique usernames/emails or verifying article existence and user permissions, preventing repetitive code and enforcing consistent error handling patterns within the API endpoints.

## Related Concepts

Depends on:
- [[db_mongodb]]
- [[models_article]]

Used by:
- [[endpoints_article]]
- [[endpoints_authenticaion]]
- [[endpoints_comment]]
- [[endpoints_user]]