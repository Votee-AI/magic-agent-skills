#!/usr/bin/env python3
"""Migrate SKILL.md frontmatter to agentskills.io format.

Moves root-level fields (version, author, tags, scripts, dependencies,
when_to_use) under metadata. Adds license and compatibility fields.
"""
import argparse
import glob
import os
import sys

import yaml


FIELDS_TO_MOVE = ["version", "author", "tags", "scripts", "dependencies", "when_to_use"]
SPEC_ROOT_FIELDS = {"name", "description", "license", "compatibility", "metadata"}


def parse_skill_md(path: str) -> tuple[dict, str]:
    with open(path, "r") as f:
        content = f.read()

    if not content.startswith("---\n"):
        raise ValueError(f"No frontmatter found in {path}")

    end_idx = content.index("\n---\n", 4)
    yaml_str = content[4:end_idx]
    body = content[end_idx + 5:]

    frontmatter = yaml.safe_load(yaml_str)
    return frontmatter, body


def migrate_frontmatter(fm: dict, has_python_scripts: bool) -> dict:
    result = {}

    result["name"] = fm["name"]
    result["description"] = fm["description"]
    result["license"] = "Apache-2.0"
    if has_python_scripts:
        result["compatibility"] = "Python 3.12+"

    metadata = dict(fm.get("metadata", {}))
    for field in FIELDS_TO_MOVE:
        if field in fm:
            val = fm[field]
            if field == "version":
                val = str(val)
                if val == "0.1":
                    val = "0.1.0"
            metadata[field] = val

    result["metadata"] = metadata
    return result


def write_skill_md(path: str, frontmatter: dict, body: str) -> None:
    yaml_str = yaml.dump(
        frontmatter,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )
    with open(path, "w") as f:
        f.write("---\n")
        f.write(yaml_str)
        f.write("---\n")
        f.write(body)


def verify_frontmatter(fm: dict) -> list[str]:
    errors = []
    if "name" not in fm:
        errors.append("missing required field: name")
    if "description" not in fm:
        errors.append("missing required field: description")
    extra = set(fm.keys()) - SPEC_ROOT_FIELDS
    if extra:
        errors.append(f"non-spec root fields: {extra}")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Migrate SKILL.md frontmatter")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--skills-dir", default="skills")
    args = parser.parse_args()

    skill_paths = sorted(glob.glob(os.path.join(args.skills_dir, "*/SKILL.md")))
    if not skill_paths:
        print(f"No SKILL.md files found in {args.skills_dir}/*/")
        sys.exit(1)

    print(f"Found {len(skill_paths)} SKILL.md files")
    errors = 0

    for path in skill_paths:
        dir_name = os.path.basename(os.path.dirname(path))
        if dir_name.startswith("_"):
            print(f"  SKIP: {dir_name} (shared utility)")
            continue

        try:
            fm, body = parse_skill_md(path)
        except (ValueError, yaml.YAMLError) as e:
            print(f"  ERROR: {path}: {e}")
            errors += 1
            continue

        if args.verify:
            validation_errors = verify_frontmatter(fm)
            if validation_errors:
                print(f"  FAIL: {dir_name}: {', '.join(validation_errors)}")
                errors += 1
            else:
                print(f"  OK: {dir_name}")
            continue

        has_python_scripts = bool(fm.get("scripts")) or any(
            f.endswith(".py")
            for f in glob.glob(os.path.join(os.path.dirname(path), "scripts", "*.py"))
        )

        migrated = migrate_frontmatter(fm, has_python_scripts)

        if args.dry_run:
            moved = [f for f in FIELDS_TO_MOVE if f in fm]
            added = ["license"]
            if has_python_scripts:
                added.append("compatibility")
            print(f"  {dir_name}: move [{', '.join(moved)}] to metadata, add [{', '.join(added)}]")
        else:
            write_skill_md(path, migrated, body)
            print(f"  MIGRATED: {dir_name}")

    if errors > 0:
        print(f"\n{errors} errors found")
        sys.exit(1)
    elif args.verify:
        print(f"\nAll files verified")
    elif args.dry_run:
        print(f"\nDry run complete. Run without --dry-run to apply changes.")
    else:
        print(f"\nMigration complete. Run with --verify to confirm.")


if __name__ == "__main__":
    main()
