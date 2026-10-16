"""Dependency-free checks for self-contained Python skills.

Run from the repository root:
    python3 -m unittest discover -s tests -v
"""

import ast
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1] / "skills" / "technical" / "python"
EXPECTED = {
    "python-code-quality", "python-collections", "python-concurrency",
    "python-control-flow", "python-data-modeling", "python-decorators",
    "python-effect-management", "python-error-handling", "python-event-handling",
    "python-functional-programming", "python-functions", "python-interfaces-dispatch",
    "python-iterators-generators", "python-metaprogramming", "python-modules",
    "python-object-creation", "python-object-design", "python-performance",
    "python-resource-management", "python-state-simulation", "python-stateless-effects",
    "python-testing", "python-trees-interpreters", "python-type-checking",
}


class PythonSkillTests(unittest.TestCase):
    def test_each_skill_is_self_contained(self):
        actual = {p.parent.name for p in ROOT.glob("*/SKILL.md")}
        self.assertEqual(actual, EXPECTED)
        for name in sorted(EXPECTED):
            with self.subTest(skill=name):
                directory = ROOT / name
                self.assertFalse(directory.is_symlink(), "Each skill must be a self-contained directory")
                self.assertEqual(
                    {p.name for p in directory.iterdir()}, {"SKILL.md"},
                    "All guidance must be in SKILL.md, without supporting files",
                )
                skill = directory / "SKILL.md"
                self.assertFalse(skill.is_symlink())
                text = skill.read_text(encoding="utf-8")
                prose = re.sub(r"```[\s\S]*?```|`[^`\n]*`", "", text)
                self.assertNotRegex(prose, r"!?\[[^\]\n]*\]\([^\n)]*\)", "No document links")
                self.assertNotRegex(
                    prose, r"(?im:references/|^##\s+References\s*$)|\[(?:\d{2}|[AB])(?:,\s*\d{2})*\]",
                )
                for sibling in EXPECTED - {name}:
                    self.assertNotIn(sibling, text, "A skill must not depend on another skill")
                self.assertIn("Thinking in Python", text)
                self.assertIn("Bruce Eckel", text)
                self.assertTrue(text.startswith("---\n"))
                self.assertIn("\n---\n", text[4:])
                self.assertLess(len(text), 100_000)

    def test_metadata_and_operational_rules_are_inline(self):
        required_sections = (
            "When to Use", "Philosophy", "Rules", "Procedure", "Pitfalls", "Verification",
        )
        for name in sorted(EXPECTED):
            with self.subTest(skill=name):
                text = (ROOT / name / "SKILL.md").read_text(encoding="utf-8")
                match = re.match(r"\A---\n([\s\S]+?)\n---\n", text)
                if match is None:
                    self.fail("Frontmatter is missing or incorrectly delimited")
                    continue
                lines = match[1].splitlines()
                # This collection deliberately uses flat frontmatter.
                self.assertTrue(all(re.fullmatch(r"[a-z_]+: .+", line) for line in lines))
                fields = dict(line.split(": ", 1) for line in lines)
                self.assertEqual(len(fields), len(lines), "Duplicate metadata keys")
                self.assertEqual(fields["name"], name)
                self.assertRegex(fields["version"], r"^\d+\.\d+\.\d+$")
                self.assertIn("mathias-mrsn", fields["author"])
                self.assertEqual(fields["platforms"], "[linux, macos, windows]")
                description = fields["description"].strip("\"'")
                self.assertLessEqual(len(description), 60)
                self.assertTrue(description.endswith("."))
                if not fields["description"].startswith(("'", '"')):
                    self.assertNotIn(": ", description, "A YAML colon must be quoted")
                for section in required_sections:
                    self.assertIn(f"\n## {section}\n", text)
                rules = text.split("\n## Rules\n", 1)[1].split("\n## Procedure\n", 1)[0]
                self.assertGreaterEqual(len(re.findall(r"^- ", rules, re.MULTILINE)), 15)
                self.assertNotRegex(text, r"/Users/|/home/|\.codex/|\.dotfiles/")

    def test_english_headings_and_no_french_instruction_markers(self):
        french_markers = re.compile(
            r"\b(?:utiliser|préférer|règles|vérification|pièges|lorsque|chaque|aucune?|ne\s+pas)\b",
            re.IGNORECASE,
        )
        for name in sorted(EXPECTED):
            with self.subTest(skill=name):
                text = (ROOT / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("\n## When to Use\n", text)
                self.assertNotRegex(text, french_markers)

    def test_shared_corpus_and_symlinks_are_absent(self):
        self.assertFalse((ROOT / "python-skill").exists())
        self.assertEqual({p.name for p in ROOT.iterdir() if p.is_dir()}, EXPECTED)
        self.assertEqual(list(ROOT.rglob("references")), [])
        self.assertFalse(any(p.is_symlink() for p in ROOT.rglob("*")))

    def test_python_examples_execute_in_isolation(self):
        for name in sorted(EXPECTED):
            text = (ROOT / name / "SKILL.md").read_text(encoding="utf-8")
            examples = re.findall(r"^```python\n(.*?)^```\s*$", text, re.MULTILINE | re.DOTALL)
            for index, code in enumerate(examples, 1):
                with self.subTest(skill=name, example=index):
                    tree = ast.parse(code, feature_version=(3, 11))
                    self.assertTrue(any(isinstance(node, ast.Assert) for node in ast.walk(tree)))
                    with tempfile.TemporaryDirectory(prefix="python-skill-example-") as directory:
                        result = subprocess.run(
                            [sys.executable, "-I", "-c", code], cwd=directory,
                            capture_output=True, text=True, timeout=20, check=False,
                        )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
