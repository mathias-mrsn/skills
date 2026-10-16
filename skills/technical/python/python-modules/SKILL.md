---
name: python-modules
description: Organize packages, imports and public boundaries.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Modules, Packages and Loading

## When to Use

- Split a program across files, define its exports and stabilize its entry point.
- Diagnose a failed import, a cycle, a name collision or a stale imported value.
- Choose between immediate and deferred loading without losing initialization effects.
- Do not reorganize paths or dependencies before identifying the actual interpreter and execution context.

## Philosophy

- A module is a namespace and a unit of execution, not just a file of declarations.
- Keep the origin of names, dependencies and the timing of their effects readable.
- A public boundary rests on a contract: neither underscores nor an export list make other names inaccessible.
- A cycle or an implicit dependency is first a problem to explain, not a reason to manipulate `sys.path` blindly.
- Respect the project's minimum version; the example below works on Python 3.11+ without installing any package.

Original synthesis based on Bruce Eckel, Thinking in Python, corpus a8feb860 (CC BY-NC-ND 4.0).

## Rules

### Namespaces and Import Forms

- Import a file by its module name, without the `.py` suffix; choose names usable as Python identifiers, excluding keywords.
- `import module` binds the module and preserves its qualification: `module.operation` indicates the origin and limits local collisions.
- `from module import name` also executes the entire module and locally binds the object referred to at that moment; it neither loads only the function nor creates a live reference to the name in the other module.
- If the module later reassigns its attribute, the name imported with `from` continues to refer to the old object.
- If several names refer to the same mutable object, a mutation remains visible everywhere; reassignment changes only one binding.
- For configuration that may be replaced, prefer `import configuration` followed by `configuration.option` to importing values.
- Use `from` for stable names, especially functions and classes, if it improves readability without hiding their origin.
- Use `as` to resolve a collision or adopt a clear alias; a module alias does not create a new instance.
- The `module.__dict__` dictionary corresponds to the namespace returned by `globals()` in that module.
- Avoid manufacturing names by writing to `globals()`: the reader, linter and checker do not necessarily see these dynamic declarations.
- If names are known only at runtime, prefer an explicit dictionary to a proliferation of computed global variables.

### Execution, Cache and Entry Point

- The first ordinary load executes the body from top to bottom; the module is placed in `sys.modules` before its initialization finishes.
- Subsequent imports under the same name reuse that object: they do not normally execute the body again.
- The cache key is the qualified name, not a guarantee of the file's physical uniqueness; do not load the same state under different identities.
- The cache belongs to one interpreter: processes and subinterpreters do not automatically share these objects or their writes.
- Place simple shared state in an imported module rather than creating a Singleton class without any other need.
- Document loading effects: plugin registration, populating a table, console output or resource acquisition.
- Isolate application launch in `if __name__ == '__main__':` so that importing supplies definitions without starting the application.
- This guard protects only its own block; all other module-level code still executes on import.
- In an imported module, `__name__` is its qualified name; when run as a program, it becomes `__main__`. Keep singleton state outside the file being run: a later import under its other name can create a second copy of that state.
- Editing the source file does not change an already loaded module; restart for reliable verification.
- `importlib.reload` reexecutes the body in the existing module object but does not update names already bound by `from`; do not present reload as a complete restart.

### Packages and Execution in Context

- Group related modules into a coherent package, with an explicit `__init__.py` by default.
- A namespace package can exist without this file; do not break an intentional organization by imposing unnecessary initialization.
- `__init__.py` initializes the package before its submodules; leave it empty if it has no public boundary to compose.
- Reexport the few desired public names in `__init__.py` to hide their internal location from clients.
- Do not confuse importing a package with importing all its contents: its submodules are available only if something loads them.
- `import package.module` normally binds `package` in the importer; the loaded submodule becomes an attribute of the package.
- `from package import module` binds `module` directly; `from package.module import function` binds only the function's name in the client.
- A nested name such as `package.subpackage.module` describes the levels to resolve, not short names automatically created in the importer.
- Between modules in the same package, use explicit relative imports for local dependencies: one dot denotes the current package, two its parent.
- To cross a package boundary, prefer an absolute path that makes the dependency visible.
- A relative import requires a package context; running an internal file in isolation removes that context.
- To run a submodule, use the project's interpreter with `-m package.module`, from an environment where the package resolves.
- Do not fix the "no known parent package" error by adding arbitrary paths inside the file; correct the launch mode.

### Exports and File Names

- Mark internal details with a leading underscore; this convention forbids neither qualified access nor explicit import.
- Define `__all__` as a list of public names expressed as strings if an explicit boundary improves readability and documentation.
- `from module import *` imports exactly the names in `__all__` if that list exists, even those starting with an underscore.
- Without `__all__`, the star imports names not prefixed with an underscore; it can therefore leak imported dependencies.
- `__all__` does not control `module.name` and provides neither privacy nor access control.
- Name imports in maintained code; reserve the star for interactive experiments where implicit provenance is acceptable.
- Use short, lowercase module names, optionally in `snake_case`; avoid hyphens, camelCase and CapWords.
- For packages, prefer a short all-lowercase name; add underscores only if they genuinely improve readability.
- Name test files according to the project's conventions, usually `test_*.py`.
- Do not name a local module `random.py`, `string.py` or after an expected dependency: the local path can shadow the library.
- Give shared modules distinctive names; generic names such as `config` can collide across the interpreter.
- Preserve exactly the same case in the file and the import, even on a case-insensitive filesystem.
- Do not rely on `PYTHONCASEOK` to make inconsistent naming work across machines.

### Module Resolution and Cycles

- Inspect `sys.path`, the executable actually used and the loaded module's path before changing the environment.
- Ordinary lookup follows `sys.path` in order: the appropriate launch directory, added paths, then installations according to the configuration.
- `PYTHONPATH` adds search paths; an injected path can shadow a library instead of resolving a dependency cleanly.
- For a packaged project, prefer making it available in the intended environment to an essential but undocumented personal `PYTHONPATH`.
- Do not install anything or change the environment without authorization; first use the mechanism already provided by the project.
- The `-P` option, available since Python 3.11, avoids initially adding the potentially unsafe path; it does not remove all other path sources.
- If no location supplies the name, diagnose `ModuleNotFoundError`; do not confuse a missing module with a missing name in a module that was found.
- In a cycle, the second module can see the first before its definitions have executed.
- Replacing `from A import value` with `import A` can postpone the error until `A.value`, without fixing the circular dependency.
- Extract the common contract, data or functions into a third module if this restores a clear direction of dependencies.
- Do not infer the cause from the word "circular" alone: read the exact error path and also look for a file that shadows a library.
- For a dependency used only by annotations, place the import under `if TYPE_CHECKING:`; do not hide a name needed by the executed body there.
- In Python 3.11 through 3.13, defer these annotations with `from __future__ import annotations` or use appropriate string references to avoid their immediate resolution.
- With deferred annotations in Python 3.14+, distinguish definition from introspection: reading that requires values can still need names absent at runtime.

### Deferred Loading: Choices, Limits and Effects

- Defer an import only if startup cost or an optional dependency justifies it; measure loading and first use separately.
- On a target earlier than Python 3.15, a local import inside the consuming function defers loading until that call.
- This choice hides the dependency at the top level and repeats a lookup in `sys.modules` on subsequent calls, without normally reexecuting the module.
- A package can also define a module `__getattr__` that imports and returns the requested submodule; reserve this mechanism for a controlled public boundary.
- This hook must distinguish supported names and raise `AttributeError` for the others; make explicit whether the result is subsequently cached.
- For Python 3.15, the corpus presents `lazy import` and `lazy from ... import`: write them only if the target and its implementation support them.
- These forms keep the declaration at module level but defer loading until the imported name is first used.
- A missing or broken dependency therefore fails on first use, not necessarily at the import declaration.
- The described `lazy` form is forbidden inside a function, a class body or a `try` block, as well as with the star and `from __future__`.
- To catch the absence of an optional dependency on older targets, keep an ordinary import in a `try` or inside the relevant function.
- On the described 3.15 implementation, `-X lazy_imports=normal` or `PYTHON_LAZY_IMPORTS=normal` defers only explicitly marked imports.
- The `all` mode defers eligible module-level imports, not those excluded by the syntax; the corpus does not retain the `none` mode.
- Do not systematically enable `all`: treat this mode as an experiment that verifies the effects of each import.
- `sys.lazy_modules`, on this implementation, indicates names still pending, not the application's history; internal imports can already appear there.
- Check membership of a specific name rather than requiring a predictable overall size for this set.
- Keep an import immediate if it exists to register a plugin, install a codec or populate a table: without access to the name, its deferred effect never occurs.
- Test the registry's state before the first client operation; a missing entry can indicate an unexecuted import, not a defective class.

## Procedure

1. Record version, interpreter, launch directory, script or `-m` mode and the location actually loaded.
2. Draw the relevant dependencies and separate public definitions, application launch and initialization effects.
3. Choose explicit imports and a coherent package; stabilize reexports and verify names and their case.
4. For a failure, distinguish lookup, shadowing, cycles, reassignment and annotations; fix the cause without adding a hidden path.
5. If loading is deferred, verify first use, errors and registrations; also validate the path without use.

### Self-contained Example: Cache and Bindings, Without Files

```python
import importlib
import sys
from types import ModuleType

name = "_inline_module_exercise"
assert name not in sys.modules
module = ModuleType(name)
exec("__all__ = ['items']\nitems = []\n_hidden = 7\n", module.__dict__)
sys.modules[name] = module
try:
    first = importlib.import_module(name)
    second = importlib.import_module(name)
    namespace: dict[str, object] = {}
    exec(f"from {name} import *", namespace)
    assert first is second is module
    original = namespace["items"]
    module.items.append("shared")
    assert original == ["shared"]
    module.items = ["replacement"]
    assert original == ["shared"]
    assert namespace["items"] is not module.items
    assert "_hidden" not in namespace and module._hidden == 7
finally:
    del sys.modules[name]
assert name not in sys.modules
```

This example intentionally constructs an in-memory module; it verifies caching, exports and reassignment, not disk lookup or `lazy` syntax.

## Pitfalls

- Believing that `from` loads less code, that the star defines a private interface or that importing a package loads all its submodules.
- Hiding a structural flaw with local imports everywhere, a personal `PYTHONPATH` or a modification of `sys.path`.
- Expecting automatic registration from a module that never executed, or comparing the global contents of deferred imports with a constant.
- Inferring Python 3.15 compatibility from the presence of Python 3.14, or confusing a reload with a fresh process.

## Verification

- In a fresh process, test the execution modes actually supported and the public import from the intended environment.
- Verify the loaded path, the identity of repeated imports, effects executed only once under the same name and the absence of unintentional launch.
- Check mutations and reassignments of shared objects separately; confirm which public and internal names are accessible.
- For cycles, try different initial imports; for deferred loading, check before and after first use.
- Verify available plugins and optional-dependency errors; report separately what was executed and what remains version-dependent.
