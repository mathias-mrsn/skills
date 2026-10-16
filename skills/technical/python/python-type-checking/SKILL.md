---
name: python-type-checking
description: Verify type contracts in Python.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Type Contracts in Python

## When to Use

- Annotate a public interface, exchanged data, or a generic abstraction.
- Diagnose a checker's rejection without diluting the contract with `Any` or suppressions.
- Choose between nominal inheritance, a structural protocol, and runtime data checking.
- Clarify the limits of a static guarantee during a review or a gradual migration.
- Do not present this work as input validation, a proof of correctness, or a replacement for tests.

## Philosophy

An annotation makes an assumption between a value's producer and its consumer visible.
Its value increases when those two places are far apart; repeating the type of an obvious local adds little.
Gradual typing lets you improve useful boundaries without converting the entire program at once.
The checker checks a model of the program, not all its possible states or the truth of external data.
Favor type relationships that explain the code over code rearranged to satisfy the tool artificially.
This original synthesis draws on Bruce Eckel, Thinking in Python, corpus a8feb860.

## Rules

### Choose the Checking Framework

- Identify the project's minimum Python version, checker, checker version, and configuration.
- Respect the tool already adopted; `ty` is the corpus's tool, not a mandatory migration.
- Run the checker separately from Python: the presence of annotations does not prove it has run.
- Do not turn the result of a particular checker into a universal language rule.
- Prefer syntax available throughout the supported version range, not just on the development machine.
- The `type` statement and type parameters in square brackets require Python 3.12; defaults for those parameters require Python 3.13.
- On a Python 3.11 codebase, retain compatible forms based on `TypeVar`, `Generic`, and `ParamSpec` as needed.
- Check the availability of newer names, especially `TypeIs`, `ReadOnly`, and `override`, before introducing them.

### Annotate Where the Contract Matters

- Describe parameters, returns, public attributes, and values crossing module boundaries; leave obvious locals to inference.
- Annotate initially empty collections when inference does not express the intended element type.
- Write `-> None` for an operation with no useful result, especially an initializer.
- Distinguish a tuple with different positional types, `tuple[A, B]`, from a homogeneous variable-length tuple, `tuple[T, ...]`.
- Choose `Iterable[T]` for simple consumption, `Iterator[T]` for a cursor, and `Sequence[T]` when indexing is necessary.
- Do not promise a second traversal because a value is annotated `Iterable`: a generator may already be exhausted.
- Use `Mapping[K, V]` for dictionary reading without requiring the concrete mutable representation.
- An abstract read interface limits the consumer's operations; it does not freeze the object for its other holders.

### Keep Unknown Areas Visible

- Prefer `object` when any value is acceptable but its behavior still needs to be established.
- Reserve `Any` for genuinely dynamic boundaries: it permits operations without checking them and propagates to results.
- An unspecified type parameter may become `Unknown` or `Any` depending on the tool; the absence of a diagnostic is not enough.
- Use `reveal_type` to inspect inference and `assert_type` to express an expectation checked by the tool.
- A `cast` neither tests nor converts the value: justify it with a property already established independently.
- Limit suppressions to the necessary line and diagnostic; explain the observed limitation and retain a test protecting the behavior.
- Do not turn data from JSON into trustworthy values merely by annotating the decoded result.

### Narrow Alternatives Before Using Them

- Use `X | None` for absence with no reason to carry, and a union of variants for genuine alternatives.
- Test `is not None` when the empty string, zero, or an empty collection remain legitimate values.
- Narrow through identity, equality, `isinstance`, or patterns the checker understands before an operation specific to a variant.
- Copy a mutable attribute into a local before narrowing it if an intervening call may reassign that attribute.
- The local protects against that reassignment, not against internal mutation of the object it references.
- Reexamine an attribute after a call that may change its state; the checker may retain information that has become false.
- `TypeGuard` narrows the true branch; `TypeIs` narrows both branches and requires a relationship compatible with the input type.
- A narrowing predicate's body must actually establish what its annotation claims; the annotation does not prove its implementation.
- For a closed union, end impossible cases with `assert_never` so that adding a variant makes the omission visible.
- Distinguish static checking from execution: if that path is reached, `assert_never` actually raises an exception.

### Name Without Inventing Guarantees

- Introduce an alias for a recurring composite shape, not to pass an ordinary integer off as a distinct identifier.
- An alias preserves the compatibility of its original type; `NewType` expresses an additional distinction for static analysis.
- `NewType` adds no runtime domain checking; a bounded value needs a real check at construction.
- Choose `Literal` for a small set of constants and `Enum` when those values need identity or behavior.
- `Annotated[T, metadata]` adds information a tool can use; without a consumer, it is not validation.
- `Final` statically forbids reassignment without preventing additions to the referenced list or dictionary.
- `ClassVar` describes a class attribute; without an assignment, its declaration creates neither storage nor a value.
- `Never` or `NoReturn` expresses the absence of a normal return, not the absence of bugs or observable effects.

### Preserve Generic Relationships

- Use a type parameter to relate input and output; replacing both with `Any` loses that relationship.
- Choose a bound when common behavior is required and constraints when the contract selects among given types.
- Do not add a type parameter that relates nothing and makes no contract more precise.
- A type parameter default specifies usage without type arguments; it constructs no runtime value.
- Preserve the invariance of mutable collections: accepting a `list[Child]` as a `list[Parent]` would permit an incompatible write.
- Prefer a covariant read abstraction if no writing is necessary; do not circumvent invariance with a `cast`.
- For a callable, the accepted input type and produced output type do not vary in the same direction; reason about the calls allowed.
- `type[C]` describes a class object compatible with `C`, whereas `C` describes its instances.
- A compatible class does not necessarily offer every imaginable constructor; check the signature actually called by a factory.
- Use `Self` for a return that follows the concrete class, especially `return self` or an alternative constructor using `cls`.
- Do not declare `Self` if the implementation always reconstructs the base class.

### Describe Interfaces and Records

- Define a minimal `Protocol` from the consumer's operations without forcing implementations to inherit from it.
- Check names, attributes, parameters, and returns: a method with a similar intent but a different signature does not satisfy the protocol.
- An ordinary protocol is unsuitable for `isinstance`; `runtime_checkable` permits only a limited runtime structural check.
- That check does not validate signatures; since Python 3.12, static member lookup does not follow `__getattr__` forwarding.
- Declare exposed methods when their static checking matters; forwarding that returns `Any` lets name mistakes pass.
- Use `TypedDict` for a dictionary with known keys without claiming to change its ordinary dictionary behavior.
- Distinguish an absent key from a `None` value; `NotRequired[T]` concerns the key's presence, not the nullability of its value.
- Use `Required` and `NotRequired` according to the presence contract without confusing these markers with default values.
- `ReadOnly`, if available, restricts writes as seen by the tool, not runtime mutations or mutations of nested objects.
- For named, typed keyword arguments, describe `**kwargs` with `Unpack[TypedDict]` only if the version and checker support it.
- `**kwargs: T` means each value has type `T`; it does not define the permitted names.

### Preserve Callable Signatures

- Describe a simple callable with its parameters and result; `Callable[..., R]` gives up argument checking.
- Use `ParamSpec` to forward a wrapped function's full parameters, and a separate type for its result.
- If the wrapper changes the result, declare that transformation while preserving the relationship between the arguments.
- `functools.wraps` preserves metadata useful at runtime but does not replace the wrapper's generic contract.
- Overloads describe several call contracts; the implementation must still actually handle the accepted combinations.

## Procedure

1. Establish versions, tool, and checked scope; identify the relevant interfaces and dynamic areas.
2. Write the contract in terms of required operations and relationships between values before choosing typing syntax.
3. Annotate the boundary, retain local inference, and replace avoidable unknowns with precise types.
4. Reduce each diagnostic to a real incompatibility, missing information, or a documented checker limitation.
5. Correct the model or narrowing; use a suppression only after establishing why it is legitimate.
6. Run the configured check and the project's tests; report their results and uncovered areas separately.

## Pitfalls

- A silent analysis may merely mean that `Any`, an untyped import, or an exclusion has neutralized checking.
- A union narrows a value's shape, not business invariants, network state, or a resource's lifetime.
- `Final`, `NewType`, `TypedDict`, and generic annotations do not become runtime barriers.
- A signature accepted by one tool does not guarantee the same conclusion with another tool or configuration.
- Recent syntax may make the module impossible to import on the minimum version before any checking even occurs.

## Verification

- Confirm that each modified interface is actually analyzed and that no new unknown area has been introduced without reason.
- Check correct usages and deliberately incompatible usages in a suitable test location without contaminating the delivered code.
- Test union branches, key presence, wrappers, and mutations between checking and use.
- Validate external inputs and invariants separately; do not credit annotations with that work.
- Declare the versions actually checked and the remaining limitations; do not claim a general proof of correctness.
