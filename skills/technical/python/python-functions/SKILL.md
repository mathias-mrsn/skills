---
name: python-functions
description: Design signatures, callbacks and variable algorithms.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Functions and Callable Behaviors

## When to Use

- Design a signature, diagnose a shared default or a scope error.
- Pass around an action, configure an algorithm or order handlers.
- Stabilize a sequence of steps while allowing their implementation to vary.
- Do not create a hierarchy merely because a classic pattern has one.

## Philosophy

- Name a behavior and expose the minimum needed to call it.
- Separate the choice of an operation from where and when it executes.
- Choose the lightest callable form that expresses the contract and its state.
- A signature describes a call form; it proves neither the effects nor the correctness of the behavior.
- Respect the project's minimum version; the self-contained example below requires Python 3.11+.

Original synthesis based on Bruce Eckel, Thinking in Python, corpus a8feb860 (CC BY-NC-ND 4.0).

## Rules

### Signature, Result and Forwarding

- Distinguish a declared parameter from a supplied argument; document the result, mutations and failures in a docstring at the start of the body.
- A docstring is information, not validation; annotations do not check input values.
- Keep return paths consistent: reaching the end of the body and a bare `return` return `None`.
- Several comma-separated expressions in a return construct a tuple: a single object is returned.
- Prefer keyword arguments when they clarify an option; their names then become part of the API.
- Place positional arguments before keyword arguments in ordinary calls.
- Place required parameters before those with defaults in the positional portion; keyword-only parameters have no such constraint.
- Use `/` to remove positional parameter names from the public contract; use `*` to require options to be named.
- The complete order is: positional-only, positional-or-keyword, `*args`, keyword-only, `**kwargs`.
- `*args` collects a tuple, `**kwargs` a dictionary; the names themselves are conventional.
- At the call site, `*iterable` and `**mapping` unpack arguments; keys used as keywords must be strings.
- Do not replace a stable signature with variadics unnecessarily; reserve opaque collection for genuinely generic forwarding.
- When forwarding, preserve `func(*args, **kwargs)` without losing arguments or the result; a `TypeError` occurs if the same positional-or-keyword parameter receives a value by position and by keyword. With `/` and `**kwargs`, a key with the same name can instead be collected without a collision.

### Defaults, Sentinels and References

- Every default is evaluated once, when `def` executes, and remains attached to the function.
- Construct lists, dictionaries and other mutable objects specific to each call inside the body.
- An immutable default, such as an empty tuple, suits input that is only read; do not subsequently apply a list operation to it.
- Use `None` as a marker only if it is not valid data; test `is None`, never the argument's truth value.
- If `None` is meaningful, create a unique module-level sentinel and compare by identity.
- For Python 3.11+, `object()` created once suffices as a local marker; do not reconstruct the marker during the comparison.
- The `sentinel` builtin presented in the corpus requires Python 3.15; do not introduce it on an earlier target.
- Define explicitly whether absence triggers a default, returns a marker or raises the expected exception; do not confuse absence with the value `None`.
- A parameter refers to the caller's object: mutating it is externally visible; reassigning the parameter does not reassign the caller's name.
- A capture or a `partial` retains references, not deep copies; a supposedly fixed configuration must also remain stable in its internal objects.

### Scope and Callback Creation

- Assigning to a name makes it local throughout the function, including before that assignment; reading it prematurely causes `UnboundLocalError`.
- Reserve `global` for deliberate reassignment of a module-level name; merely reading it does not require this, and mutation is not reassignment.
- Use `nonlocal` to reassign a binding in an enclosing function; it does not refer to module scope.
- Avoid mutable global state: understanding a call would require reconstructing the history of previous calls.
- A closure keeps enclosing bindings alive; each call to a factory can produce an independent configuration.
- Captured names are read at call time: lambdas in the same loop see its final value.
- To freeze the value during construction, use `partial`, a lambda default or a factory that receives the iteration's value.
- Keep a late-bound closure only if reading at call time is intended; computing too early then changes the behavior.
- A mutable closure can concentrate state in a single function; its privacy remains conventional, not a security barrier.
- Pass an existing function directly; prefer `key=len` to an equivalent lambda.
- Reserve lambdas for short, local expressions; use `def` for a lasting name, multiple steps, a docstring and useful tracebacks.
- To read an attribute or an index, consider `operator.attrgetter` and `operator.itemgetter` before a more obscure lambda.

### Choosing the Representation of Behavior

- Without its own state: a function; with the state of an existing object: a bound method.
- Store `object.method`, not `object.method()`: the second form executes immediately and stores the result.
- For a configuration: a closure; if the general function already exists, prefer `functools.partial` to a repetitive factory.
- `partial` fills positions from the left; bind a trailing option by name if it accepts keywords.
- To reserve intermediate positions, `functools.Placeholder` requires Python 3.14+; before that, write an adapter function. Checkers may track these signatures poorly: distinguish their limitation from an actual runtime error.
- Choose an object with `__call__` when the configuration needs an explicit name, fields and representation.
- Choose an object with multiple operations if undo, evolving state or bound methods are needed; a `Protocol` can describe `__call__` and `undo` without a common base.
- A command base is justified only by implementation that is actually shared, not by a second method alone.
- `Callable[[...], R]` describes the call, not `__name__`: a `partial` lacks an ordinary function's metadata; include the name in an explicit structural contract if the client requires it.
- Reserve attributes added to a function for markers read later; store configuration and call state in a closure or a typed object.

### Command, Strategy, Chain and Broadcast

- Command carries what to execute later; a list of callables executes every action in the intended order.
- Strategy chooses how to do a job: a callable parameter suffices for one call, a persistent context only if the strategy must outlive it.
- Chain of Responsibility tries handlers in order and stops at the first success; a list suffices without linked objects.
- Define the failure marker; compare by identity, because `0`, `0.0`, `False` and an empty string can be successes.
- Test an empty chain, all refusals, fallback and immediate stopping; the result is no more reliable than each handler's success criterion.
- Distinguish an expected failure from an exception: returning `None` in a handler and raising in the orchestrator are two different contracts.
- A bus associates an event type with all its handlers; unlike a chain, it calls them all.
- A dictionary indexed by `type(event)` handles only the exact type; traversing its MRO extends the contract to ancestors and can multiply notifications.
- With `defaultdict`, publishing with `.get()` avoids creating an empty list for every unknown event.
- Coupling the event type and handler signature at registration lets the checker verify their agreement; heterogeneous storage may nevertheless require a broader internal type.
- A bus that reads the annotation of `__call__` and uses marker decorators replaces this check with explicit runtime validation.
- For this marked bus, inspect `vars(cls)` if `__call__` must be declared directly: `hasattr(cls, '__call__')` is true even for a class whose instances are not callable.
- Check that the inspected annotation denotes a registered event; if it is deferred or textual, resolve that policy before comparing it with a class.
- With `dataclass(slots=True)`, register the class returned by the decorator, not the one it receives; their identities differ.
- `dataclass_transform` describes the generated constructor to the checker but does not itself perform the transformation; do not confuse declaration with mechanism.
- Keep registration explicit if tags and introspection do not remove enough repetition to justify their additional checks and failures.

### Fixed Algorithm and Variable Steps

- Distinguish Strategy, which replaces an algorithm, from a fixed sequence that delegates only certain steps.
- Prefer an orchestrating function and steps passed as parameters when the steps are independent.
- Choose Template Method if the steps share state, build on each other or form a coherent whole.
- Declare essential steps abstract with `ABC` and `@abstractmethod`; an empty hook is optional and can hide an omission.
- A default neutral callable can make a step optional without `None` checks in the loop.
- Separate construction and launch: the client calls `run()` after initialization is complete, never from the base constructor.
- Mark intentional overrides with `typing.override` on Python 3.12+; under 3.11, retain tests and signature checking without adding an implicit dependency.
- `typing.final` statically prevents replacement of the orchestrator; it does not block it at runtime.
- `__init_subclass__` can reject a redefinition during class creation; add this check only if the requirement goes beyond the checker.
- A similar-name heuristic can detect misspelled hooks but reject legitimate methods; this cost must remain explicit.
- None of these markers proves behavior: preserve the steps' order, repetition, effects and error policy with contract tests.

## Procedure

1. Identify inputs, outputs, effects and minimum version; write the absence and failure contract before the signature.
2. Choose explicit parameters, `/` and `*` constraints, then check every default and every mutable reference.
3. Determine what varies: operation, complete algorithm, step or handler; choose the corresponding minimal representation.
4. Fix when configuration is read and how long state lives; check callbacks constructed in loops.
5. Test order, stopping and failures with recording callables; run the project's already configured tools without inventing their results.

### Self-contained Example: Configurable Normalization

```python
from collections.abc import Callable, Iterable
from functools import partial

Handler = Callable[[str], str | None]

def choose(text: str, handlers: Iterable[Handler], /) -> str | None:
    for handler in handlers:
        result = handler(text)
        if result is not None:
            return result
    return None

def remove_prefix(text: str, *, prefix: str) -> str | None:
    return text[len(prefix):] if text.startswith(prefix) else None

def process(text: str, /, *, step: Handler,
            trace: list[str] | None = None) -> tuple[str | None, list[str]]:
    if trace is None:
        trace = []
    trace.append("before")
    result = step(text)
    trace.append("after")
    return result, trace

handlers = [partial(remove_prefix, prefix=p) for p in ("draft:", "ok:")]
assert choose("ok:", handlers) == ""
assert choose("other", []) is None
assert choose("other", handlers) is None
external: list[str] = []
value, trace = process("ok:ready", step=handlers[1], trace=external)
assert value == "ready" and trace is external
assert external == ["before", "after"]
assert process("ok:x", step=handlers[1])[1] is not external
assert [h("draft:x") for h in handlers] == ["x", None]
```

## Pitfalls

- Believing a capture deeply freezes data or that `final` protects execution.
- Forgetting that an arbitrary callable does not necessarily have `__name__`, a function attribute or an undo method.
- Replacing a result check with its truth value, or making a step on which the contract depends silent.
- Starting hooks on an incomplete subclass or turning a local variation into a framework.

## Verification

- Test omission, explicit `None`, a supplied empty container and successive calls without accidental sharing.
- Test accepted and rejected call forms, forwarding collisions and mutations visible to the caller.
- Verify configuration independence, intended late binding and falsy successes; check order with a call log.
- Run each implementation against the same contract; distinguish runtime tests from a checker actually run.
- Confirm that every syntax feature and import exists on the oldest supported version.
