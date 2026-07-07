import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

EXTRACTED_FILE = Path("output/extracted.json")
BUNDLE_DIR = Path("bundle")
MODEL = "gemini-2.5-flash"
BATCH_SIZE = 5          # files per API call
SECONDS_BETWEEN_CALLS = 15
MAX_RETRIES = 3

client = genai.Client()


def slugify(path: str) -> str:
    parts = path.replace("\\", "/").replace(".py", "").split("/")
    relevant = parts[-2:] if len(parts) >= 2 else parts
    slug = "_".join(relevant)
    return re.sub(r"[^a-z0-9_]+", "_", slug.lower())


def summarize_file(f: dict) -> str:
    route_lines = []
    for fn in f["functions"]:
        if fn["route_paths"]:
            methods = [d.split(".")[-1].upper() for d in fn["decorators"] if "router." in d]
            route_lines.append(f"{methods} {fn['route_paths']} -> {fn['name']}({', '.join(fn['args'])})")
    class_lines = [f"class {c['name']}(bases={c['bases']}) methods={[m['name'] for m in c['methods']]}" for c in f["classes"]]
    func_lines = [f"{fn['name']}({', '.join(fn['args'])})" for fn in f["functions"] if not fn["route_paths"]]

    return (
        f"path: {f['path']}\n"
        f"imports: {', '.join(f['imports'])}\n"
        f"routes: {route_lines or 'none'}\n"
        f"classes: {class_lines or 'none'}\n"
        f"functions: {func_lines or 'none'}"
    )


def build_batch_prompt(files: list[dict]) -> str:
    file_blocks = "\n\n".join(f"### FILE {i+1}\n{summarize_file(f)}" for i, f in enumerate(files))
    return f"""You are documenting a codebase for new engineers joining the team.
Below are {len(files)} source files. For EACH one, write a concise concept description
(under 120 words) covering: what it's responsible for, what it depends on (based on
imports), and any non-obvious design choices you can infer. Do not just restate the raw
data back verbatim.

{file_blocks}

Respond with ONLY a JSON array, no markdown fences, no preamble, in this exact shape:
[{{"path": "<file path exactly as given>", "description": "<your description>"}}, ...]"""


def call_with_retry(prompt: str) -> list[dict]:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            return json.loads(response.text)
        except (genai_errors.ClientError, genai_errors.ServerError) as e:
            if attempt < MAX_RETRIES:
                wait = 20 * attempt
                print(f"  Error ({e.__class__.__name__}), waiting {wait}s (attempt {attempt}/{MAX_RETRIES})...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Max retries exceeded")


def tags_for(f: dict) -> list[str]:
    tags = []
    if any(fn["route_paths"] for fn in f["functions"]):
        tags.append("api-endpoint")
    if f["classes"]:
        tags.append("data-model")
    if "crud" in f["path"]:
        tags.append("data-access")
    return tags


def write_concept_file(f: dict, description: str):
    slug = slugify(f["path"])
    out_path = BUNDLE_DIR / f"{slug}.md"
    resource_path = f["path"].replace("\\", "/")
    frontmatter = (
        "---\n"
        f"type: code_concept\n"
        f"title: \"{resource_path}\"\n"
        f"tags: {tags_for(f)}\n"
        f"resource: \"{resource_path}\"\n"
        f"timestamp: \"{datetime.now(timezone.utc).isoformat()}\"\n"
        "---\n\n"
    )
    out_path.write_text(frontmatter + description.strip(), encoding="utf-8")
    print(f"Wrote {out_path}")


def main():
    data = json.loads(EXTRACTED_FILE.read_text())
    BUNDLE_DIR.mkdir(exist_ok=True)

    pending = [f for f in data if not (BUNDLE_DIR / f"{slugify(f['path'])}.md").exists()]
    print(f"{len(pending)} files pending out of {len(data)} total")

    for i in range(0, len(pending), BATCH_SIZE):
        batch = pending[i:i + BATCH_SIZE]
        print(f"Batch {i // BATCH_SIZE + 1}: enriching {[f['path'] for f in batch]}")
        try:
            results = call_with_retry(build_batch_prompt(batch))
            results_by_path = {r["path"]: r["description"] for r in results}
            for f in batch:
                desc = results_by_path.get(f["path"])
                if desc:
                    write_concept_file(f, desc)
                else:
                    print(f"  Warning: no result returned for {f['path']}")
        except Exception as e:
            print(f"  Batch failed permanently: {e}")
        time.sleep(SECONDS_BETWEEN_CALLS)


if __name__ == "__main__":
    main()