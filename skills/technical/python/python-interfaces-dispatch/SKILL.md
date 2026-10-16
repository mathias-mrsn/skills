---
name: python-interfaces-dispatch
description: Adapt interfaces and choose Python dispatch.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Interfaces and Dispatch in Python

Original synthesis of Bruce Eckel's Thinking in Python, local corpus a8feb860.
The corpus targets Python 3.15 and later; specific version requirements are stated below.
The scope is interface interposition and operation selection, not general object construction.

## When to Use

- Interpose access control, lazy initialization or instrumentation without changing client calls.
- Connect an existing API to a different contract, simplify a subsystem or migrate an old interface.
- Choose an operation according to a type, a combination of types or operator protocols.
- Add external operations to a hierarchy without multiplying that hierarchy's methods.
- Do not introduce a dispatch mechanism if an ordinary function already covers all values.

## Philosophy

Indirection must hide a real variation, not merely add a layer.
Name the wrapper after what is lost when it is removed: control, behavior, compatibility or simplicity.
In Python, functions, dictionaries and structural protocols often replace the hierarchies required in other languages.
An object that forwards calls forwards neither its type identity nor all the guarantees of its implementation.

## Rules

### Distinguish Intent from Structure

- A Proxy controls when and whether a call reaches an implementation: remote access, lazy construction, authorization or call tracking.
- Strictly speaking, Proxy and Decorator preserve the interface; Decorator adds behavior, Adapter makes two interfaces compatible.
- The book also uses Surrogate in a looser sense: the intent to replace the implementation takes precedence over an identical interface.
- A Facade reduces the number of exposed concepts and hides their assembly; simple renaming does not justify it.
- A Surrogate with an interchangeable implementation changes the behavior of the same calls; this mechanism becomes State when that variation is its intent.
- Document the interface actually promised rather than claiming that the wrapper is “transparent”.

### Choose Verifiable Forwarding

- Prefer explicit methods for a small, stable public interface: names, signatures and return values remain visible to the reader and static checker.
- Describe the implementation's requirements with a `Protocol` if inheritance adds nothing; an ABC additionally enforces abstract methods at construction.
- A runtime-checkable protocol checks for the presence of members, not the compatibility of their signatures.
- Reserve `__getattr__` for generic forwarding of missing names; attributes already present on the proxy always win.
- Do not confuse this fallback with `__getattribute__`, which intercepts every read and requires explicitly bypassing interception for internal accesses.
- An `Any` return from `__getattr__` lets typos and malformed calls through; annotating the implementation does not restore checks on the proxy.
- A universal proxy gains generality at the expense of its contract; do not widen an entire API to `Any` to hide this trade-off.
- Reserve an internal namespace; name mangling limits collisions without providing security protection.

### Respect Python Protocols and Reconstruction

- Define the necessary special methods on the type: `len`, indexing, iteration, operators and representation cannot be inferred from ordinary forwarding alone.
- Test protocol syntax, not just a direct call to its special method: `p.__len__()` may succeed while `len(p)` fails.
- When `object` already provides a special method, the proxy may respond through it without an error and without reaching the implementation.
- Writes do not go through `__getattr__`: an ordinary assignment creates a proxy attribute that subsequently shadows the implementation's attribute.
- If writes must be forwarded, define a `__setattr__` policy distinguishing internal storage from delegated attributes.
- Initialize internal storage with `object.__setattr__` when the write hook is already active; otherwise the first assignment may delegate before the target exists.
- Names expressed as strings do not undergo name mangling; do not mix a double-underscore internal name with its unmangled string.
- Prevent `__getattr__` from calling itself for a missing internal attribute: guard private names or read internally and directly through `object.__getattribute__`.
- Make this case fail with an `AttributeError` naming the attribute, rather than recursing until `RecursionError`.
- If copying or serialization is promised, test reconstruction: it may create an instance without executing `__init__` and then look for `__setstate__`.
- Frozen dataclasses with slots have suitable reconstruction hooks; do not attribute this property to all wrapper classes.

### Do Not Confuse Access, Identity and Security

- Delegation does not make the proxy an instance of the wrapped class; do not base a consumer on this assumption.
- Since Python 3.12, runtime `Protocol` checking uses static inspection that does not trigger `__getattr__`.
- A proxy that provides its methods only dynamically may therefore satisfy `hasattr` and fail the protocol check.
- Virtual registration with an ABC or a `__class__` property does not prove conformance; prefer an explicit interface if checking is required.
- `hasattr` absorbs only `AttributeError`; a `PermissionError` raised by an authorization proxy also propagates during introspection.
- An authorization proxy protects against accidental use, not against a client that can deliberately reach the internal target.
- `weakref.proxy` forwards to a weakly held target and raises `ReferenceError` after it disappears; it is neither a lazy proxy nor access control.
- A lazy proxy constructs the target on first demand and then reuses it; check accesses that must remain cost-free and behavior when construction fails.
- Call instrumentation increments at call time, not when an attribute is read; also forward the result and exceptions.
- Recreating a wrapper on every read changes its identity and may hide its name; do not promise stable identity for generated methods.
- An unsynchronized target change does not make a sequence of multiple calls atomic: another thread may split it across two implementations.

### Adapt and Simplify Without Breaking Clients

- Compare three locations: a wrapper using composition, adaptation at the point of use or a subclass of the adapted object.
- Composition accepts a target supplied at runtime and separates the interfaces; inheritance fixes the adapted class and also exposes its existing interface.
- Moving adaptation into the consumer couples it to the old form; do so only if that knowledge genuinely belongs there.
- A small adapter can declare the few new operations and delegate the rest; the limitations of special methods, writes and copies remain the same.
- Name the target contract with a `Protocol` when only the presence of methods matters; require no unnecessary common base.
- An override may accept more inputs, but must never reject an input allowed by the base method.
- Preserve the names of parameters usable as keywords; only positional-only parameters can be renamed without breaking that usage.
- Prefer a Facade implemented as a module, or a package's public exports, to a class containing only static methods.
- Hide assembly order and internal dependencies; underscore-prefixed names and `__all__` express a convention, not an access lock.
- Accommodate advanced needs without re-exporting the entire subsystem: too few names force bypasses, too many remove the simplification.
- To replace an interface you own, first provide its replacement and keep the old one functional during migration.
- With Python 3.13+, `warnings.deprecated` marks functions, methods and classes; before that version, its equivalent requires `typing_extensions`.
- Provide a message stating what to call instead; a marked class warns on construction and subclass creation.
- Explicitly enable `DeprecationWarning` in tests: these warnings are often hidden during normal execution.
- Marking a single overload produces only a static diagnostic; overload declarations do not survive as executable variants.

### Resolve a Type or a Combination of Types

- An ordinary method call chooses behavior through the receiver; it does not automatically select according to all its arguments.
- Use `functools.singledispatch` for an extensible external operation based on the first argument; each operation keeps its own registry.
- Registration by annotation associates the function with the annotated type; union annotations have been supported since Python 3.11.
- Subclasses resolve to a registered ancestor; inspect `registry` and `dispatch(cls)` to verify the expected selection.
- The base function is registered under `object`, even if its parameter has a more restrictive annotation.
- Choose a semantically valid default or raise an explicit failure; a plausible default may hide a forgotten registration or an out-of-domain type.
- Do not assume that all static checkers restrict dispatcher calls identically; also check the runtime contract.
- With `singledispatchmethod`, registered selection uses the first argument other than `self` or `cls`, not the receiver-argument pair.
- An inherited dispatcher is shared: registering through two subclasses changes the same registry and may silently replace the same entry.
- To distinguish receivers as well, give each relevant class a separate dispatcher or choose an explicit combination table.
- A table indexed by `(type(a), type(b))` centralizes combinations; each cell can contain a value or a function reading both objects' state.
- This table compares exact classes without traversing their MRO; a subclass requires its own entries and a missing pair fails at lookup.
- A `match` using class patterns accepts subclasses but keeps cases in a closed block; case order becomes a priority.
- Prefer method-based double dispatch if a subclass must override one combination and inherit the others; an exact table does not provide this inheritance.
- Specify which participant the result refers to and test both orders; an override on only one side may make the interaction inconsistent.
- Declare the required methods through a protocol or ABC rather than letting `Any` hide a missing combination.

### Use Operators and Visitor Appropriately

- For an unsupported operand, return `NotImplemented`; raising `TypeError` or `NotImplementedError` interrupts the computation without allowing the fallback.
- For different types, refusal by `__add__` allows an attempt at `__radd__` on the other operand; refusal on both sides results in `TypeError`.
- When the right-hand operand is a subclass with a different reflected method, that method takes priority over the left-hand method.
- For two instances of the same type, do not count on the reflected method as a second attempt.
- In-place forms such as `__iadd__` are distinct from ordinary operations; do not conflate them in tests.
- For a noncommutative operation, preserve operand order in its reflected method.
- An operator's return annotation describes the useful result; the sentinel passed to the interpreter does not justify making all results `Any`.
- Visitor aims to add external operations, not necessarily to solve the general problem of two unknown types.
- Prefer one `singledispatch` function per operation: the call site chooses the operation, leaving only one type to resolve at runtime.
- Classic Visitor requires an `accept` method already to be available; it remains suitable for a framework that requires it or an object that drives the traversal itself.
- Two definitions of `visit` do not overload the method in Python; the last replaces the previous one and `@overload` adds no runtime dispatch.
- Selection through a dynamically constructed name, such as `visit_` followed by the class name, escapes static checking of the targeted method.

## Procedure

1. List the client calls to preserve, their signatures and the syntactic protocols actually used; obtain an observable contract.
2. Identify what varies and choose the smallest necessary wrapper or function; explain what removing it would lose.
3. Explicitly decide on forwarding for reads, writes and special methods, and the promised identity and reconstruction behavior.
4. For dispatch, write the matrix of accepted types, including subtypes, and choose a default, failure or inheritance for each case.
5. Separate registrations or the table from executable demonstrations; verify that a plain import executes no client scenario.
6. Add compatibility, subclass and error tests before replacing the old entry point; make the expected warnings visible.

## Pitfalls

- Delegation that works for two methods proves neither `len(proxy)`, nor a write, nor a type check.
- An internal name missing during a copy can turn a simple lookup into infinite recursion.
- A shared method registry sometimes produces a credible result attributed to the wrong receiver.
- Replacing an exact table with inherited dispatch changes the covered domain, not just code organization.
- A facade that exposes all its details or a migration that immediately removes the old method negates its own benefit.

## Verification

- Check arguments, return value, called target and exception propagation for each adapted public operation.
- Exercise special syntax, internal name collisions, writing and copying if they are part of the contract.
- Test every accepted combination in both orders, an absent type, a subtype and specific overrides.
- Check the effective registry and dispatch default; do not limit testing to the result of a happy-path case.
- Verify reflected priority, refusal through a sentinel and final operator failure.
- Confirm that old calls remain valid and that the recommended replacement appears in the captured warning.
