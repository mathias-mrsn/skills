---
name: python-effect-management
description: Analyze and isolate effects in Python.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Managing and Tracking Python Effects

Original operational synthesis of Bruce Eckel's ideas, Thinking in Python, local corpus a8feb860. The source corpus is attributed to Bruce Eckel and carries CC BY-NC-ND 4.0; no new license is granted here.

## When to Use

- Explain why a correct calculation fails depending on the environment, call order, or a hidden dependency.
- Isolate clocks, randomness, networking, storage, output, shared state, and errors to make tests controllable.
- Choose between explicit parameters, error contracts, an effect system, or experimental static analysis.
- Examine a proposal for tracking through `Annotated` or an AST-based checker without overstating what it proves.
- Do not introduce a generic system if a few parameters and a targeted error policy solve the problem.

## Philosophy

- An effect is what a call imposes on its caller beyond the ordinary result: an outgoing interaction, an incoming dependency, or the possibility of failure.
- Analyze the call chain, not just the visible body. A distant interaction becomes a property of the computation that depends on it.
- Keep a computational core that is easy to test and make external contacts replaceable at an explicit boundary; useful effects are not a defect to eliminate.
- Distinguish a checked description, behavior actually intercepted, and a trust assumption. A name in a type performs no interception.

## Rules

### Inventory of Contacts and Propagation

- Classify outputs: console, display, hardware action, networking, database, nonlocal mutation, lock acquisition, or coordination.
- Also classify incoming causes: time, randomness, file, database, or network reads, and reassignable globals. A read can make the result vary without modifying the source.
- A captured constant that does not change is not a variable external cause; do not equate every closure with impurity.
- Include exceptions that escape a call in the analysis, even if you adopt a definition of purity allowing deterministic failure for the same arguments.
- If a function calls an effectful computation, it inherits its unhandled contacts. Repeat the analysis up to the boundary and through callbacks.
- Distinguish confined local mutation from observable shared state; using a loop or a local accumulator is not enough to establish an external dependency.
- Separate two decisions: which effects are necessary, then where and how each is performed or absorbed.

### Transforming Failures Without Promising the Impossible

- Represent an expected failure as data with a discriminated result, or intercept the precisely expected exception and choose an explicit business response.
- A targeted catch handles only the named classes. If a validator called inside can produce another error, that error still needs to be propagated or handled.
- A wrapper catching all `Exception` loses the distinction between expected errors and bugs. Do not present a broad union of errors as a precise business classification.
- Move invariants into a type validated at construction when this simplifies subsequent functions; analyze constructor failure separately.
- Combine boundary validation with an explicit result: parse untrusted input, construct the valid value, then call the computation that uses this invariant.
- A type excluding zero eliminates that case in a computation that actually receives a valid instance; it proves neither the absence of other exceptions nor runtime validation of every annotation.
- Describe what was converted: an exception turned into data does not remove clock reads, writes, mutations, or other failures from the same body.
- A result annotation does not force the client to use the returned value. Check usages and error branches rather than promising their automatic handling.

### Two Levels of Isolation

- First separate pure computation from interactions to facilitate testing, caching, and independent execution; check that the data and dependencies actually justify that characterization.
- Then isolate each family: failures as data, causes as replaceable inputs, outputs as replaceable receivers that record actions.
- Provide a fixed or scripted clock, controlled randomness, and output captured by an object; test the computation without waiting, networking, or touching real outputs.
- Do not conclude that making a dependency substitutable makes its implementation pure: a test recorder can mutate its own list, and a real database continues to perform I/O.

### Tracking, Handling, and Late Binding

- Effect tracking indicates the categories a function may perform. Full effect handling adds interface/implementation separation and binding of the implementation after the computation has been defined.
- Concentrate test, production, tracing, or resilience variants at the binding point rather than scattering decisions throughout every client.
- Passing interfaces as parameters is the simplest manual form. The checker validates supplied arguments, but every intermediate level must forward them.
- Assess the cost of evolution: a new manual dependency changes signatures and calls along the path; an effect channel moves this propagation into types without necessarily inferring it automatically.
- A global registry or service locator makes the dependency substitutable but hidden in the body; constructor or parameter injection is more explicit and checkable at calls.
- A `ContextVar` propagates a value within a task context without an intermediate parameter; it does not declare the need in the signature, and a missing or incorrect context remains a runtime problem.
- A late-supplied implementation can itself read, write, or fail. Discharging an abstract effect does not mean the handler's effects have disappeared.

### Native Systems, Libraries, and Python

- In a native system with tracking, the compiler can infer the row, propagate effects from calls, check handlers, and subtract what is handled.
- Inference, row variables for callbacks, handler-related subtraction, and coverage of all libraries are distinct properties to assess; do not assume all of them from the word "effects."
- An algebraic handler can receive the continuation, meaning the rest of the computation; depending on the system, it resumes it, abandons it, or invokes it multiple times.
- A Python generator retains a suspended execution, not a copyable continuation. You cannot resume the same suspension point twice to replay two independent futures.
- Libraries generally encode contacts in a description type executed later. Distinguish construction, composition, and launch: ordinary code placed during construction can act immediately.
- `yield from` relays requests and responses from a composed generator; the driver answers requests. Confusing delegation with interpretation breaks the execution boundary.
- Python imposes syntactic propagation around `await` and `async def`, but this does not track all I/O, mutations, or errors and does not provide general handling of customizable effects.
- Library and checker diagnostics depend on their versions. The corpus's observations are neither a guarantee about every future tool nor an obligation to adopt a language presented for comparison.

### Carrying a Row with Annotated

- `typing.Annotated[T, metadata, ...]` carries metadata values, not additional type parameters. A reader that does not understand them treats the annotation as `T`.
- Attaching a row to the return annotation describes the call without cluttering its parameters, but only a dedicated tool gives it that meaning.
- The corpus uses educational markers `Performs` and `performs(*effects)`; these are not `typing` APIs. Their role is to carry a set of effects in metadata.
- To read this metadata at runtime, use `typing.get_type_hints(function, include_extras=True)` and then the recognized objects in `__metadata__`. Without `include_extras=True`, metadata is stripped.
- Do not evaluate untrusted annotations as though this were simple text analysis: runtime reading can evaluate expressions; the static prototype reads the AST without importing the program being analyzed.
- Separate an absent declaration from an empty declaration. The former may require inference; empty `performs()` asserts the absence of effects. A reader returning only an empty list loses this distinction.
- Without propagation or comparison against the body, a declared row is a structured comment. Two tools reading the same annotation are not automatically integrated.

### What a Real Checker Must Resolve

- Conceptually calculate a function's row by taking the union of its direct contacts and the rows of its calls, then removing effects actually handled.
- Resolve each callee: imports, aliases, methods, receiver type, hierarchy, dispatch, stored functions, and dynamic calls. The name alone is insufficient in general Python.
- For a method override, require its effects to remain compatible with those announced by the base contract.
- Propagate callback effects through a row variable; metadata containing a `TypeVar` ignored by the checker does not solve the problem.
- Subtract only where runtime interception exists. An annotation announcing a handler cannot turn a direct call to `input` into a substitutable dependency.
- Choose a policy for untracked code: assuming purity gives a lower bound; `Unknown` propagates uncertainty; external declarations move trust into a table or stubs.
- Runtime checking resolves the actual callee but covers only executed paths. Broader static checking requires inference and integration into the checking pipeline.

### The Corpus's AST Prototype: Exact Mechanism

- The prototype collects imports, definitions, written or obvious types, and explicit calls into per-function facts: name, optional declared row, hidden effects, and called names.
- It converts syntax errors into diagnostics; its core receives text and returns a report, while file reading and display remain outside.
- The table maps importable names to sets of effects; `fnmatchcase` patterns follow insertion order, and the first matching pattern wins. Place specific cases before general patterns.
- A target absent from the table becomes `Unknown`. Audit patterns declared pure separately: a broad pattern can hide poorly resolved behavior.
- Callers trust the explicitly declared row. Functions without a declaration take the union of the rows of their calls, repeated from empty rows until a fixed point; the finite vocabulary and monotonic growth ensure this calculation terminates.
- The check calculates the body's effects, removes those marked `hides`, and then reports those absent from the declaration. It accepts overdeclaration; it does not require exact equality.
- In this prototype, `hides` acts on this check, not as proof of a handler. For an inferred row without a declaration, the presented algorithm propagates the union of calls without subtracting `hides`.
- External stubs are declarative text supplied under the module name; they avoid `Unknown` for covered calls, but their assertions remain trusted.

### Prototype: Coverage and Blind Spots

- Resolved: direct names, dotted imports, methods on annotated receivers, `Final`, local aliases, literals, some comprehensions, and variables assigned from a call; the heuristic for the last case takes the callee's name as the type, not its real return type.
- A class call uses its locally defined `__init__`. A synthetic module function gathers the calls from top-level statements.
- Calls in a nested function or lambda also count among the enclosing function's calls; the prototype therefore does not faithfully model their execution time.
- Produce `Unknown`: a callback called as a parameter or variable, a call to the result of a call, a method on a field, an unresolved loop or destructuring variable, contradictory assignments, a union, an imported type alias, or an unknown inherited method.
- Escape without `Unknown`: a function passed as an argument to a tool declared pure; implicit calls through operators, properties, iteration, or context managers.
- Also escape: calls in class bodies, decorator arguments, or default values; construction through `__new__`, `__post_init__`, or inherited `__init__`; decorator wrappers.
- Marker recognition expects the written names `Annotated` and `performs`; qualified forms and aliases may be ignored. The first parameter of a `staticmethod` is incorrectly taken to be a receiver of the class.
- Pure table patterns can swallow incorrectly named targets: types `Any` or `object`, and a method chain where the return type is replaced by the previous method's name.
- `hides` is accepted without proof, even when it lies. An empty row or the checker's self-analysis therefore does not demonstrate purity in general Python.

## Procedure

1. Start from a problematic computation and inventory causes, outputs, and failures along its call paths. Criterion: every external contact has a category and an owner.
2. Move validation and dependency acquisition to a boundary; choose what remains data, a parameter, or an effect request. Criterion: the core can be tested on controlled values.
3. Define each dependency's interface and the supplied scenarios. Criterion: test and production use the same computation without hidden global substitution.
4. Choose the mechanism's level according to scale; document what is declared, inferred, intercepted, or merely assumed. Criterion: no guarantee is attributed to a mere annotation.
5. If tracking is added, address propagation, handlers, callbacks, and external code; do not deliver only row syntax. Criterion: a newly introduced effect produces the expected diagnostic.
6. Check blind spots and undeclared errors in the project's tool version. Criterion: known limits appear in the assessment, even if all positive tests pass.

## Pitfalls

- Reducing effects to writes and forgetting that a clock or mutable global changes results.
- Confusing deterministic exceptions, totality, and absence of I/O; these properties require separate checks.
- Presenting injection, implicit context, or `Annotated` as general inference of external contacts.
- Declaring an effect handled because a marker subtracts it, without proving interception or analyzing the handler.
- Selling the AST prototype as an exhaustive production tool because it analyzes itself.
- Fixing only visible `Unknown` cases and ignoring constructs that produce no diagnostic.

## Verification

- For each contact, produce a deterministic scenario: a fixed response, an evolving response, a recorded write, or an expected failure.
- Separately test invalid input, an invalid constructor, a handled known error, and a different error that must remain visible.
- Add an effect several calls deeper; check that intermediate contracts and the binding point must evolve.
- Distinguish an absent row from an explicitly empty row; test mutual recursion, an absent stub, a present stub, and pattern precedence.
- For the prototype, check a resolved case, an `Unknown` case, and a silent blind spot; record that the last invalidates a general purity conclusion.
- Keep the checker's reading/writing at the boundary; test its core with in-memory text and inspectable reports.
- Trust a green diagnostic only after seeing the same mechanism reject a controlled faulty case, with the versions actually used.
