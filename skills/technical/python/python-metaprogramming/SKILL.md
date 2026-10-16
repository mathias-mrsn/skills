---
name: python-metaprogramming
description: Build and inspect classes with discernment.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Python Metaprogramming

## When to Use

- Build a family of classes from data rather than copying definitions.
- Register subclasses, collect marked methods, or apply an invariant when they are created.
- Reuse an access or validation rule with a descriptor.
- Choose between a hook, a class decorator, and a metaclass, or understand their execution order.
- Inspect a signature, members, or annotations without confusing declarations with behavior.
- Do not generate classes if a value, a function, or a table is enough to represent the variation.

## Philosophy

A class is an object built while the program runs.
Hooks are not additional magic: Python calls functions at specific moments.
Choose the narrowest intervention point that solves the problem; a metaclass remains the last resort.
The cost to control is as much the effort of understanding the program as its length.
The structure actually produced must fulfill the promises made to users and the type checker.

Original synthesis based on Bruce Eckel, Thinking in Python, corpus a8feb860.
Attribution does not imply any new license for the source text.

## Rules

### Choose When to Intervene

- React to a new subclass: define `__init_subclass__` on a common base.
- An attribute that needs to learn its owner and name: give it `__set_name__`.
- Transform or inspect a completed class: use a class decorator.
- A family defined by name, bases, and attributes: consider `type(name, bases, namespace)`.
- A special namespace during execution of the body: use `__prepare__` on a metaclass.
- A structural transformation before construction, particularly of bases or slots: intervene in its `__new__`.
- Modify an already constructed class in an existing metaclass: its `__init__` may suffice.
- Intercept calls to the class and instance construction: its `__call__`.
- Read an existing structure: use `inspect`, without rewriting it to discover it.

### Understand Classes, Instances, and Hook Order

- A class modification can affect attribute lookup on already created instances without changing their dictionaries.
- Distinguish a class's base from the metaclass that constructs it: ordinary inheritance and `metaclass=` are not interchangeable.
- The usual sequence is: `__prepare__`, class body, metaclass `__new__`, then its `__init__`, then class decorators.
- During the call to `type.__new__`, Python names attributes with `__set_name__`, then triggers `__init_subclass__`.
- These two hooks therefore run before that `__new__` returns, not after all construction is complete.
- Metaclass `__call__` intervenes later, on every call to the completed class.
- A method decorator runs during the body: the class it might want to consult does not exist yet.
- Avoid making a hook depend on a global class name before the `class` statement has bound it.

### Generate Only the Necessary Distinction

- A generated class is a real type; it can be used with `isinstance` or a class pattern.
- If callers distinguish only data, prefer an explicit field to a subclass for each value.
- With `type`, supply a tuple of bases and a dictionary of functions and attributes.
- Functions placed in this namespace become methods through the descriptor protocol.
- Capture each varying parameter in a local factory to avoid late binding of a loop variable.
- A nested function passed to `type` does not acquire the `__class__` cell that a method compiled in a class body would have.
- Do not assume zero-argument `super()` works there; choose explicit delegation compatible with the intended bases.
- Build a small known set in advance; defer generation only if many classes would remain unused.
- Deferred generation must reject unknown names and retain the already constructed type if type identity matters.
- Repeating generation without memoization creates distinct types, even under the same name.

### Constrain Code Constructed as Text

- `exec` can make a generated body more readable than assembling a dictionary, but it executes a complete program.
- Prefer `type` when the differences are values: a name remains a string there, not source code.
- Never interpolate uncontrolled external input into source; a closed list of known names avoids this unrestricted interpolation.
- A private globals dictionary organizes names but is not a sandbox.
- `exec` can add `__builtins__` to the namespace; do not infer a lack of capabilities from its apparent smallness.
- The type checker cannot see definitions hidden in a string.
- A type assertion then documents an assumption; it proves neither signature, safety, nor behavior.
- Do not reproduce an injection exercise in a real environment to justify this rule.

### Keep the Limits of Dynamic Classes Visible

- The classes generated locally in the corpus cannot be located by `pickle`.
- Ordinary serialization looks up a class by module and name; a name kept only in a local dictionary is not enough.
- An execution namespace without a suitable module identity can give the class a misleading identity.
- Do not conclude that every dynamic class is always impossible to serialize: test the mechanism actually provided.
- Do not promise `inspect.getsource` for code constructed in memory; source and runtime structure are different things.
- A requirement for persistence, distribution across processes, or tooling may justify an explicitly written class.

### Register and Mark Without a Metaclass

- `__init_subclass__` receives the new subclass and does not run for the base that defines it.
- Consume its keyword options, then forward the others with `super().__init_subclass__(**kwargs)`.
- Let an unknown option propagate rather than ignoring it; this preserves cooperation between bases.
- Define the registry contract: all classes, only leaves, or only explicitly eligible classes.
- For leaves, add the class and then remove its registered bases; also test an additional inheritance level.
- Keep registries for distinct families independent; do not accidentally share the same mutable container.
- A class that has not been imported is not created and does not register itself; explicitly arrange the required imports.
- A key based on `__name__` can collide; choose a domain key and a duplicate policy.
- To mark a method before the class exists, write metadata onto the function and then collect it in the hook.
- `vars(cls)` traverses only the class's own namespace: decide whether inherited marks should be merged or replaced.
- Functions collected this way are not automatically bound to an instance; calling them must supply the appropriate receiver.
- Marks describe the function; a counter or state that changes with each call belongs instead in a closure or a callable object.
- `functools.wraps` normally copies the function's dictionary; check decorator order if marks matter.

### Localize Constraint Enforcement

- An annotation does not validate assigned values; a runtime rule requires code that enforces it.
- `typing.final` expresses a static prohibition; its marker alone does not prevent subclassing at runtime.
- Runtime rejection can be implemented in `__init_subclass__`, if this exceptional need is genuinely required.
- The `override` marker, when available, likewise does not perform runtime checking by itself.
- `dataclass` actually generates methods; the checker separately reconstructs their static model.
- `dataclass_transform` announces generation behavior but produces no methods by itself.
- If a decorator advertises a constructor and frozen fields, it must actually construct and freeze them.
- Distinguish static markers, runtime generation modeled statically, and mechanisms that apply two independent checks.
- Do not generalize one checker's observed behavior to others: analysis of dynamic classes differs.
- Limit `Any`, casts, and suppressions to the dynamic boundary; they must not disable checking of the entire API.

### Design a Reusable Descriptor

- An object whose type defines `__get__`, `__set__`, or `__delete__` participates in the descriptor protocol.
- Binding a function to an instance is already a use of `__get__`.
- Use a property for an isolated attribute; a descriptor becomes useful when several attributes share the same rule.
- `__set_name__(owner, name)` supplies the name without having to repeat it when declaring each attribute.
- This hook can exist on an attribute that is not a descriptor.
- Store each instance's data on that instance, under a name distinct from the intercepted attribute.
- Reading the same attribute again from its own `__get__` would cause recursion.
- Validate before replacing the value so that a rejected assignment preserves the previous state.
- Handle `obj is None` in `__get__` to allow access through the class, often by returning the descriptor itself.
- A data descriptor with reading and writing takes precedence over the instance dictionary; a non-data read can be shadowed by it.
- Installing an attribute later by assignment is not class creation: do not assume another automatic call to `__set_name__`.
- Test storage, class access, and isolation between instances rather than only an accepted value.

### Reserve Metaclasses for Their Domain

- Their ordinary methods operate on the class object, not its instances; a `classmethod` does not have the same scope.
- A metaclass protocol method can make the class itself iterable or change its instance construction.
- `__prepare__`, defined as a class method, can supply a mapping that sees assignments during the body.
- This is when a duplicate can be detected before overwriting; a later hook cannot recover its history.
- Transform the name, bases, or namespace in `__new__` before delegating to actual construction.
- After that construction, modifying the old namespace dictionary no longer changes the class; act on the completed class.
- Preserve cooperative calls to the base wherever the protocol requires them.
- If `__call__` returns an already retained object without delegating to `type.__call__`, the ordinary constructors do not run again.
- This power is not sufficient justification for imposing a singleton or hidden global state.
- A common metaclass can apply a rule to classes without a common domain base, but adds coupling to their construction.
- Multiple inheritance requires a metaclass compatible with those of all bases; composing their hooks can remain complex.
- A metaclass conflict differs from a memory-layout conflict between built-in or slotted bases.
- Prefer composing a dictionary to inheriting simultaneously from `type` and `dict`.

### Inspect Without Confusing Reading and Execution

- Use `inspect.signature`, `getdoc`, and the `isclass`, `isfunction`, `ismethod` predicates for structured questions.
- `getmembers` can trigger dynamic accesses; prefer `getmembers_static` to avoid properties and descriptors.
- Do not turn this preference into a general sandbox guarantee: annotations and representations can still execute code.
- Account for missing signatures and the `TypeError` or `ValueError` raised by some built-in objects.
- An annotation without a value is not necessarily a bound member visible on the class; separate annotations from existing values.
- To combine base annotations, traverse the MRO in an order that lets derived declarations take precedence.
- Distinguish storage on the class from a `ClassVar` declaration; they are not equivalent tests.
- To limit noise, select the protocols of interest and compare their identity with inherited ones, without displaying everything by default.

### Adapt Annotations to the Version and Timing

- The corpus targets Python 3.15; do not copy its recent syntax or mechanisms into a 3.11 project without adaptation.
- Python 3.11 already provides the hooks, `dataclass_transform`, and `getmembers_static`, but not `annotationlib`.
- Do not assume the deferred annotation model of the 3.14/3.15 targets in Python 3.13.
- On those recent versions, use the available public `annotationlib` API to choose the requested format.
- `VALUE` requests resolved objects and can raise `NameError` during construction if a name does not exist yet.
- `FORWARDREF` keeps resolved parts and represents missing references; defer their resolution until the appropriate time.
- `STRING` is suitable for a textual description, not for code that actually expects classes.
- A format that avoids full resolution is not a security mechanism for untrusted annotations.
- Do not build a portable API on the internal annotation attributes displayed by the corpus's interpreter.

## Procedure

1. Describe the desired variation and explain why ordinary data is not enough; keep this decision verifiable.
2. Identify the target Python and checker, then the point when all required names and objects exist.
3. Choose the narrowest mechanism using the rules above; a metaclass must address a need not covered by simple hooks.
4. Define registry, validation, identity, inheritance, and serialization contracts before adding the transformation.
5. Implement a single dynamic boundary, without interpolated external source or globally disabled type checking.
6. Check phases, failure paths, and static promises against actual behavior.
7. Keep the solution only if it removes duplication or makes an invariant clearer than the explicit version.

## Pitfalls

- A hook that runs too late cannot recover definitions already overwritten in the namespace.
- A registry populated at import time may seem empty only because its modules have not been loaded.
- An injected class can be usable while remaining opaque to the checker, `pickle`, or source lookup.
- A descriptor that stores the value on itself unintentionally shares that value across all instances.
- A marker recognized by the checker is not runtime enforcement; a cast is never validation.
- Extending a metaclass can make previously ordinary multiple inheritance incompatible.

## Verification

- The hook choice matches the required phase and imposes no unjustified metaclass.
- Unknown options, duplicates, and invalid inputs fail explicitly.
- Registries remain independent, and their inheritance rules are tested.
- Descriptors preserve a value after rejection and do not mix up two instances.
- Reading a class and reading an instance each have an intended behavior.
- The statically advertised constructor and restrictions actually exist at runtime.
- Every serialization or source requirement has its own test, rather than being inferred from successful construction.
- Version compatibility is explicit; no 3.14/3.15 API is advertised as available in 3.11.
