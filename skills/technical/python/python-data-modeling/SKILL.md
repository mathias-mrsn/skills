---
name: python-data-modeling
description: Model data and its invariants in Python.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Data and Invariants in Python

## When to Use

- Choose a representation for a record, multiple return values, or a data transfer object.
- Replace scattered checks with domain values checked at construction.
- Design normalization, immutability, replacement, copying, and reconstruction after serialization.
- Examine what a dataclass, a named tuple, or an annotated dictionary actually guarantees.
- Do not impose a wrapper object on every scalar without a business benefit or an examination of the cost.

## Philosophy

A useful model describes the set of admissible values and the operations that preserve that set.
Naming a class is not enough: examine every way to construct, modify, and restore its instances.
Transforming raw input into a checked value carries a guarantee; a validation boolean leaves the raw data unchanged.
Immutability reduces the paths to monitor, but its depth and limitations must remain explicit.
Separate the transport shape from the business meaning, even when both start with the same fields.
This original synthesis draws on Bruce Eckel, Thinking in Python, corpus a8feb860.

## Rules

### Define Invariants Before Fields

- State the legal values, bounds, and relationships between fields before selecting a structure.
- Distinguish the representation type, such as `int`, from the business subset actually allowed.
- Identify every input boundary: decoded text, database row, form, file, or dynamic public argument.
- Construct checked values at those boundaries; do not circulate raw data accompanied by a verbal promise of validity.
- Return domain values when the result must preserve the invariant; returning a scalar relinquishes that guarantee.
- Compose small validated types, then add constraints between their values to the enclosing record.
- Valid components are not enough if their combination can be inconsistent.
- Do not confuse an example of a minimal check with a complete specification of an address, a name, or a date.

### Choose the Least Misleading Representation

- Use `SimpleNamespace` for an ad hoc bundle of attributes whose names may vary; accept the loss of static checking of those names.
- Do not reimplement an attribute bag by manipulating `__dict__` when `SimpleNamespace` meets the need.
- Choose a dataclass for declared fields, a readable representation, and value equality within the same type.
- Keep a dataclass mutable when reassignments are part of the contract; choose the frozen variant for stable values.
- Choose `NamedTuple` when tuple behavior is actually required: unpacking, indexing, or existing compatibility.
- Prefer a frozen dataclass when two records with the same shape must remain values with different meanings.
- Keep a dictionary with `TypedDict` if the dictionary shape is the contract; this marking validates nothing at runtime.
- A DTO gives names to exchanged data; it does not inherently require networking, persistence, or the absence of behavior.
- For multiple results, favor named access when swapping two positions could go unnoticed.

### Understand What a Dataclass Generates

- Annotations determine the fields; they do not check the values received by the constructor.
- A bare annotation on an ordinary class initializes no attribute; a dataclass's generated constructor performs the assignments.
- A dataclass normally produces `__init__`, `__repr__`, and `__eq__`; examine the options and methods already defined before relying on them.
- A dataclass is mutable by default and is not automatically orderable.
- Generated equality requires the same concrete type; do not inadvertently replace it with a comparison of anonymous tuples.
- Enable `order=True` only if lexicographic field order is indeed the desired business ordering.
- A field with a default value remains an instance field; its initial presence on the class does not make it a `ClassVar`.
- A real `ClassVar` is excluded from the fields and the generated constructor; a declaration without an assignment gives it no value.
- Use required keyword-only fields with `kw_only=True` or `KW_ONLY` when several positional arguments would be ambiguous.
- Examine the order of required and defaulted fields, including inherited ones; keyword-only parameters can remove some ordering constraints.

### Construct Without Letting an Illegal Value Through

- Place checks that must follow field assignment by the generated initializer in `__post_init__`.
- If the constructor is handwritten, do not assume it will automatically call `__post_init__`.
- Explicitly raise an exception for invalid input; `assert` can be removed by optimized execution.
- Also check actual types at an untrusted boundary; a range check may accept a float despite an integer annotation.
- Decide explicitly whether a boolean is an admissible integer: `bool` is a subclass of `int`.
- If the domain requires a strict integer, do not settle for `isinstance(value, int)`, which accepts `True` and `False`.
- Check nested structures, not just their outer container, when input may come from dynamic code.
- Give a construction error structured information about the field and the reason; do not force callers to parse its text.
- `check` and `TypeFailure` are tools defined in the corpus's illustrations, not built-in functions to import implicitly.
- If an exception is itself a dataclass, examine `eq=False` to preserve expected identity comparison and hashability.

### Normalize Without Changing Meaning

- Decide which input differences represent the same value and which must cause rejection.
- Normalize deterministically, then check the chosen representation; retain explicit rejection when correction would be ambiguous.
- On a frozen dataclass, reserve `object.__setattr__` for targeted normalization during construction.
- This mechanism also bypasses freezing outside the constructor; freezing prevents ordinary mistakes, not a determined caller.
- Do not turn an illustrative cleanup rule into universal domain normalization.
- If the model remains mutable, compute and check the new state before replacing the old one.
- An exception after a mutation does not restore the previous state; guarantee a valid state even on the failure path.

### Control Freezing, Sharing, and Defaults

- `frozen=True` forbids ordinary attribute assignments; a contained list or dictionary can still be modified.
- Use immutable components when the invariant must last without further checking, or adopt an explicit policy of controlled mutations.
- Copy or convert mutable input if its owner could modify the data retained by the object after construction.
- A frozen dataclass is hashable only if the fields participating in hashing are hashable; test the real case rather than inferring it from the decorator.
- Do not force hashing to hide mutable state that would change a key already placed in a dictionary.
- Use `field(default_factory=...)` for each default value that must be fresh for every instance.
- Pass the callable without calling it; it must be able to produce the value with no arguments.
- Rejection of certain default values is based on their unhashability, not on a general proof of mutability.
- A mutable, hashable custom object can therefore be shared silently; do not rely solely on rejection by the decorator.
- Check that the factory produces the expected type and contents; checkers do not all analyze this connection in the same way.
- Two constructions must have independent containers unless sharing is deliberate and documented by the model.

### Use a Finite Set and Named Tuples Appropriately

- Use `Enum` for a small closed family of named values; a dataclass is better suited to open-ended structured values.
- Enum members with the same value become aliases; if their identities must remain distinct, give them distinct values.
- Do not assume the value carried by a member is a simple identifier if it contains several components.
- A `NamedTuple` retains `tuple`'s positional equality, hashing, and ordering, even between records with different names and meanings.
- Two equal named tuples can therefore occupy the same dictionary key; choose a distinct type if that equivalence is wrong for the business domain.
- Unpacking depends on order; renaming local variables does not correct a reversal.
- The attributes `_fields`, `_asdict`, and `_replace` are public named tuple mechanisms despite their prefix.
- A named tuple remains shallowly immutable; a list field remains mutable and prevents hashing the tuple.
- `typing.NamedTuple` does not allow the usual construction methods to be redefined within it to enforce validation.
- An adjacent factory can be bypassed; a validating subclass can still be bypassed through the replacement mechanism.
- Do not choose this form if validity depends on an unavoidable path through the constructor.

### Reconstruct, Copy, and Inherit Deliberately

- `dataclasses.replace` reconstructs through the constructor and reruns a conventional dataclass's checks.
- Examine non-init fields and derived state: replacement is not a blind copy of all attributes.
- `copy.replace`, available since Python 3.13, offers a more general protocol; check the types supported by the project's version.
- For a custom type, make `__replace__` reconstruct from the modified arguments rather than reinjecting unchecked state.
- Ordinary copying and restoration mechanisms can bypass `__init__` and `__post_init__`; custom hooks can change this behavior.
- A copy of a legal original does not validate old, altered, or externally received state.
- A derived dataclass's generated initializer does not call an ordinary base class's initializer; explicitly trigger the necessary initialization.
- Before making that call from `__post_init__`, check that it does not replace the storage of fields already assigned.
- Between dataclasses, inherited fields participate in the generated constructor; also ensure checks are chained if a hook is overridden.
- Do not mix frozen and non-frozen dataclasses in the same hierarchy; prefer composition if their policies conflict.

### Serialize Without Confusing Representation and Validation

- `asdict` and `astuple` traverse nested dataclasses and copy elements according to their rules; they are not free shallow views.
- `json.dumps` cannot serialize a dataclass directly; define the output representation and handle values still incompatible with JSON.
- A named tuple is encoded as a JSON array and loses its names; call `_asdict` if named keys are part of the format.
- On decoding, check the shape, keys, and types, then reconstruct every domain value through its checked path.
- A successful round trip on legal data does not demonstrate that the decoder rejects all illegal data.
- For an evolving persistent format, plan for versioning and migration; restoring an old object may bypass new checks.
- Do not load an untrusted pickle; the mechanism's simplicity does not turn its contents into safe data.
- A validation library can lighten complex conversions, but its adoption must respect the project's dependencies and versions.

## Procedure

1. Describe the legal set, invalid combinations, and input boundaries; distinguish representation from business meaning.
2. Choose a dictionary, namespace, named tuple, Enum, or dataclass, explicitly stating the behaviors accepted and those to avoid.
3. Centralize checks and normalization, then determine whether the invariant survives mutations and component sharing.
4. Audit direct construction, factories, inheritance, replacement, copying, and restoration; note the paths that do not revalidate.
5. Design the transport format and its checked reconstruction; make boundary errors usable by the caller.
6. Test the claimed guarantees and measure allocations or reconstructions if this model touches a hot path.

## Pitfalls

- Statically typed data may remain illegal in the business domain; a frozen dataclass can contain mutable objects.
- The model's cost includes additional objects, attribute access, and revalidation during replacement; measure before generalizing.
- A property without a setter does not prevent an internal method from corrupting the underlying field.
- `__repr__` and equality may omit an old restored attribute: a correct appearance does not prove a correct persistent format.
- No guarantee should implicitly extend to bypass mechanisms, uncontrolled code, or an untested version.

## Verification

- Test boundary values, wrong types, booleans, missing fields, and inconsistencies between components.
- Confirm rejection at direct construction and replacement; check that the original remains valid after a failure.
- Construct two instances and check the independence of defaults and the absence of unwanted mutable aliasing.
- Test equality between distinct types, ordering if any, hashing, and unpacking according to the chosen contract.
- Test illegal decoding, output format, old state, and migration, not just a nominal round trip.
- Report the paths actually exercised, compatible versions, and measured cost without promising absolute immutability.
