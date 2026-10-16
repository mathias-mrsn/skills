---
name: python-iterators-generators
description: Design reliable iterations and generators.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Python Iterators and Generators

## When to Use

- Design an API that traverses data without requiring it to be stored.
- Process a large stream, an infinite source or an interruptible producer.
- Diagnose an empty second traversal, late validation or unexpected consumption.
- Compose a conversation using `yield`, `send`, a final return value or closure.
- Do not choose a generator to implicitly promise indexing, length or backward traversal.

## Philosophy

The caller requests a next value, not the structure that contains it.
The native protocol replaces a traversal hierarchy and redundant control methods.
Laziness shifts work, errors and the lifetime of references; it does not eliminate them.
A stream can be a sequence of data or a description of requests to which a driver responds.
This original synthesis draws on Bruce Eckel, Thinking in Python, corpus a8feb860.

## Rules

### Choose the Minimal Contract

- An iterable provides an iterator through `iter(source)`; an iterator responds to `next(it)`.
- The iterator returns itself from `__iter__` and signals its end with `StopIteration`.
- Use `for`, comprehensions and native consumers rather than calling their special methods directly.
- Accept `Iterable[T]` for a single pass; do not require a list without a need for indexing or storage.
- `Iterable[T]` can refer to an already partially consumed generator; the annotation guarantees no replay.
- For multiple passes, materialize once, accept a source factory or require a suitable collection.
- `Collection[T]` or `Sequence[T]` express additional capabilities, not an immutable snapshot.
- An object whose `__iter__` creates a new generator can remain lazy and support repeated traversal.
- The old `__getitem__` protocol indexed from zero works until `IndexError`, but interferes with `Iterable` checks.
- In new code, define `__iter__` instead of depending on this historical compatibility.

### Generator or Iterator Class

- Start with a function containing `yield`; its frame automatically retains position and local variables.
- Reserve an iterator class for attributes observable during traversal or useful additional methods.
- An adapter that calls `next` on its source must retain `iter(source)`, not assume that every collection is already a cursor.
- A value check using `isinstance` must specify whether it rejects the stream at the first failure or skips invalid elements.
- Do not confuse this runtime examination with merely annotating the element type.
- For a dataclass representing a cursor, prefer `eq=False` if identity-based equality is the intended contract.
- Field-based equality is ill-suited to moving traversals; do not add a hash based on mutable state.

### Deferred Execution and Lifetime

- Calling a generator function creates the generator without executing its body; the first `next` starts it.
- A generator expression does, however, evaluate its leftmost iterable immediately: do not generalize to every expression.
- Validation placed before the first `yield` in the body remains deferred until consumption.
- If the call must reject an argument immediately, validate in an ordinary function that returns an inner generator.
- After exhaustion, subsequent traversals are empty without a diagnostic; `iter(g)` does not restart `g`.
- Explicitly choose between retaining values and repeating the computation, especially if the external source can change.
- A suspended generator retains references in its frame, sometimes a large structure or an open resource.
- Memory remains bounded only if the stages, buffers and consumers do too.
- Avoid `list(source)` before a limit; limit the source and then materialize only the finite portion.

### Consuming Is Not Observing

- `next(it, marker)` already advances the cursor; a membership test consumes through and including the value found.
- Use a distinct marker, such as a dedicated `object()`, if `None` is among the possible data values.
- A lookahead must retain the element read and return it later; disclose this buffer instead of promising free inspection.
- The `first/current_item/is_done` interface on a stream requires reconstructing storage to offer true backward traversal.
- `iter(function, sentinel)` calls the function until a value equal to the sentinel; choose that sentinel unambiguously.
- `for` absorbs normal termination; do not let the `StopIteration` from an internal `next` escape the generator body.
- Such an escaped exception becomes `RuntimeError`; finish with `return` or traverse the source with `for`.

### Compose Streams Without Losing Bounds

- A generator expression suits a local transformation; use `chain` to concatenate and `islice` to bound.
- `islice` also consumes skipped elements and does not accept negative indices.
- `takewhile` stops at the first failure and consumes the rejected element; `filter` continues searching.
- On an infinite source with no next eligible element, a filter may never yield a result or terminate.
- Bound tests with a read counter that fails, rather than starting an infinite consumer.
- `tee` retains values between the leading reader and the lagging one; a stopped reader can force unbounded retention.
- After `tee`, use only the returned branches, without advancing the original source directly.
- If one branch finishes before the other starts, a finite list is often simpler and just as economical.
- `tee` branches are not thread-safe; provide synchronization or queue-based transfer.
- A generator cannot be resumed simultaneously; a single driver owns its advancement.

### The Three Channels

- For production alone, annotate with `Iterator[T]`; for a conversation, `Generator[Y, S, R]`.
- `Y` is the value emitted by `yield`, `S` the value received by that expression, `R` the final result of `return`.
- In a Python 3.11-compatible project, provide all three `Generator` parameters and use `TypeVar` if necessary.
- Do not copy newer generic syntax without checking the project's minimum version.
- Prime with `next(g)`: sending a value other than `None` before the first `yield` raises `TypeError`.
- At runtime, `send(None)` is equivalent to `next`, but may contradict a `SendType` that excludes `None`.
- Each `send(response)` supplies the response to the suspended `yield` and then advances to the next `yield` or final return.
- A `for` resumes with `next`, so it supplies `None` and ignores the final return value; it does not drive an arbitrary typed conversation.
- The final return value arrives in `StopIteration.value`; check it at the boundary if its origin is untrusted.
- Distinct `NewType` types can help the checker distinguish requests, responses and results with the same representation.
- Annotations do not validate received responses at runtime; enforce necessary invariants in the code.

### Delegation, Interpretation and Cleanup

- `yield subgenerator()` emits the generator object; `yield from subgenerator()` delegates its traversal.
- `result = yield from subgenerator()` receives its final return value, not the list of its emitted values.
- Delegating to a simple list iterator normally returns `None`.
- `yield from` relays emissions and, if the delegate offers them, the `send`, `throw` and `close` operations.
- A `for` loop that re-emits elements loses responses and the final return value; it is not a general replacement.
- Distinguish composition from interpretation: generators describe requests, while the driver chooses how to respond.
- In the driver, wrap only `next` or `send` in the `try` that recognizes the generator's termination.
- Do not confuse this termination with exhaustion of a response source; handle that second situation separately.
- Account for a generator that returns during priming, without ever emitting a request.
- `throw(Exception(...))` raises the exception at the suspended `yield`; handling it can produce a new value or terminate.
- `close()` injects `GeneratorExit` into a suspended generator; allow that request to terminate it and execute the `finally` blocks.
- Never emit a new value during closure: doing so causes `RuntimeError`.
- A driver that abandons a live conversation closes it in `finally`; `break` alone does not guarantee this closure.
- Closing a generator that has never started does not execute cleanup inside its body; acquire resources in the right place.
- Do not depend on the value returned by `close`, whose behavior differs by Python version.
- A cooperative scheduler can rotate a queue of generators, one advancement per turn; it does not make blocking code nonblocking.

## Procedure

1. Define whether the source is finite or infinite, the number of traversals, the order and the cursor owner; make these choices explicit.
2. Choose a generator function, expression or class solely according to the capabilities actually needed.
3. Delineate immediate validation, deferred work, final consumption and resource management.
4. For a conversation, name the three channels and the driver's response, error and abandonment policies.
5. Compose native stages; for every buffer and materialization, set a bound or justify a finite input.
6. Run empty, partial, exhausted and interrupted tests; observe values, read counts and cleanup.

## Self-contained Example

A measurement request is delegated; a negative measurement fails, and cleanup belongs to the conversation.

```python
from collections.abc import Generator


def measure() -> Generator[str, int, int]:
    value = yield "measurement"
    if value < 0:
        raise ValueError("negative measurement")
    return value


def total(trace: list[str]) -> Generator[str, int, int]:
    try:
        left = yield from measure()
        right = yield from measure()
        return left + right
    finally:
        trace.append("closed")


trace: list[str] = []
g = total(trace)
assert trace == []
assert iter(g) is g
assert next(g) == "measurement"
assert g.send(7) == "measurement"
try:
    g.send(5)
except StopIteration as end:
    assert end.value == 12
else:
    raise AssertionError("missing final return value")
assert trace == ["closed"] and list(g) == []
h = total(trace)
assert next(h) == "measurement"
h.close()
assert trace == ["closed", "closed"]
k = total(trace)
assert next(k) == "measurement"
try:
    k.throw(ValueError("cancellation"))
except ValueError as error:
    assert str(error) == "cancellation"
else:
    raise AssertionError("exception not propagated")
assert trace == ["closed", "closed", "closed"]
```

## Pitfalls

- An `Iterable` signature guarantees neither a fresh source, nor cardinality, nor termination.
- Laziness and reusability are independent; two names for the same generator do not create two traversals.
- A chain of generators can retain large references despite producing one element at a time.
- Recursive flattening must treat `str` and `bytes` as leaves if descending into them makes no sense.
- No type checker proves stream termination or the absence of additional consumption.

## Verification

- Test an empty source, one element, multiple elements and a partially consumed generator.
- Compare a second traversal against the promised contract; verify that independent traversals have distinct cursors.
- Trigger an error at creation and at consumption according to the stated policy.
- Check the three channels, return without emission, response-provider errors and propagation of `throw`.
- Verify that closure and interruption clean up resources actually acquired exactly once.
- Run the assertions on supported versions; measure buffers if a memory bound is promised.
