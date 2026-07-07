---
type: code_concept
title: "crud/tag.py"
tags: ['data-access']
resource: "crud/tag.py"
timestamp: "2026-07-07T14:45:09.318267+00:00"
---

This module is responsible for managing tags associated with articles. Its core functions include fetching all existing tags, retrieving tags for a specific article, and efficiently creating new tags only if they don't already exist in the database. It depends on `db.mongodb` for persistence, `models.tag` for defining tag data structures, and `core.config` for application settings. The design choice to include `create_tags_that_not_exist` indicates an "upsert" pattern for tag creation, ensuring tag uniqueness and minimizing redundant database writes.

## Related Concepts

Depends on:
- [[core_config]]
- [[db_mongodb]]
- [[models_tag]]

Used by:
- [[endpoints_tag]]