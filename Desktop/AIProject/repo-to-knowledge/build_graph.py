"""
Week 3: Cross-linking script for repo-to-knowledge
Uses the `imports` field from extracted.json to build a dependency graph
between concept files, then writes both a graph.json and injects
"Related Concepts" links directly into each bundle .md file.
"""

import json
import re
from pathlib import Path

EXTRACTED_FILE = Path("output/extracted.json")
BUNDLE_DIR = Path("bundle")
GRAPH_FILE = Path("output/graph.json")


def slugify(path: str) -> str:
    parts = path.replace("\\", "/").replace(".py", "").split("/")
    relevant = parts[-2:] if len(parts) >= 2 else parts
    slug = "_".join(relevant)
    return re.sub(r"[^a-z0-9_]+", "_", slug.lower())


def module_path_of(file_path: str) -> str:
    """Convert a file path like 'crud/article.py' into a dotted module path 'crud.article'."""
    return file_path.replace("\\", "/").replace(".py", "").replace("/", ".")


def main():
    data = json.loads(EXTRACTED_FILE.read_text())

    # Build a lookup: dotted module path -> slug, so we can resolve imports to actual files
    module_to_slug = {module_path_of(f["path"]): slugify(f["path"]) for f in data}
    module_to_title = {module_path_of(f["path"]): f["path"] for f in data}

    nodes = [{"id": slugify(f["path"]), "path": f["path"]} for f in data]
    edges = []

    for f in data:
        source_slug = slugify(f["path"])
        for imp in f["imports"]:
            # An import might be a submodule (e.g. "models.article" imported as "models")
            # so check exact match first, then check if any known module starts with this import
            matches = [m for m in module_to_slug if m == imp or m.startswith(imp + ".") or imp.startswith(m + ".")]
            for m in matches:
                target_slug = module_to_slug[m]
                if target_slug != source_slug:
                    edges.append({"source": source_slug, "target": target_slug})

    # De-duplicate edges
    seen = set()
    unique_edges = []
    for e in edges:
        key = (e["source"], e["target"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)

    graph = {"nodes": nodes, "edges": unique_edges}
    GRAPH_FILE.parent.mkdir(exist_ok=True)
    GRAPH_FILE.write_text(json.dumps(graph, indent=2))
    print(f"Graph built: {len(nodes)} nodes, {len(unique_edges)} edges -> {GRAPH_FILE}")

    # Now inject "Related Concepts" section into each bundle .md file
    outgoing = {}
    incoming = {}
    for e in unique_edges:
        outgoing.setdefault(e["source"], []).append(e["target"])
        incoming.setdefault(e["target"], []).append(e["source"])

    for f in data:
        slug = slugify(f["path"])
        md_path = BUNDLE_DIR / f"{slug}.md"
        if not md_path.exists():
            continue

        content = md_path.read_text(encoding="utf-8")
        # Strip any previously injected section if re-running
        content = content.split("\n\n## Related Concepts")[0]

        depends_on = sorted(set(outgoing.get(slug, [])))
        used_by = sorted(set(incoming.get(slug, [])))

        section = "\n\n## Related Concepts\n"
        if depends_on:
            section += "\nDepends on:\n" + "\n".join(f"- [[{d}]]" for d in depends_on)
        if used_by:
            section += "\n\nUsed by:\n" + "\n".join(f"- [[{u}]]" for u in used_by)
        if not depends_on and not used_by:
            section += "\n(No detected internal dependencies)"

        md_path.write_text(content + section, encoding="utf-8")

    print("Injected Related Concepts links into all bundle files.")


if __name__ == "__main__":
    main()