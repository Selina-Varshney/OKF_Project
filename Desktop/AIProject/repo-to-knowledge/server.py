"""
Week 4: MCP server for repo-to-knowledge
Exposes the OKF concept bundle as tools any MCP-compatible host can query.
"""

import json
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

BUNDLE_DIR = Path(__file__).parent / "bundle"
GRAPH_FILE = Path(__file__).parent / "output" / "graph.json"

mcp = FastMCP("repo-to-knowledge")


def parse_frontmatter(content: str) -> dict:
    """Very small YAML-ish frontmatter parser, good enough for our own generated files."""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    raw = content[3:end].strip()
    meta = {}
    for line in raw.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"')
    return meta


@mcp.tool()
def list_concepts() -> list[dict]:
    """List every concept file in the knowledge bundle, with its path and tags."""
    results = []
    for md_file in sorted(BUNDLE_DIR.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        meta = parse_frontmatter(content)
        results.append({
            "slug": md_file.stem,
            "path": meta.get("resource", md_file.stem),
            "tags": meta.get("tags", ""),
        })
    return results


@mcp.tool()
def get_concept(slug: str) -> str:
    """Get the full content of one concept file by its slug (e.g. 'crud_article')."""
    md_file = BUNDLE_DIR / f"{slug}.md"
    if not md_file.exists():
        return f"No concept found with slug '{slug}'. Use list_concepts to see available slugs."
    return md_file.read_text(encoding="utf-8")


@mcp.tool()
def search_bundle(query: str) -> list[dict]:
    """Search concept files by keyword match against title, tags, and description text.
    Returns the most relevant concepts with a short snippet."""
    query_terms = query.lower().split()
    scored = []

    for md_file in sorted(BUNDLE_DIR.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        lower = content.lower()
        score = sum(lower.count(term) for term in query_terms)
        if score > 0:
            meta = parse_frontmatter(content)
            body_start = content.find("---", 3) + 3
            body = content[body_start:].strip()
            snippet = body[:200].replace("\n", " ")
            scored.append({
                "slug": md_file.stem,
                "path": meta.get("resource", md_file.stem),
                "score": score,
                "snippet": snippet + "...",
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:5]


@mcp.tool()
def get_related_concepts(slug: str) -> dict:
    """Get the dependency graph neighbors (depends on / used by) for a given concept slug."""
    if not GRAPH_FILE.exists():
        return {"error": "graph.json not found, run build_graph.py first"}

    graph = json.loads(GRAPH_FILE.read_text())
    depends_on = [e["target"] for e in graph["edges"] if e["source"] == slug]
    used_by = [e["source"] for e in graph["edges"] if e["target"] == slug]
    return {"slug": slug, "depends_on": depends_on, "used_by": used_by}


if __name__ == "__main__":
    mcp.run()