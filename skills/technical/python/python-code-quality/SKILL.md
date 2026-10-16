---
name: python-code-quality
description: Review and simplify Python code design.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Python Code Quality and Design

## When to Use

- Write or review Python that works but remains difficult to understand, extend or maintain.
- Replace a direct translation from Java or C++ with a construct suited to the language.
- Choose an abstraction, assess coupling or refactor after a new requirement.
- Recognize a pattern's intent without turning its name into an architectural obligation.
- This scope concerns reasoning about code; it prescribes neither a deployment environment nor a framework.

## Philosophy

Seek the smallest construct that solves the observed problem, not the most general design imaginable.
A pattern retains its intent when Python already provides its structure; removing that structure is an improvement, not a lack of sophistication.
A good abstraction makes change less costly without erasing information its clients need.
Operational synthesis of Thinking in Python, by Bruce Eckel; corpus a8feb860.
Respect the Python version actually supported by the project: the corpus's recent target does not authorize any implicit version upgrade.

## Rules

### Readable Syntax and Predictable Names

- Make indentation match the actual block structure; use four spaces and do not mix tabs and spaces.
- End block headers with a colon; avoid semicolons and multiple statements that artificially compress the code.
- For a long statement, use continuation within parentheses, brackets or braces rather than a split that is difficult to follow.
- Do not confuse blocks with scope: an assignment in an `if` or a `for` may remain visible after the block.
- Check that an assignment executes on every path before the name is used; indentation alone does not guarantee its binding.
- Use `snake_case` for variables, functions, methods and files; `PascalCase` for classes; uppercase to indicate constants.
- Reserve the exception of classes named like functions for objects actually used that way; do not make it a general style.
- Do not infer runtime protection from an uppercase name: it signals an intention to the reader.
- Retain the project's consistent conventions and use its existing linter rather than creating arbitrary local rules.

### References, Values and Mutation

- Read an assignment as binding a name to an object; it does not copy the object.
- Explicitly distinguish reassignment from mutation: reassigning a name leaves its previous aliases unchanged, while mutating the object may affect them all.
- Use `==` for value equality; reserve `is` for intended identity, notably `is None` and other singletons.
- Do not use the identity of strings or small integers as a value test: sharing optimizations do not provide that contract.
- A slice or shallow copy of a list recreates the outer structure, not the nested elements; check which objects remain shared.
- Use a deep copy only when the need is also to duplicate the contained objects; an assignment cannot provide this isolation.
- Do not mechanically replace `x += y` with `x = x + y`: for a list, the first form modifies it in place and the second produces a new one.
- For immutable numbers, understand that augmented assignment rebinds the name to the result rather than modifying the shared number.
- Prefer immutable data when it does not need to evolve, without confusing the immutability of a container with that of its contents.

### Numbers and Truth

- Distinguish `/`, division that produces a float for integer operands, from `//`, division rounded toward negative infinity.
- Test negative cases when porting: the integer quotient is not truncation toward zero, and the remainder `%` follows the divisor's sign.
- Do not assume Python integers have a fixed width; they do not overflow like bounded integers in other languages.
- Separate exact integer arithmetic from floating-point arithmetic; do not import the guarantees of one into the other.
- Account for ties-to-even rounding with `round()` and formatting; do not assume rounding is always away from zero.
- Use `_` separators in literals to make large numbers readable without changing their value.
- Use `+= 1` and `-= 1` to increment or decrement; Python has no `++` or `--` operators.
- A boolean is also an integer: summing conditions can count true cases, but `True` does not constitute a numeric type distinct from `int`.
- Prefer `if items:` to a length test when the question is simply whether the container is empty.
- Remember that an object's truth value can be defined by `__bool__()` or, failing that, `__len__()`.
- `and` and `or` short-circuit and return an operand, not necessarily a boolean; do not annotate their result based on their names alone.
- Use `x or default` only if all false values should be replaced; preserve zero or empty text with an explicit `None` test.
- For masks, distinguish bitwise operators from logical operators; `~x` does not invert a fixed-width word.
- Do not expect `@` to perform a product on built-in numbers: matrix multiplication depends on the type and differs from decorator syntax.

### Strings and Interpolation

- Strings are immutable: retain a transformation's result if it must be reused.
- Choose quotes that limit escaping; use triple quotes when newlines are part of the text.
- Use a raw string for literal backslashes, accounting for the impossibility of ending that literal with a lone backslash.
- Use built-in search, split, replacement and joining operations rather than character-manipulation loops without a particular need.
- Do not use `strip`, `lstrip` or `rstrip` to remove an exact prefix: their argument denotes characters, not an indivisible substring.
- Use `removeprefix()` and `removesuffix()` to remove an exact leading or trailing substring when the target version supports them.
- `+` does not implicitly convert a number to a string; use an explicit conversion or an f-string.
- Prefer an f-string to produce ordinary text; its expression is evaluated and its result rendered immediately.
- Use the format specification for precision, width and alignment; `!r` shows a representation useful for diagnosis, and `=` labels an expression.
- Do not rewrite old `%` or `str.format()` uses merely because they exist: they remain valid, and a migration must improve the code concerned.
- Consider a t-string only if the target version supports it and a consumer needs to distinguish literals from values before assembly.
- A t-string produces a structured object, not a finished string; the consumer must actually quote, escape or reject interpolations according to its domain.
- Do not promise security based on interpolation syntax alone, or repurpose an illustrative character rejection as general protection.
- A template consumer must not assume strict alternation between text and values: iteration may omit empty literals.

### Abstractions, Dependencies and Cohesion

- Before adding a new class, check whether a function, dictionary, module or language protocol suffices.
- A class that merely hosts a method is not justified by that organization alone.
- Name the axis of change based on real requirements; repeated changes in the same place are more useful evidence than anticipated flexibility.
- Separate what changes from what remains stable; do not build a variation mechanism when nothing varies.
- Treat an idiom, a specific solution and a general pattern as possible stages, not as a ladder that must be climbed.
- For each abstraction, identify the details it erases and confirm that no legitimate client needs to recover them.
- Also examine the work hidden behind the interface: copying, sorting or indirect access can become dominant at the actual data size.
- Assess coupling by what one part knows: parent details, concrete class, interface, call signature or a simple value.
- Do not confuse a typed dependency with the absence of a dependency: a `Protocol` avoids declared inheritance, but its members remain a contract.
- Prefer a function signature when the client needs only one operation; do not create a multi-method interface without a use for it.
- A pattern often moves a dependency rather than removing it; locate the part that must still name the concrete classes.
- Accept a concrete dependency when it is deliberately placed at an assembly point that is inexpensive to change.
- Do not reach into the internal details of indirectly obtained objects; request the required service through an explicit interface.
- Group elements serving the same subject in one component; separate ideas that can evolve independently.
- Prefer composition to vary a collaborator without inheriting its implementation details; retain inheritance if substitutability is genuine.
- Check that a subtype meets the expectations of the base type's clients, not just the names of its methods.
- Factor out duplication that expresses the same intention for the same reason; accidental resemblance is not enough.
- Make common cases simple, rare cases possible and interfaces consistent; a behavioral exception imposes a memorization cost.
- Remove a layer if removing it eliminates neither necessary behavior nor useful isolation; choose between two sufficient solutions by their simplicity.
- Make computations pure when possible: equal inputs produce the same result, without observable changes to the outside world.

### Refactor Along the Two Axes of Extension

- Distinguish adding a type from adding an operation; a design often favors one at the expense of the other.
- A `match` that enumerates all subclasses of an open family requires maintaining the list and may silently ignore a new type.
- If the operation only groups by exact class, a dictionary indexed by `type(obj)` avoids this enumeration.
- Do not treat this replacement as purely syntactic: a subclass then gets its own key, unlike with a parent class pattern.
- For groups created on first occurrence, `defaultdict(list)` provides a fresh list; a dictionary annotation does not create this behavior.
- Leave a uniform operation as an ordinary function that reads the relevant attributes; dispatch adds nothing if the algorithm does not vary by type.
- Keep methods on a small, controlled hierarchy when each type naturally carries its responses and operations remain few.
- Consider `functools.singledispatch` to add operations that vary by type without modifying an external hierarchy or spreading new operations across every class.
- With `singledispatch`, the implementation is selected on the first argument and may be inherited according to the MRO; it is not an exact-class table.
- A default response must be genuinely valid for unregistered types; otherwise raise `NotImplementedError` to make the omission visible.
- Do not add methods from arbitrary modules: that forces readers to search for a class's behavior outside its definition.
- Measure a refactoring by the locations changed and the data preserved, not just by the number of lines removed.

### Use Pattern Vocabulary Without an Imposed Catalog

- Describe the problem first: creation, interface adaptation, algorithm selection, notification, a tree or state restoration; the name comes afterward.
- Reduce Strategy and Command to passing or storing a function when that suffices; a chain can be a list of functions tried in order.
- Recognize that a shared module, a table of classes or the iteration protocol may already fulfill the intent of Singleton, Factory or Iterator.
- Distinguish Adapter, which converts an interface, Façade, which simplifies a subsystem, and Proxy, which controls access to another object.
- Distinguish State, which changes behavior according to state, from a state machine, which selects transitions in response to inputs.
- Distinguish injecting a collaborator from outside from looking up that collaborator in a registry; both move control without exposing dependencies in the same way.
- Keep architectural, persistence, messaging and cloud names at the level of intent described: their presence in a catalog establishes no implementation recipe.
- Do not infer a deployment, recovery or consistency recommendation from a mere mention of Circuit Breaker, Saga, Repository or Event Sourcing.

## Procedure

1. Identify the target Python, conventions and checks already in use; record the behavior to preserve.
2. State a concrete requirement and the observed axis of change; list the components affected today.
3. Check the shared references, truth values, numeric operations and string transformations involved.
4. Write the minimal solution, then compare the proposed abstraction: erased details, hidden work and moved dependencies.
5. Test adding a type and adding an operation separately; note the changes required in each variant.
6. Refactor in stages while retaining behavioral tests and counts of incoming and outgoing data.
7. Remove layers that have become unnecessary, then run the project's tests and checks on its supported versions.

## Pitfalls

- A program may produce a plausible total after losing new types: check data preservation, not just the output presentation.
- A fallback branch or default implementation can hide a forgotten extension; prefer an explicit failure if no neutral response is correct.
- Generalizing before having several real cases creates options without evidence of usefulness; reject the speculative framework.
- A short abstraction can hide a high cost or erase an indispensable detail; counting lines is not enough to judge its quality.
- Recent syntax and APIs from the corpus are not necessarily available in an older project; do not raise its minimum Python version to adopt them.

## Verification

- Each new class or interface protects a named need; no pattern is present solely for its name.
- Conditional paths bind their variables before use; identity, mutation and equality are not confused.
- Zero, empty values, `None`, negative numbers and nested data have been exercised when their distinction matters.
- New subclasses do not silently disappear, and exact-class or inherited-class rules are intentional.
- The scope of a change, remaining dependencies and erased details can be explained without reconstructing the entire implementation.
- The tests run confirm the stated behavior; the project's tools pass without imposing an additional runtime, dependency or license.
