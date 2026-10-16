# Repository Conventions

## Language

- Write and maintain all skills in English, including YAML descriptions, headings, rules, decision criteria, procedures, pitfalls, verification steps, and examples.
- Keep supporting documentation, code comments, and human-readable example text in English as well.
- Preserve skill identifiers, public API names, commands, version constraints, and source attribution exactly when translating.
- Do not change an artifact's language to match the language used in chat.

## Self-Contained Skills

- Each skill must contain its complete guidance directly in its own `SKILL.md`.
- Do not introduce reference directories, symbolic links, or instructions that require another document or skill to understand the rules.
- Keep thematic scope and concrete decision criteria; do not replace rules with a list of topics.

## Verification and Scope

- Preserve every rule and qualification when translating; do not summarize or silently change behavior.
- Run the repository's validation suite after edits: `python3 -m unittest discover -s tests -v`.
- Run embedded executable examples and preserve attribution and source notices.
- Do not modify the original Codex collection when editing this repository.
- Do not commit or push unless explicitly requested.
