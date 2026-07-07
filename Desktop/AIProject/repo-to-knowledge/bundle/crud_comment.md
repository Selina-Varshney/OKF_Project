---
type: code_concept
title: "crud/comment.py"
tags: ['data-access']
resource: "crud/comment.py"
timestamp: "2026-07-07T14:44:35.647676+00:00"
---

This module provides the data access layer (CRUD) for managing comments related to articles. It is responsible for retrieving all comments for a given article, creating new comments, and deleting existing ones. It depends on `db.mongodb` for database interactions, `models.comment` for the comment data structure, and `profile` for potentially linking comments to user profiles. Design choices mirror other CRUD modules, using dependency injection for the database connection (`conn`) and incorporating `slug` to identify articles and `username` for authorization and contextual operations, ensuring comments are correctly associated and managed securely.

## Related Concepts

Depends on:
- [[core_config]]
- [[db_mongodb]]
- [[models_comment]]

Used by:
- [[endpoints_comment]]