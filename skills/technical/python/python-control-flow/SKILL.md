---
name: python-control-flow
description: Clarify Python conditions, loops and patterns.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Python Control Flow and Structural Patterns

## When to Use

- Write or review conditions, loops, early exits, parallel iteration and assignments within an expression.
- Precisely interpret an `else` clause, a guard or a path with no match.
- Decompose values using patterns and make captures, constraints and missing cases visible.
- Choose between centralized branching, a lookup table and behavior carried by objects.
- Detailed error policy and resource design are not the main focus; the rules needed for exit paths are included here.

## Philosophy

Control flow must express the question being asked: a condition, traversal, search, structural match or targeted recovery.
Choose the lightest form that keeps success, absence and failure paths visible.
A `match` is useful when it inspects a structure, not because it resembles another language's `switch`.
Operational synthesis of Thinking in Python, by Bruce Eckel; corpus a8feb860.
Respect the Python actually supported: `match` requires Python 3.10 or later, and `typing.assert_never` is available from Python 3.11 onward.

## Rules

### Conditions, Expressions and Blocks

- Use `if` and `elif` for predicates; their order matters, and the first true condition determines which branch executes.
- Use a chained comparison such as `lower < value < upper` when it really is the same value being bounded.
- Use `a if condition else b` to choose a simple value; keep separate statements if the branches involve several steps.
- Empty containers, zero and `None` are false; do not confuse absence with a legitimate value merely because they fail the same truth test.
- If only absence should trigger the fallback, test `is None`; `value or fallback` also replaces zero and empty text.
- `and` and `or` short-circuit and return an operand; place preconditions before the operations that depend on them.
- An `if`, `for`, `while`, `match` or `with` block does not create an independent local scope; do not assume its names disappear after the block.
- A conditional assignment binds the name only if it executes; define all relevant paths before reading the value after the block.
- Use `pass` for an intentionally empty statement; do not confuse inaction with actually implemented behavior.
- `...` is the Ellipsis value, commonly used as a stub body; neither it nor `pass` signals an implementation failure when called.
- Avoid naming new variables `match` or `case` despite their soft-keyword status: the reader should recognize the syntax immediately.

### Loops and Exits

- Traverse an iterable's elements directly; do not introduce indices merely to retrieve elements by indexing.
- Use `range()` to count, and `enumerate()` when both position and element are needed.
- Use `while` when repetition depends on an evolving condition; make visible what advances that condition.
- To perform an action before the test, use `while True` with an explicit exit; Python has no `do`/`while` statement.
- Check that acquiring the next value can succeed or that its failure is handled; a sentinel loop does not guarantee that the sentinel is present.
- `break` exits only the nearest enclosing loop; `continue` starts that loop's next iteration, not that of an arbitrary outer loop.
- A `return` exits the entire function: extracting a nested-loop search into a function can make its exit clearer.
- If work must continue in the same function, choose an explicit flag or a readable `else` structure rather than simulating a labeled `break`.
- A loop's `else` executes on normal completion without `break`, including when no iterations occurred.
- Do not read this `else` as the complement of an internal `if`: its alignment and trigger concern the loop.
- For a search, put the "found" path before the `break` and the "absent" path in the `else`, without an unnecessary flag variable.
- A `return` or exception that exits the loop does not constitute normal completion and does not execute its `else`.
- A combination of `else: continue` in the inner loop followed by an outer `break` can propagate a discovery; keep it only if it is more readable than a function.
- Do not change the size of the container being traversed: a list may silently skip an element, while a dictionary or set may raise `RuntimeError`.
- Build another container or defer deletions and additions; do not rely on an exception to detect every incorrect mutation.
- Use a comprehension to build a simple collection; retain a loop if the goal is an effect, multiple steps or control-flow exits.

### Parallel Iteration and the Walrus Operator

- Use `zip()` to advance through multiple sources together; without an option, traversal ends with the shortest source.
- If lengths must be identical, use `zip(..., strict=True)` on a compatible Python; a mismatch must not silently truncate data.
- If an index is also useful, combine `enumerate` and `zip` with unpacking that clearly reflects the nesting of pairs.
- A `zip` length error appears during consumption; an early exit does not validate all lengths.
- Use `:=` if computing, naming and testing a value in one place avoids duplication and clarifies the condition.
- Parenthesize the assignment before a comparison: otherwise, `name := expression > limit` binds the boolean result, not the computed value.
- Do not add a walrus to save a line if a separate assignment makes the path more obvious.
- A short-circuited condition may never execute the walrus; do not later read its name as if it were always defined or updated.
- In a reading loop, distinguish the stopping sentinel from a valid false value; explicitly test the expected condition.

### General Semantics of `match`

- Use a table for value-to-value mapping, conditions for predicates and `match` to examine and unpack a value.
- `match` is a statement, not an expression; to compute a value by case, place the returns in a function.
- Patterns are tried from top to bottom; only the first accepted case executes, without implicit fallthrough to the next case.
- Do not add a `break` to end a `case`; inside a loop, it would exit the loop, not just the `match`.
- With no match and no fallback case, `match` does nothing and does not automatically raise an error; decide whether that absence is acceptable.
- Place specific cases before general cases; a broad case can absorb inputs that a later branch was meant to handle.
- Numeric literal patterns use equality: an integer pattern can accept an equal float or a corresponding boolean.
- The `None`, `True` and `False` patterns compare by identity; do not attribute exactly the same semantics to them as to numeric literals.

### Captures, Constants and Alternatives

- A bare name captures any value, even if it resembles a constant or type name; `case CONSTANT:` does not compare against the existing constant.
- Compare a constant using a literal or qualified name, for example an Enum member; a guard can also compare against an unqualified name.
- Use `_` as a wildcard without capture; use another name when the branch needs to retrieve the entire value.
- To test a type, keep the class pattern's parentheses: `case str():` tests, whereas `case str:` captures and shadows that name.
- An unguarded capture is irrefutable; placing it before other cases makes them unreachable and can prevent compilation.
- Do not expect a warning for an accidental capture placed last: it may compile and pass checks while capturing everything.
- Use `|` for pattern alternatives, not to combine boolean conditions arbitrarily.
- Each alternative must bind the same set of names, so that the body has an identical contract regardless of the chosen alternative.
- Use `pattern as name` to check the shape while retaining the whole object; do not needlessly reconstruct the object from its fields.
- Do not repeat the same name to request equality between two captures; capture two distinct names, then compare them in a guard.

### Sequence and Mapping Patterns

- A sequence pattern describes a shape, not an exact container: brackets can accept a list as well as a tuple.
- Without a star, the length must match; with a starred capture, collect the rest at the beginning, middle or end, with only one star per sequence pattern.
- Sequence patterns exclude `str`, `bytes` and `bytearray`; do not expect them to decompose these values character by character.
- A mere iterable is not necessarily a sequence: a generator or set does not satisfy a pattern such as `[a, b]`.
- In a pattern, `(name)` is a grouped capture, not a singleton; `(name,)` describes a one-element sequence.
- A mapping pattern requires the mentioned keys and ignores additional keys; it does not validate an exact schema on its own.
- `case {}` accepts any mapping, not just the empty mapping; use an emptiness guard if that is the need.
- Use `**rest` to capture the remaining keys; explicitly decide whether they should be accepted, used or rejected.
- Do not infer value types from keys alone: with `dict[str, object]`, captures generally remain of type `object`.
- When a known structure needs precise field types, convert it into typed data and then match that shape rather than scattering assumptions across branches.

### Class Patterns, Guards and Nesting

- A class pattern constructs nothing: it tests the type, then examines the requested attributes.
- The test accepts subclasses; in particular, put `bool()` before `int()` when their handling must differ.
- Do not confuse this test with a table indexed by `type(value)`, which distinguishes exact classes.
- Positional patterns depend on `__match_args__`; dataclass and NamedTuple can generate it, while an ordinary class may need to declare it.
- A positional pattern that is too long or applied to a class without a positional contract may raise `TypeError` instead of simply failing to match.
- Prefer named attributes when the meaning of positions is ambiguous or field order may evolve; these patterns do not depend on that order.
- A named class pattern can check only a subset of attributes; `Class()` tests the type without requiring all its fields.
- For certain built-in types such as `int(n)` or `str(s)`, the single position captures the entire value; do not generalize this exception to ordinary classes.
- A guard is evaluated only after the pattern succeeds and can use its captures; a false guard allows the next case to be tried.
- Put relationships between captures, ordering comparisons and computed tests that shape alone cannot express in a guard.
- Prefer a literal pattern to a guard that only compares against that same literal, unless comparison against an unqualified constant is needed.
- Use captures only in the branch that defines them; a false guard may leave names bound without the body having executed.
- Do not depend on partial captures after a pattern fails: their possible retention is not a portable contract.
- Nest patterns when the depth is fixed and readable; for a recursive tree, handle one level, then call the function again on the children.
- Computing a simple representation of the subject before `match` can replace repeated guards; retain this preparation if it makes dispatch clearer.

### Exhaustiveness and the Axis of Extension

- For a closed family of variants, explicitly define a type union or an Enum rather than a supposedly complete open base.
- Use the alias syntax available on the target Python; a union can be named without imposing the `type` statement from recent versions.
- End closed-family handling with a case that calls `assert_never(subject)`; the checker can then report the unhandled variant after type narrowing.
- Actually run the project's checker: the annotation and `assert_never` alone do not produce static proof when the program starts.
- At runtime, an unexpected value reaching `assert_never` raises `AssertionError`; annotations do not block incorrect calls.
- A declared return type excluding `None` can reveal a missing path; a `match` used only for its effects does not benefit from this indirect check.
- A guard can reject values of an already recognized type; do not count that type as fully covered without examining the rejection path.
- An open hierarchy is not exhaustive merely because all its current subclasses are listed; other types can appear later.
- Prefer behavior carried by each type if new variants must be added without editing a central dispatch.
- Prefer external operations on a closed union if the variants remain stable and new operations arrive often.
- Compare actual costs: adding a type requires a case in every centralized operation; adding an operation through methods requires touching every type.
- A value table avoids a long chain of comparisons and can evolve at runtime; do not promise a measurable gain on just a few cases.
- An expensive default passed to `dict.get()` is computed before the call, even on success; choose a branch or access with targeted handling if its computation must be deferred.

### Exceptions and Cleanup on Exit Paths

- Attempt the operation and catch its expected failure when that expresses the contract better than approximate or race-prone prechecks.
- Do not replace a conversion with `isdigit()`: the predicate may reject convertible inputs and accept characters that the conversion rejects.
- Limit the `try` to the operation liable to produce the recoverable failure; do not pass off a later programming error as that failure.
- Catch precise types, from most specific to most general; a bare `except` also catches user interruptions.
- A broad catch of `Exception` remains a boundary decision, not universal recovery; re-raise with `raise` if no correct response is possible.
- The `else` of `try` contains the normal continuation after success, outside the scope of the associated `except` clauses.
- Use `raise NewError(...) from error` when the cause explains the failure; suppress its display with `from None` only if that disappearance is intentional.
- Reserve `finally` for cleanup: an exit through `return`, `break` or `continue` can override an exception or return already in progress.
- Prefer `with` for a resource with a context manager; its cleanup occurs on normal exit, return or exception after successful entry.
- Do not confuse a cleaned-up resource with a deleted name: the object may remain bound after the block while closed and unusable for another operation.

## Procedure

1. Identify the target Python and map the required paths: success, empty input, absence, unexpected input and recoverable failure.
2. Choose a condition, table, loop or pattern according to the question; justify any central dispatch over a family of types.
3. For each loop, check progress, sentinel, exit scope, possible mutation and the length policy for parallel iteration.
4. For each `case`, identify constants, captures, structural constraints, guard and fallback branch; reread bare names in isolation.
5. Declare genuinely closed sets and check remaining cases with the checker; do not demand fictitious exhaustiveness over an open base.
6. Run empty, boundary, no-match, false-guard and early-exit paths; also confirm cleanup and failure propagation.

## Pitfalls

- A loop's `else` does not mean "the body never succeeded"; only the termination path determines its execution.
- A bare constant or a type name without parentheses can turn a test into a capture of any value.
- A mapping with additional keys or a boolean received as an integer may satisfy a pattern that seemed too narrow on reading.
- A false guard does not necessarily erase captures; using them elsewhere makes the result depend on the history of cases.
- A silent fallback case can hide a lost variant; an annotation alone does not make the family closed at runtime.

## Verification

- Every loop exit and every `else` has been exercised, including with empty input; relevant variables are defined on all their paths.
- Parallel-iteration lengths, container mutations and sentinel-based acquisitions have a tested contract, not just an implicit assumption.
- Tests distinguish literals, qualified constants, captures, booleans, subclasses and non-sequence shapes when these cases are admissible.
- Incomplete mappings, additional keys, false guards and the absence of a matching pattern have the intended behavior.
- For a closed family, the executed checker detects a variant added without handling; for an open family, extension does not depend on a falsely exhaustive list.
- Unexpected exceptions remain visible, and cleanup replaces neither their propagation nor the function's result.
