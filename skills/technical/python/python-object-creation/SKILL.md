---
name: python-object-creation
description: Choose simple and safe ways to create objects.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Python Object Creation

## When to Use

- Centralize product selection without scattering concrete classes throughout callers.
- Choose between a constructor, an alternative constructor, a table, a factory, a prototype and stepwise construction.
- Examine a single-instance requirement, a first-call race or state shared between tests.
- Design an extensible registry and its loading, validation and collision rules.
- Do not introduce a factory if a direct constructor call already expresses the entire contract.

## Philosophy

Identify what varies before choosing a structure: arguments, type, preconfigured state or process.
In Python, functions and classes are values; a module and a dictionary often solve the problem.
Unique identity guarantees neither consistent mutations, nor test isolation, nor uniqueness across processes.
Prefer explicit mechanisms to construction interception that is difficult to type and diagnose.
This original synthesis draws on Bruce Eckel, Thinking in Python, corpus a8feb860.

## Rules

### Choose According to the Variation

- With no variation, call the constructor; for another argument format, choose an alternative constructor that validates and normalizes.
- A name selects the type: use a table of classes or construction functions.
- Additional construction work justifies a factory function; its own state, such as a pool, can justify an object.
- Multiple products must belong to a consistent family: choose that family at a single boundary.
- Preconfigured state matters more than type: compare copying a prototype with reconstructing it with changes.
- Reserve a builder for ordered, interdependent steps; simple independent options are keyword arguments with defaults.

### Uniqueness Through a Module

- A module is shared through its name in `sys.modules`, per interpreter; processes and subinterpreters have their own instances.
- Keep shared state in an importable module separate from the entry script executed as `__main__`.
- Loading the same file under multiple names, or reloading it, can invalidate once-only initialization assumptions.
- After `from configuration import data`, mutating the shared dictionary differs from reassigning the local name.
- Prefer `import configuration` followed by `configuration.data` if the entire value may be replaced.
- Initialization at import simplifies first access, but imposes its cost and errors as soon as loading occurs.
- For an external resource, also define who closes, replaces and invalidates the instance; a module does not settle its lifetime.
- Global state facilitates sharing but hides dependencies; inject an explicit instance when multiple configurations are needed.

### Instance Retained by a Function

- If a class is useful, a no-argument function decorated with `cache` can retain its instance.
- The guarantee applies to this function, not to direct constructions; `_Class` is a convention and `type(instance)` retrieves the type.
- Do not nest the class inside the function to claim it is inaccessible: public typing becomes more difficult.
- Without a cache, a class redefined at each call also produces different type identities.
- Keep the single-access signature empty; with arguments, the result is a cache per key, not a global instance.
- `access()`, `access("prod")` and `access(environment="prod")` can form different keys despite the same logical default.
- Initializing one key does not protect the other call forms; explicitly handle any later configuration by rejection, replacement or prohibition.
- `cache_clear` removes the cache's reference but neither destroys nor closes objects still held by clients.
- Prefer fresh instances injected into tests; cache clearing must be controlled and performed outside concurrent access.

### First Call and Synchronization

- `cache` protects the consistency of its internal structure, not once-only function execution during simultaneous first requests.
- Multiple threads can miss the same key and then each construct a different object.
- If unique identity matters, create the object before starting consumers, or protect the check and creation with the same lock.
- A lock placed only inside the body of a function already decorated with `cache` does not recheck the miss detected before entry.
- For manual lazy creation, acquire the lock, check for absence and then construct and publish the complete object under that lock.
- Use an explicit sentinel if `None` is a valid result; do not test only the instance's truth value.
- If construction fails, do not publish a partial object; decide whether the next call retries and clean up acquired resources.
- Reentrant construction can deadlock with an ordinary lock; remove the cycle rather than hide incomplete initialization.
- Double-checked locking requires a second check under the lock and publication after complete initialization.
- Do not choose lock-free access for a presumed optimization: assess runtime guarantees and measure before adding complexity.
- Early initialization or systematic locking is easier to reason about than a subtle publication protocol.
- The creation lock does not subsequently protect mutations of the shared object; synchronizing them belongs to another contract.
- `global` is necessary to reassign a module name inside a function, not to use or modify the object it refers to.

### Recognize Classic Forms Without Imposing Them

- `__new__` chooses the returned object; if it returns an instance of the class, `__init__` may be called again on each construction.
- Stable identity therefore does not prove once-only initialization; prevent a new call from silently resetting shared state.
- If `__new__` returns another type, normal initialization is skipped and the `isinstance` contract may be broken.
- A metaclass can intercept `__call__` and avoid subsequent initializations, at the cost of additional inheritance and argument rules.
- A decorator replacing a class with a callable object can break `isinstance`, subclassing and typing precision.
- A wrapper that delegates everything through `__getattr__` often exposes `Any`; this cost is unnecessary for sharing data.
- Borg creates multiple identities that share the same `__dict__`; it is not a single identity.
- Use Borg only if the interface really requires multiple objects with common state; otherwise prefer a module.
- An inherited storage attribute can cause unintended subclasses to share state; explicitly define the storage scope.
- A dataclass generates an `__init__` that does not automatically call the base's initializer; Borg sharing can silently disappear.
- Connecting the `__dict__` after the generated assignments can instead lose fields already initialized.

### Tables, Alternative Constructors and Contracts

- A table provides an explicit, inspectable choice; never use `eval` to turn an external name into a constructor.
- Store classes when they share a construction contract; otherwise use adapted functions with a uniform signature.
- `type[Product]` describes the type of classes but is not enough to guarantee arbitrary subclass parameter conventions.
- For a closed set, a `Literal` alias helps the checker; also test that the table contains all expected keys.
- An external string still requires runtime validation; a `Literal` annotation is not a parser.
- Decide whether an unknown key exposes `KeyError` or is translated into a business error; do not silently return an arbitrary product.
- `Final` protects the binding for the checker, not dictionary entries; do not confuse it with a frozen registry.
- An alternative `classmethod` ends with `cls(...)` to respect subclasses whose constructors remain compatible.
- Annotate its return with `Self` on Python 3.11 or later; a simple function suffices if no association with the type is useful.
- Preserve invariants in the final constructor; the alternative constructor must not be the only validated path.

### Open Registries

- Choose between explicit registration and `__init_subclass__` according to who must be able to participate and when.
- The hook requires actual inheritance; a class that only satisfies a `Protocol` does not automatically participate.
- Explicit registration can be a module function; a registry object is useful only to own or isolate its state.
- A registration decorator must return the class unchanged and preserve its precise type.
- A `TypeVar` bounded by a `Protocol` allows the checker to reject an incomplete product at the registration point.
- The `Protocol` alone does not enforce runtime validation; an ABC prevents instantiation of subclasses that remain abstract.
- An intermediate abstract class can register itself before any instantiation attempt; do not presume an entry is constructible.
- A plugin is registered only after its module executes; explicitly load plugins before exposing the factory.
- If the project uses deferred imports, their textual presence does not prove that registration has occurred.
- Reject collisions or state an explicit replacement rule; a short class name is not necessarily unique.
- A key qualified by module and name can avoid some collisions, but a stable business identifier better withstands reorganizations.
- Do not infer a complete registry from `__subclasses__`, which returns only direct subclasses on each call.
- Choose a single table owner; access through `cls.registry` can select storage shadowed by a subclass.
- The registry's strong references also retain temporary classes created by tests.
- Give each test a fresh registry, or restore its contents exactly; test missing registration as well as automatic registration.

### Elaborate Factories and Families

- A factory object suits pooling, caching or evolving configuration that it genuinely owns.
- Injecting a construction function often suffices to replace a parallel hierarchy of creators.
- Factory Method is useful if an existing algorithm calls a creation operation that subclasses specialize and already has real behavior.
- Avoid a creator per product without behavior of its own; Abstract Factory chooses multiple compatible products, expressible by a `Protocol` without a common base.
- A common product interface does not prove family compatibility; test allowed combinations or encode their relationship.
- Do not assign variation in usage rules to the factory: constructing a product and deciding how it acts are two responsibilities.

### Prototype and Copies

- Copy a prototype when its configured state is more natural to reuse than its construction recipe.
- `copy.copy` duplicates the outer shell, not nested mutable objects; modifying a shallow-copied list still modifies the original.
- `dataclasses.replace` suits dataclass variants on Python 3.11 and calls their construction again, hence `__post_init__`.
- Unchanged fields remain shared; supply a new value for every mutable object that must become independent.
- `copy.replace` is more general but requires Python 3.13 or later; do not impose this API on the project without checking its minimum version.
- `deepcopy` processes the graph with memoization, may retain objects or apply their hooks; it is not proof of universal independence.
- It generally does not go through the constructor or its validation again; a subsequently modified variant must explicitly preserve invariants.
- Files, connections and locks do not become independent resources through deep copying; define dedicated reconstruction.
- Test both variant independence and the stability of the stored prototype, including nested fields.

### Builder and Publication

- Prefer keyword arguments, defaults and `replace`; reserve a builder for dependencies and cross-cutting constraints that justify intermediate state.
- Distinguish local validation at each step from global validation before publishing the complete product.
- A list of fragments followed by `join` is already progressive construction; a new class is not mandatory.
- If methods are chainable, return `self` with `Self` and document mutation of the builder.
- Define whether `build` consumes, resets or snapshots the builder; test a second call and a modification after publication.
- Do not let the product accidentally share the internal construction list; freeze or copy the necessary elements.

## Procedure

1. State what varies, the invariants, the sharing scope and the project's minimum Python version.
2. Choose the smallest sufficient structure: a constructor, function, module or table before a hierarchy and metaclass.
3. Define external inputs, errors, registry keys and the common constructor contract.
4. For single-instance sharing, specify initialization, concurrency, later arguments, closure and test reset.
5. For a copy or builder, map shared references and prevent publication of invalid state.
6. Verify product additions, errors and isolation; introduce a heavier mechanism only in response to an observed constraint.

## Self-contained Example

A table of functions produces validated configurations; `replace` creates a variant without a builder.

```python
from collections.abc import Callable
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Export:
    width: int
    columns: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.width <= 0 or not self.columns:
            raise ValueError("invalid configuration")


RECIPES: dict[str, Callable[[], Export]] = {
    "short": lambda: Export(40, ("name",)),
    "full": lambda: Export(100, ("name", "total")),
}


def create(name: str) -> Export:
    return RECIPES[name]()


a = create("short")
b = create("short")
assert a == b and a is not b
c = replace(a, width=60)
assert a.width == 40 and c.width == 60
assert c.columns is a.columns  # Safe sharing of the immutable tuple.
for operation, error in ((lambda: create("missing"), KeyError),
                         (lambda: replace(a, width=0), ValueError)):
    try:
        operation()
    except error:
        pass
    else:
        raise AssertionError("missing expected error")
```

## Pitfalls

- A shared instance can be a disguised global dependency; prefer injection if sharing is not essential.
- The absence of failure in a fast race does not prove the absence of a race; synchronize the start of concurrent tests.
- A factory alone protects neither against direct use of a public class nor against mutation of the exposed registry.
- A successful copy proves neither resource independence nor revalidation of invariants.

## Verification

- Test every valid key, an unknown key, malformed inputs and a registry collision.
- Verify product type and behavior, not just the number of dictionary entries.
- For a promised singleton, check `is`, concurrent first calls, the absence of repeated initialization and per-interpreter scope.
- Verify test isolation, construction failure and the policy for retained references after reset.
- For prototypes and builders, modify a variant and confirm that the source and previous product remain consistent with the contract.
- Run the assertions with the standard library; keep syntax compatible with the project's minimum Python version.
