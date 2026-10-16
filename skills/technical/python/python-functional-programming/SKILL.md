---
name: python-functional-programming
description: Compose pure functions and controlled streams.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Functional Programming in Python

## When to Use

- Isolate reproducible computations amid input/output and application state.
- Replace repeated loops with operations whose contract is already established.
- Configure behaviors with functions, closures or partial application.
- Examine a stale cache, an indirect mutation or a pipeline that consumes too much.
- Do not impose a loop-free style or a functional library if straightforward Python suffices.

## Philosophy

Expand the portion of the program that can be understood from its arguments alone.
Keep useful effects at explicit boundaries and compose small, testable transformations.
Immutability facilitates sharing; a well-contained local mutation can still be the best construction tool.
A function or a dictionary of functions often replaces a single-method object.
This original synthesis draws on Bruce Eckel, Thinking in Python, corpus a8feb860.

## Rules

### Purity and Dependencies

- A pure function depends on its arguments and truly stable configuration, without modifying external state.
- Given identical inputs, it produces the same result or the same deterministic error; raising an exception does not prove impurity.
- Inventory reads of globals, time, randomness, environment, files and captured objects before claiming purity.
- Extract external data upstream and pass it to the computation; perform display, logging and persistence downstream.
- A read-only annotation does not protect against mutation of the same objects by another owner.
- Building a local mutable accumulator is compatible with a pure computation if no external reference is modified.
- If this accumulator escapes, do not subsequently modify it behind the scenes; clearly define who owns it.
- A function without shared state is simpler to test and parallelize, but does not automatically become faster.
- Define the pipeline's failure policy: propagation, rejection of an element or an error represented as data; composition does not choose it.

### Immutable Values and Sharing

- Prefer tuples, `frozenset` and frozen dataclasses for long-lived values when this expresses their meaning.
- `frozen=True` and tuples do not recursively freeze their contents; an internal list remains mutable.
- `Final` prohibits reassignment for the checker, not mutation of the referenced object or reassignment at runtime.
- `Sequence` and `Mapping` describe a read-only interface; they do not convert the supplied object into an immutable value.
- For a stable snapshot, copy or normalize the relevant contents, without forgetting nested objects.
- A usable hash does not prove immutability: a mutable object can be hashed by identity.
- A content-based hash must remain consistent with equality throughout use as a key.
- A frozen dataclass is hashable only if the fields involved in its hash are also hashable.
- Avoid copying large structures at every tiny change; build locally and then freeze at the boundary.
- A shallow copy reuses references from unchanged fields; this sharing is safe only according to their contract.

### Functions as Values and Closures

- Pass a function to isolate what varies; use a dictionary if behavior selection is extensible data.
- For a closed set of structural cases, a `match` can be more explicit than a function table.
- Reserve `lambda` for a short local expression; use `def` for a name, documentation, annotations and a readable error traceback.
- Prefer a comprehension when `map` or `filter` would require a new lambda without improving clarity.
- Prefer `map(existing_function, source)` when the operation's name suffices; do not multiply list conversions.
- `map` and `filter` are single-pass iterators; `sorted` consumes everything and returns a new list.
- A closure retains bindings, not a deep snapshot; its purity depends on what can change behind those bindings.
- Captured, stable configuration suits a specialized pure function.
- `nonlocal` allows reassignment of an enclosing binding; without it, an assignment makes that name local to the function.
- A captured and modified counter is deliberately impure, even if better encapsulated than a global.
- In a loop, closures can read the last value of the same binding; fix the value with a factory or `partial`.
- A closure's encapsulation is an inspectable convention, not a security protection.

### Specialize and Compose

- `partial` fixes positional arguments from the left; use keywords to target a named parameter.
- Fixed arguments are references to objects, not copies; a mutable object can still change after creation.
- A keyword fixed by `partial` can be replaced when calling; do not treat it as an inviolable constraint.
- `partialmethod` suits specializations within a class, because its method binding correctly places `self`.
- Do not assume that `partial` has the same descriptor properties across all supported versions.
- To leave a positional hole, `Placeholder` requires Python 3.14 or later; on 3.11, write a small explicit wrapper.
- Compose in a stated order: in `f(g(x))`, `g` executes before `f`.
- Annotate intermediate inputs and outputs; a composition that erases everything into `Any` loses its checking value.
- Keep named stages rather than an obscure generic composition operator for two simple calls.
- A decorator wrapper uses `wraps` to preserve documentary identity and `__wrapped__`, without claiming to guarantee purity.

### Choose a Reduction or Adapter

- Look for the computation's name before rewriting its loop: `sum` for the sum, `math.prod` for the product.
- `reduce` performs a left fold; supply an explicit initializer if empty input must have a defined result.
- On Python 3.11, pass this initializer as the third positional argument to remain compatible.
- The initializer also participates in nonempty computation; choose a genuine identity when that is the contract.
- `accumulate` emits intermediate results; its `initial` parameter also adds a first value to the output.
- `operator` provides named operations along with `itemgetter` and `attrgetter`, often more readable than a lambda.
- Prefer a `key` function to a comparator; use `cmp_to_key` only to adapt a necessary or existing comparator.
- `total_ordering` completes `__eq__` and one ordering comparison; return `NotImplemented` for incompatible types.
- A dataclass with `order=True` suffices if lexicographic field order is precisely the desired contract.
- `singledispatch` selects by the type of the first positional argument, not its value or multiple arguments.
- Provide a fallback implementation; a table indexed by name serves a different need from type-based dispatch.
- `singledispatchmethod` uses the first argument other than `self` or `cls`; make decorator order compatible with registration.

### Correct Caches and Retention

- Add `cache` or `lru_cache` only after identifying all dependencies of the result and a measurable benefit.
- Arguments must be hashable; converting a list to a tuple removes no hidden dependency on mutable history.
- A key must include the relevant configuration, version or snapshot; otherwise explicitly invalidate when they change.
- Do not cache a generator or coroutine to reuse its computation: the cache would return the same consumable object.
- Avoid shared mutable results or copy at the boundary; a caller could alter the response to subsequent calls.
- `cache` retains keys and results without a limit; `lru_cache(maxsize=...)` bounds the number of entries, not their total size.
- A method cache retains `self` through its keys; it can retain instances much longer than expected.
- Use `cache_info` to measure hits, misses and occupancy; `cache_clear` is an explicit policy, not a correction for impurity.
- A cache's thread-consistent internal structure does not rule out multiple simultaneous computations of the same missing key.
- `cached_property` stores per instance in its `__dict__`; without this dictionary, notably with slots alone, it is unsuitable.
- Its value remains stale if source data changes; delete the cached attribute to allow recomputation.
- Do not attribute a universal once-only execution guarantee to it: its former internal lock was removed starting in Python 3.12.

### Iteration Tools and Hidden Costs

- `count` is infinite; `repeat` re-emits the same object without making a copy; always identify the consumer that stops.
- `cycle` remembers its input; with infinite input, its retention grows without ever reaching a second cycle.
- `islice` limits or skips by consuming; neither negative indices nor backward traversal of the source.
- `chain.from_iterable` concatenates a source of sub-iterables without expanding all arguments in advance.
- `pairwise` produces overlapping adjacent pairs; an empty source or singleton gives empty output.
- `batched` exists starting in Python 3.12; its `strict` option starting in 3.13.
- On 3.11, form each batch with `tuple(islice(it, size))`, stop at the empty tuple and reject `size <= 0`.
- Decide whether to keep or reject the final short batch; do not silently lose a tail of data.
- `compress` selects by indicators; `starmap` expands each row into arguments; both require a clear shape contract.
- `filterfalse` selects all rejected elements; `takewhile` stops at the first rejection and consumes it.
- `dropwhile` skips a prefix and then stops evaluating the predicate; its first output may require many reads.
- `zip` and `map` over multiple inputs stop at the shortest; use `zip(strict=True)` if lengths must match.
- `zip_longest` retains tails by padding; choose a distinct `object()` if `None` is valid data.
- `groupby` groups consecutive elements; for global grouping by key, sort with the same key or accumulate in a dictionary.
- Consume or materialize each group before requesting the next; groups share the underlying cursor.
- Global sorting materializes the data; do not conceal it behind a promise of constant-memory processing.
- `tee` retains the gap between readers, is not thread-safe and requires no longer reading the original source directly.
- `product`, `permutations` and `combinations` pool their inputs; those inputs must be finite.
- `permutations` considers order, `combinations` does not; `combinations_with_replacement` and `product(..., repeat=...)` allow repetitions.
- Combinatorial output can explode despite lazy emission; bound the search space as well.

### Recursion and History

- Use recursion for a self-similar structure, with a verifiable base case and progression.
- For long, flat repetition, choose a loop; Python does not eliminate tail-recursive calls.
- For unbounded external depth, prefer an explicit stack to blindly raising the recursion limit.
- Cache repeated subproblems if their inputs are complete; a tree without repetitions gains nothing from memoization.
- In a rotation or group computation, separate a direct formula from a history-based heuristic.
- A generator with local seeded randomness can be reproducible without each step being pure.
- A function that reads previous encounters remains dependent on that history; a tuple of participants alone is not a sufficient key.
- Test coverage, duplicates, small populations and remainders; a reproducible heuristic does not prove optimality.

## Procedure

1. Inventory inputs, outputs and states read or modified; isolate at least one transformation whose contract is explicit.
2. Choose values and snapshots, then direct functions, closures or `partial` according to what must vary.
3. Replace only loops whose meaning a tool expresses better; define bounds, remainders and evaluation order.
4. Before any memoization, verify key completeness, result stability, retention and invalidation policy.
5. Test stages alone and then their composition on an empty source, singleton, partial stream and unsorted data.
6. Measure memory and time at a representative size; retain the simplest form that satisfies the contract.

## Self-contained Example

A memoized report includes all its dependencies in its key and returns only immutable values.

```python
from functools import lru_cache, partial
from itertools import groupby
from operator import itemgetter


def eligible(threshold: int, row: tuple[str, int]) -> bool:
    return row[1] >= threshold


@lru_cache(maxsize=8)
def report(rows: tuple[tuple[str, int], ...], threshold: int
           ) -> tuple[tuple[str, int], ...]:
    retained = sorted(filter(partial(eligible, threshold), rows),
                      key=itemgetter(0))
    return tuple((name, sum(map(itemgetter(1), group)))
                 for name, group in groupby(retained, key=itemgetter(0)))


data = (("b", 6), ("a", 4), ("b", 2), ("a", 9))
report.cache_clear()
assert report(data, 4) == (("a", 13), ("b", 6))
assert report(data, 4) == (("a", 13), ("b", 6))
assert report.cache_info().hits == 1
assert report(data, 7) == (("a", 9),)
assert report((), 4) == ()
assert data == (("b", 6), ("a", 4), ("b", 2), ("a", 9))
assert report.cache_info().currsize == 3
```

## Pitfalls

- No visible effect does not mean no state is read; also inspect closures and properties called.
- A stable seed does not cancel consumption of a random generator supplied by the caller.
- Laziness guarantees neither termination, nor constant memory, nor independent restarting.
- Correct standard tools can be assembled in the wrong order: units, filtering and sorting remain business decisions.

## Verification

- Call twice with the same values and compare the result or error, without requiring a hidden reset.
- Verify the absence of input mutation, including nested contents and shared references.
- Test the cache with a changed dependency, eviction and a consumable or mutable result explicitly excluded.
- Check noncontiguous groups, different sizes, an incomplete final batch and bounds on infinite sources.
- Adapt syntax and tools to the project's minimum version; the examples require only the standard library and Python 3.11 or later.
