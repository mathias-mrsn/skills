---
name: python-object-design
description: Design objects, state and substitutable contracts.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Designing Objects and Their Contracts

## When to Use

- Choose between data and functions, a stateful class, composition and inheritance.
- Diagnose shared attributes, shadowing, incomplete initialization or a stale cache.
- Define a polymorphic interface and verify its static and behavioral guarantees.
- Do not create a class merely to house a function, or inherit only to obtain a few methods.

## Philosophy

- Start with functions and data; introduce an object when coherent state and its operations must remain together.
- Prefer immutable data, functions, composition and protocols to encapsulation mechanisms and deep hierarchies.
- These are selection criteria, not a ban on objects: a namespace, method discovery and state management can justify a class.
- A contract includes the meaning of values, mutations, errors and termination; a correct signature guarantees only part of it.
- Respect the project's minimum version; the self-contained example below requires Python 3.11+ and only the standard library.

Original synthesis based on Bruce Eckel, Thinking in Python, corpus a8feb860 (CC BY-NC-ND 4.0).

## Rules

### Class, Initialization and Operations

- Distinguish `__new__`, which constructs the instance, from `__init__`, which initializes it; customize construction only for a concrete need.
- Declare `self` as the first parameter of instance methods and access its attributes explicitly through `self`.
- A bound method carries its instance; when called through the class, the function still requires that instance as its first explicit argument.
- Initialize all necessary attributes before publishing the object; an annotation alone does not replace an assignment.
- If the subclass defines its own `__init__`, explicitly call the required base initialization; Python does not add it automatically.
- A subclass without its own `__init__` inherits its base's; do not rewrite an identical constructor without a reason.
- Separate construction from starting a process: an overridden method called too early can read subclass attributes that do not yet exist.
- Prefer a free function if the operation requires neither owned state nor privileged access and must serve multiple types.
- Choose a method for completion-based discovery, a local invariant or operations that regularly modify the same state.
- A function imported into a class body can become a method and receive `self`; avoid this trick when a function or explicit component is clearer.
- Choose `staticmethod` for an operation related to the class's domain but using neither the instance nor the class; a module function remains an alternative.
- Choose `classmethod` when the effective class is needed; conventionally use `cls`.
- In an inheritable alternative constructor, construct through `cls(...)`, not the base's fixed name; check that subclasses accept this construction.

### Inheritance, MRO and Substitution

- Inheriting an implementation couples the subclass to the base's details; a common interface alone does not require this inheritance.
- A `self.method()` call inside an inherited method looks up the method from the instance's effective type, not from the class containing the calling body.
- `super()` follows the rest of the object's MRO; it is not always a call to the most textually obvious parent.
- Inspect `Class.__mro__` in a conflict and before multiple inheritance; base order participates in C3 linearization.
- In a diamond, resolution is deterministic but can be difficult to follow; prefer several independent protocols if only the interface is wanted.
- To preserve existing cooperative behavior, use `super()` and compatible signatures; avoid explicitly calling several bases and risking repetition of an ancestor.
- Apply `typing.override`, available since Python 3.12, to intentional overrides; do not implicitly import it on a 3.11 target.
- A checker can detect a nonexistent name and an incompatible signature; at runtime, `override` blocks neither a misspelled name nor a behavioral violation.
- Without a marker, a typo creates a perfectly legal new method; constructors and common dunders can remain without an explicit marker.
- Require a subclass to work wherever the base is promised: accept at least its inputs, provide usable results and add no surprising failures.
- A new limit, an additional effect or an operation made inert can violate this contract despite identical annotations.
- Run the same contract tests on the base and subtypes; do not confuse checker approval with satisfaction of the substitution principle.

### Class and Instance Attributes

- An assignment in an ordinary class body creates a shared class attribute, not a default automatically copied into each object.
- For an ordinary attribute, reading searches the instance, then the class and its bases; writing through `self` generally creates an instance attribute that shadows the class value.
- Inspect `vars(instance)` and `vars(Class)` to locate storage; the class dictionary is exposed as a view that is not directly modifiable.
- The two-dictionary model has exceptions: properties and other descriptors can intercept access, and `__slots__` can remove the instance dictionary.
- A property owns its name: its getter and setter control access, even if an instance dictionary contains a key with the same name.
- Methods also live on the class; an instance assignment with the same name can shadow a method for that object only.
- Without an available instance dictionary, an ordinary class name that is not otherwise writable cannot be shadowed by an arbitrary write.
- Deleting an instance attribute exposes the inherited value again; deleting it a second time does not delete the class attribute.
- Mutating a list obtained by falling back to the class creates no instance attribute: all objects sharing the list see the mutation.
- A `+=` requires analyzing the type: an integer produces a reassignment, whereas a list can first be modified in place.
- For state specific to each object, assign in `__init__` and construct mutable objects at each creation.
- A mutable constructor default reintroduces sharing; use a marker and then construct in the body, with an identity check.
- With `dataclass`, annotate real fields and use `field(default_factory=list)` or another factory for mutable values.
- An unannotated assignment in a dataclass remains a class attribute, excluded from the generated constructor.
- An annotated field with a default can leave a value on the class, but the generated constructor initializes each instance separately.

### Declaring Intentional Sharing

- Annotate a genuinely common counter, registry or state with `ClassVar[T]`; the checker can then reject assignment through an instance.
- `ClassVar` creates neither storage, a value nor a runtime write barrier; `dataclass` nevertheless uses it to exclude that name from its generated fields.
- `name: T` and `name: ClassVar[T]` without a value create no attribute; access before assignment can raise `AttributeError` even if the checker accepts the declaration.
- A base declaring an attribute for its subclasses to provide does not automatically force them to create it; verify this contract explicitly.
- Initialization and attribute-override diagnostics depend on the checker: do not turn local silence into a language guarantee.
- Repeating `ClassVar` on an override can preserve the intention with checkers that lose the inherited annotation.
- `self.counter += 1` on a class integer generally creates an instance counter; modify the class name to count globally.
- A subclass reads its base's value until an assignment creates its own value; its siblings do not share this new binding.
- `type(self).counter += 1` and `cls.counter += 1` can therefore separate counters by subclass, starting from the inherited value, not zero.
- For a total covering all subtypes, write through the common owner's name; for separate totals, explicitly initialize each subclass's policy.
- Mutation of an inherited registry can remain shared, while its reassignment on a subclass creates an independent table.
- For a class constant, use `Final` according to the supported typing contract; it statically forbids reassignment, not deep mutation of a contained object.

### Properties, Cache and Representation

- Start with a simple attribute; add a property when computation or validation becomes necessary, without changing client read syntax.
- A property without a setter rejects reassignment; a setter must validate before storing and use distinct storage, such as `_value`.
- Do not read or reassign the property's name from its own accessor: this calls that accessor repeatedly until `RecursionError`.
- Read `object.property` without parentheses; `object.property()` calls the result, not the getter.
- Prefer a method to a write-only property; its intent is an operation, not a readable value.
- An ordinary property recomputes on every read; use `cached_property` only if the result remains stable, or if explicit invalidation is genuinely controlled.
- `cached_property` stores in the instance's `__dict__`; slots without that dictionary make this storage impossible.
- Mutating inputs does not refresh the cache; deleting the cached attribute causes recomputation on the next read.
- Provide an informative `__repr__` to diagnose the value; aim for an unambiguous form, ideally reconstructible when that makes sense.
- Add `__str__` only for different user-facing display; `str` and `print` fall back to `repr`, not the reverse.
- Containers represent their elements with `repr`; in an f-string, `{object}` and `{object!r}` do not choose the same representation.
- Do not unintentionally expose sensitive internal data in a generated `repr`; readability must not contradict the intended boundary.

### Encapsulation, Immutability and Composition

- An underscore signals an internal detail; it is not access control.
- A getter returning an internal list or mutable object passes on its reference; a property without a setter does not protect its elements.
- If defensive copies are necessary, copy on input too: protecting only returned values leaves the caller's references active.
- A shallow copy isolates the container but shares its elements; compare recursive copying and immutable values according to their structure and cost.
- `dataclass(frozen=True)` normally forbids field reassignment, not mutation of their objects; make the entire structure to be shared immutable.
- A tuple of lists remains mutable through its elements; a frozen dataclass is hashable only if the fields used by its hash are also hashable.
- Immutability reduces mutation-protection mechanisms but does not hide representation: a public field still commits to its visible type.
- Composing a type from other types preserves their independent uses and makes dependencies visible; an immutable update may require rebuilding enclosing values.
- Prefer delegation to adapt a component; expose only the desired operations rather than all those of a base.
- Do not assume that an inherited method calls another overridden method: `list.extend` is not required to go through `append`.
- Composition does not prevent bad delegation, but localizes its logic in the class to examine instead of depending on base internals.

### Interfaces and Type Variation

- Choose an `ABC` with `abstractmethod` if nominal membership and a common implementation are wanted; instantiation requires the abstract methods, not their correctness.
- If the entire hierarchy must remain without a dictionary, also consider the bases' slots: a nonslotted base can provide a `__dict__` to its descendants.
- Duck typing calls operations directly and discovers incompatibilities at runtime; `Any` largely disables static checking, unlike `object`.
- Prefer a minimal `Protocol` to describe the required shape without imposing inheritance or modifying library types.
- Declare a read-only property in the protocol if the client only needs to read; an ordinary attribute annotation also promises writing.
- A class can satisfy several protocols without a diamond; in exchange, its code does not necessarily declare every protocol it satisfies.
- Names and signatures do not convey meaning: distinguish price from weight through types and a contract rather than an ambiguous `total() -> float` method.
- `NewType` differentiates concepts for the checker but constructs neither a wrapper nor runtime validation; a validated data type can provide the latter.
- Do not use `isinstance` on an ordinary protocol; `runtime_checkable` permits a weaker check that proves neither signatures nor behavior.
- For a closed set of variants and frequently added operations, compare a union of immutable data and functions using `match` with polymorphic methods.
- For frequent new types, a polymorphic interface localizes their addition; for frequent new operations, a function on the union avoids modifying every class.
- `match` requires Python 3.10+; `typing.assert_never`, available since 3.11, makes an uncovered residual case visible to the checker if it checks this exhaustiveness.
- A generic implementation can serve multiple types without branching; `overload` describes several signatures but only the final undecorated definition executes.
- `singledispatch`, by contrast, selects an implementation registered by type; do not mistake `overload` declarations for runtime dispatch.
- Aliases with the `type` statement and type parameters in brackets require Python 3.12+; retain earlier syntax when the project needs it.
- A Null Object centralizes neutral behavior if all clients handle absence the same way; a stateless neutral object can be shared as a default.
- If absence is information or requires different reactions, retain an optional type or an explicit failure result: do not silence it.

## Procedure

1. Write the invariants, state owners, client operations and axes of variation; check whether a function and data suffice.
2. Choose mutability and the representation boundary; justify every class and any implementation base.
3. Locate each assignment: instance, owning class or subclass; declare sharing and actually initialize attributes.
4. Define the minimal contract, then test each subtype and adapter against that same behavior, not just its signature.
5. Verify read/write access, sharing, copies, cache and representations; run existing checks on the target version.

### Self-contained Example: Owned State, Immutable View and Minimal Contract

```python
from collections.abc import Iterable
from typing import ClassVar, Protocol

class HasLabels(Protocol):
    @property
    def labels(self) -> tuple[str, ...]: ...

class LabelBox:
    created: ClassVar[int] = 0

    def __init__(self, labels: Iterable[str] = ()) -> None:
        self._labels = list(labels)
        LabelBox.created += 1

    @property
    def labels(self) -> tuple[str, ...]:
        return tuple(self._labels)

    def add(self, label: str) -> None:
        if not label:
            raise ValueError("empty label")
        self._labels.append(label)

    @classmethod
    def named(cls, label: str):
        return cls((label,))

class SpecialBox(LabelBox):
    pass

def describe(box: HasLabels) -> str:
    return ", ".join(box.labels)

source = ["amber"]
a = LabelBox(source)
b = SpecialBox.named("blue")
source.append("external")
snapshot = a.labels
a.add("green")
assert snapshot == ("amber",)
assert describe(a) == "amber, green" and describe(b) == "blue"
assert isinstance(b, SpecialBox) and LabelBox.created == 2
assert "created" not in vars(a) and "created" not in vars(SpecialBox)
try:
    a.add("")
except ValueError:
    pass
else:
    raise AssertionError("empty label accepted")
assert a.labels == ("amber", "green")
```

## Pitfalls

- Confusing the presence of an annotation with the presence of storage, `ClassVar` with forced sharing, or freezing with deep immutability.
- Treating the dictionary model as absolute despite properties, slots or other descriptors.
- Inheriting to count or intercept a single operation while forgetting the base's other mutation paths.
- Replacing meaningful absence with a neutral object, or accepting a structural shape without checking its meaning.

## Verification

- Create at least two instances and a subclass; distinguish mutation, reassignment and shadowing through their actual storage.
- Test every public path that modifies an invariant, including inherited or delegated methods.
- Mutate input data and returned values to prove the claimed isolation; also examine nested objects.
- Verify alternative construction, errors, initialization order, cache freshness and representations in containers.
- Separate runtime results, diagnostics from the checker actually run and behavioral commitments still to test.
