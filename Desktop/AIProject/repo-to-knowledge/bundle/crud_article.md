---
type: code_concept
title: "crud/article.py"
tags: ['data-access']
resource: "crud/article.py"
timestamp: "2026-07-07T14:44:35.647676+00:00"
---

This module is the core data access layer (CRUD) for articles within the application. It provides functions for creating, retrieving, updating, and deleting articles, alongside specialized operations like managing user favorites, counting favorites, and filtering articles. It depends on `db.mongodb` for database interactions, `models.article` for data structure, and uses `slugify` for generating unique article identifiers. A key design choice is passing `conn` as an argument for database operations, promoting dependency injection. Many functions also take `username`, indicating personalized data retrieval or authorization checks, potentially interacting with user profiles and tags for richer article data.

## Related Concepts

Depends on:
- [[core_config]]
- [[db_mongodb]]
- [[models_article]]

Used by:
- [[endpoints_article]]