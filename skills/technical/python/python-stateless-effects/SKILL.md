---
name: python-stateless-effects
description: Compose and control effects with Stateless.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Effects with the Stateless Library

Original operational synthesis of Bruce Eckel's ideas, Thinking in Python, local corpus a8feb860. The source corpus is attributed to Bruce Eckel and carries CC BY-NC-ND 4.0; no new license is granted here.

## When to Use

- Compose computations whose declared dependencies and failures must remain visible until handled.
- Replace clocks, randomness, state, services, and outputs with deterministic scenarios without modifying the computation.
- Examine code using Stateless's `Need`, `Ability`, handlers, retry, caching, or parallel execution.
- Reserve this mechanism for systems where hidden contacts justify its discipline and the team accepts contracts throughout the chain; elsewhere, prefer explicit parameters and a simpler error policy.

## Philosophy

- Naming external contacts and binding their implementations at the boundary is a general design rule; the names and signatures below are the API of a specific library, not native Python constructs.
- Separate description from execution; compose the success path and choose the failure policy separately.
- Checking concerns the consistency of declared effects, not exhaustive coverage of contacts in the body. `Success` proves neither actual purity nor the impossibility of a runtime exception.
- Dependency: suned's Stateless project, Python module `stateless`. The corpus does not specify a version number for this library; do not invent one. Pin the installed revision and the checker in the project, then test the contracts below before adoption.
- The inference observations cited here concern `ty` 0.0.84 and a corpus targeting Python 3.15+; they do not guarantee all Python or checker versions. No executable library example is simulated here.

## Rules

### Three Parameters, Three Generator Channels

- `Effect[A, E, R]` names the required Abilities, declared errors, and result; its expansion is `Generator[A | E, Any, R]`.
- `A` is bounded by `Ability[Any]`, `E` by `Exception`. The driver treats a yielded object that is an `Exception` as failure, and others as requests; do not create a type combining both roles.
- `Success[R]` means `Effect[Never, Never, R]`, `Depend[A, R]` means `Effect[A, Never, R]`, and `Try[E, R]` means `Effect[Never, E, R]`: absent channels contain no declared values.
- A generator exchanges a yielded request, a sent response, and a `return` result. `yield from` forwards requests to the driver and responses to the inner generator, and takes its final result as its value.
- An Effect's receiving `Any` cannot type a response that varies with each request. Prefer `yield from need(C)` to bare `yield Need(C)`: the response type then comes from the accessor's specialized return type.
- `need(C)` constructs `Depend[Need[C], C]`; `Need[C]` is a request whose `t` field carries the requested class, not the instance to use.
- An ordinary service `C` is requested with `Need[C]`. A subclass of `Ability[T]`, including `Async`, is itself the Ability and is named directly in the channel; `Depend[C, R]` is not suitable for an ordinary service class.

### Description, Functions, and Single Consumption

- Calling a generator function creates the Effect without executing its body; the driver starts and then resumes the computation. Ordinary calls needed for construction, however, can act immediately.
- `success(value)` produces `Success[R]` from an already computed value. An ordinary function can return it; in a generator function, write `return value`, not `return success(value)` if `R` expects that value.
- An expression passed to `success` is evaluated before the call: neither a division nor a `print` placed in an ordinary function is magically deferred.
- Compose each sub-Effect with `yield from`. A call left on its own constructs and then discards a description; if another `yield` remains in the body, tools may report no omission.
- A generator Effect can be consumed only once. A second execution of the same exhausted object can return `None` without reporting the error; keep producer functions, not generators, in a reusable registry.
- `success` is an exception to this consumption rule: its `SuccessEffect` object directly implements the protocol and can return the same constant again. Do not generalize this case to other Effects.
- `supply`, `catch`, `throws`, `retry`, `repeat`, `memoize`, and `fork` operate on functions so that they can construct new descriptions; distinguish the function, the function call, and the produced Effect.

### Supplying Dependencies

- `supply(instance)(function)` constructs a handler and then a bound function; `supply(instance)(function)(arguments)` constructs its Effect. `supply(*instances)` accepts multiple dependencies.
- The handler statically removes the `Need[T]` corresponding to the supplied types; at runtime, it looks for an instance with `isinstance(instance, request.t)` and always responds with that instance during the run.
- Each caller must declare unresolved needs even if it requests them only indirectly. The union `Need[X] | Need[Y]` represents variants of a request; the program may request both during its lifetime.
- The corpus's `supply` signatures cover one to nine arguments. Beyond that, the variadic implementation may work, but the overloads no longer check the call; split it across successive handlers and reconsider an overly broad computation.
- The handler closest to the computation answers first; the outer one receives only what remains. A fallback can thus provide a genuine default, but must not hide a forgotten binding.
- `need` takes no default-value parameter, and Stateless has no global provider registry. Supply and inspect instances explicitly.
- When two instances satisfy the same runtime need, the first in the `supply` arguments wins; no diagnostic enforces uniqueness. Supply one candidate per role and distinguish ambiguous interface shapes.

### Interfaces and Static Upcasting

- To avoid a test double accidentally inheriting a real I/O method, define a `Protocol` interface instead of reusing a concrete class without examination.
- An interface used as a `need` target must be `@runtime_checkable`, since `supply` performs an `isinstance`. This runtime check checks member presence, not signatures or behavior; the checker separately checks static compatibility.
- `supply` reads the argument's static type. A directly supplied subclass may be seen as `Need[Subclass]` and leave `Need[Interface]` in the type, even when runtime selection would work.
- `as_type(Interface)(implementation)` widens the static type; the received function is typed `(Interface) -> Interface` and checks compatibility. At runtime, it returns the same object; it is neither adaptation nor an additional check.
- `typing.cast` asserts without checking; do not substitute it for this upcast as though the guarantees were identical.
- A boundary function whose parameters are annotated with the interfaces allows `supply` calls with those types without repeating `as_type` at each call.
- Do not rely on an annotated local variable to prevent narrowing toward the concrete implementation in the project's checker; inspect the type actually supplied.
- Built-in dependencies are concrete classes: `stateless.console.Console`, `stateless.files.Files`, and `stateless.time.Time`. Test doubles must satisfy their nominal check, generally through inheritance; replace all methods that might access real I/O.
- `stateless.console` exposes the `print_line` and `read_line` accessors; `stateless.files.read_file` reads the entire file and carries the failures `FileNotFoundError` and `PermissionError`. Do not confuse these services with an educational `Console` defined in your own module.

### Domain-Specific Abilities and Handlers

- A custom request subclasses `Ability[T]`; its fields carry the necessary data, and `T` names the response. An accessor returns `Depend[Request, T]` and delegates to the instance with `yield from Request(...)`.
- `Ability.__iter__` provides the generator that yields the request and then returns the response. An Ability without data may have no fields; a write can carry its message and expect `None`.
- `handle(handler)(function)` removes the Ability recognized in the handler's parameter annotation. Annotating this parameter is mandatory; otherwise, `handle` raises `ValueError` during decoration.
- The handler is an ordinary function that receives the request and returns a response, not an Effect constructor and not the continuation. With the corpus's `record` helper, requests use `slots=False` because their base has no slots; this helper is not a standard API.
- The runtime dispatch of `handle` erases generic parameters via `get_origin(t) or t`: a handler annotated `Need[X]` can therefore select other `Need` requests at runtime while its type removes only the announced need. Do not use it as proof of precise generic filtering.
- For fixed responses throughout execution, supply an instance; for a scripted clock, a controlled draw, or an implementation changing with each request, use a handler that chooses on each request.
- An ordinary handler that raises fails outside the Effect's channel; `catch` around the consumer does not automatically convert that exception into data.
- Avoid letting an exhausted response script leak `StopIteration`: in the corpus's handler, it can be interpreted as the end of the Effect and silently produce `None`. Check exhaustion or use an explicit error such as `IndexError`.
- For shared state, separate a read request `Ability[T]` from a write request `Ability[None]`; entrust the cell to handlers and create one per test. A counter owned by a single function remains a local variable.
- If a filename and timestamp must describe the same instant, read once and reuse the value; a handler crossing midnight must make it possible to detect two inconsistent reads.

### Entering and Leaving the Error Channel

- `throws(*ErrorTypes)` is applied as `@throws(Error)` and converts only the named exceptions into yielded values; it can wrap an ordinary function or a function already returning an Effect.
- `throw(error_instance)` constructs `Try[E, Never]`; `yield from throw(error)` puts the failure directly into the channel and does not return a normal result.
- An error produced by `throw` outside the declared channel can be rejected at `yield from`; a `raise` not covered by `throws` can pass through the types without a diagnostic.
- Declaring a failure does not handle it. The driver accepts remaining errors and reinjects them as exceptions; an unhandled error can therefore escape `run`.
- `catch(*ErrorTypes)(function)` moves only the named errors from the channel into the result union. For `Try[KeyError | ValueError, int]`, catching `KeyError` leaves `Try[ValueError, int | KeyError]`.
- Then examine the returned union. `Success[int | KeyError]` means the channel is empty, not that the business operation found an integer; returning an exception as data differs from raising it.
- `catch_all(function)` is imported from `stateless.effect`, not from the package root. It turns all declared failures into result branches without catching exceptions raised outside the channel.
- With a named `catch`, a new failure requires handling or propagation; with `catch_all`, write a controlled return union or an exhaustive `match` ending in `assert_never` to detect this evolution.
- A `catch` naming an absent error may be accepted and add a useless result branch without handling anything. Inspect the channel at the exact point of decoration.

### Why except Does Not Replace catch

- If `run` directly drives an Effect, its error injection through `generator.throw` may reach an `except` around the inner `yield from`; this does not subtract the error from the annotation.
- An interposed `supply` drives its own `Handler`: the reinjected error can be raised in that frame and bypass the inner `except`, even if the dependency had not yet been requested.
- A `catch` receives the yielded value before the driver and can terminate that path without resuming the generator; the inner `except` then becomes inactive.
- Use `catch` to handle the channel compositionally; explicitly test handler layers rather than deducing behavior from an isolated Python `try`.

### Composition and Launch Boundary

- Compose the program through functions using `yield from`: needs and errors are unioned, failure stops subsequent steps, and the computation does not have to scatter error checks between its steps.
- Supply already constructed leaves with `supply`; produce computed dependencies through an explicitly composed Effect. There is no effectful constructor layer that automatically resolves a graph.
- For families of coordinated implementations, write one assembly function per scenario; a flat list of `supply` values does not guarantee compatibility between their roles.
- `run(effect)` expects a channel compatible with `Effect[Async, Exception, R]`: any other remaining Ability is statically rejected if the checker retains it. Without checking, it causes `stateless.errors.MissingAbilityError` at runtime.
- `run` is implemented as `asyncio.run(run_async(effect))`: it creates and closes a loop on every call. Launch once at the synchronous boundary, not at every step of a pipeline.
- In an already active loop, use `await run_async(effect)` at the request boundary; `run` causes `RuntimeError` there and can leave an unawaited coroutine. The type does not record the loop's existence.
- `wait(awaitable_or_task)` introduces `Async` and returns the awaited result. `stateless.time.sleep(seconds)` is already an Effect: compose it directly with `yield from`; it introduces `Need[Time] | Async` and returns `None`.
- `Time.sleep` is an asynchronous method; to eliminate real waits, supply a compatible test double that records delays and returns without waiting.

### Retry, Repetition, and Caching

- `retry(schedule)(function)` creates a fresh description and replays the entire body on every attempt, including writes already performed. Decide idempotence before decoration; the type does not prove it.
- Retry handles all declared errors without filtering by class. First move a deterministic error out of the channel with `catch` if it must not trigger another attempt, then handle its result branch.
- `stateless.schedule.spaced(timedelta(...))` produces an indefinite fixed interval; `recurs(n, schedule)` bounds the number of yields. In the corpus, `recurs(3, spaced(...))` gives three total attempts, not an initial attempt plus three retries.
- The type after retry adds `Need[stateless.time.Time]` and `Async`, and replaces `E` with `stateless.functions.RetryError[E]`. Supply the clock and catch `RetryError`, not just the original error.
- After exhaustion, failures are gathered in `RetryError`. In the corpus's implementation, the advertised `.errors` attribute is not initialized and raises `AttributeError`; the errors reside in `.args[0]`. Check this contract in the project's revision before depending on it.
- `repeat(schedule)(function)` continues executions until the schedule is exhausted and collects their results in an ordered tuple; a propagated error remains the original error, unlike retry, which stops at the first success.
- `repeat` also introduces `Need[Time]` and `Async`. Repeated calls really modify the environment; this is not reading a retained result several times.
- `memoize(function)` preserves the type and caches by arguments; its wrapper returns the recorded result rather than driving an exhausted generator.
- The key does not contain bindings: two different databases supplied to the same memoized call may yield the first one's response without calling the second. Isolate the cache by environment or make environment identity explicit in the key.
- Do not confuse a replayed result, replayed work, and the uniqueness of an instance; these are three distinct contracts.

### Fork, Errors, and Resources

- `fork(function)` or `@fork` returns a function that requests `Need[concurrent.futures.Executor]` and produces `Task[R]`; `yield from wait(task)` introduces `Async` and retrieves the result.
- Supply the worker's needs before `fork`, except for `Async`, which its driver knows how to interpret. A worker executes its Effect with `run`; a remaining business need does not satisfy the intended overloads.
- Submit all tasks before awaiting them if overlap is desired; forking and then waiting on every iteration serializes the work.
- The `Task` does not carry the error channel, although the overloads accept workers declaring a failure. This becomes an ordinary exception in the worker and then at `wait`, beyond the reach of an outer `catch`.
- Move declared errors into the result before submission: for a function not yet forked, supply its needs and then apply `fork(catch_all(bound_function))`. The awaited result can thus carry `R | E`; undeclared exceptions remain possible.
- Supply the executor under its general type, for example through `as_type(Executor)(pool)`, and keep its lifetime in a `with` outside the launch. For processes, respect serialization and the `if __name__ == '__main__':` guard; do not promise that a simple replacement will always work.
- Shared-state handlers provide no atomicity. Two workers can interleave reads and writes without a type error; protect or remove that sharing.
- Resources remain subject to Python discipline: `with` inside an Effect for a local lifetime, or `with` / `contextlib.ExitStack` at the boundary to enclose the program. There is no native finalizer or scope linking acquisition in one Effect to release after another.

### Actual Scope of Guarantees

- Name intermediate steps and inspect `reveal_type` after each handler. Under `ty` 0.0.84, catching and then supplying can yield `Never` where supplying and then applying `catch_all` leaves `Unknown`; an actually unsupplied need must still be checked separately.
- Require negative tests for a missing declaration, an absent binding, and a residual error. Type aliases and nested compositions must be tested with the pinned checker, not assumed correct.
- Handlers do not capture a reusable continuation; they return a response, and resumption happens once. Retry reconstructs the entire computation; it does not duplicate a suspension point.
- No analysis of undeclared direct I/O, no separate defect channel, no automatic graph construction, and no general detection of provider cycles.
- The corpus provides only fixed schedules and repetition counts; do not invent exponential backoff, jitter, timeout, race, fallback, finalization, an atomic cell, or a circuit breaker in this API.
- Integrating a third-party function requires an explicit route through a need, an error wrapper, or composition; an annotation alone does not convert it into an Effect.

## Procedure

1. Pin the runtime, library, and checker; inventory contacts and expected errors. Criterion: every promise concerns a testable version, and every contact has a channel or an explicitly accepted boundary.
2. Define interfaces or requests and accessors; compose with `yield from`. Criterion: precise response types and no discarded sub-Effect.
3. Build scenarios and bind dependencies. Criterion: every request has an intended provider, without ambiguous candidates or unintended inheritance of real I/O.
4. Choose where errors become data or boundary exceptions. Criterion: all returned unions are examined, and out-of-channel exceptions remain identified.
5. Add retry, repeat, memoize, or fork only after analyzing repetitions, environments, channels, and resources. Criterion: each transformation has an expected type and a specific runtime test.
6. Launch at the appropriate boundary, then inspect outputs, state, and types. Criterion: a controlled incorrect scenario fails where the contract says it will, and no result is attributed to an API simulation.

## Pitfalls

- Believing that `Success` prevents a `raise`, that `catch` intercepts everything, or that a declared error must be handled before `run`.
- Reusing a consumed generator, forgetting `yield from`, or confusing a bound function with the Effect it produces.
- Hiding a missing need with a fallback; supplying two implementations indistinguishable at runtime.
- Reading a real clock in a test, letting `StopIteration` escape a handler, or sharing its mutable cell between tests and workers.
- Retrying a charge already performed, memoizing multiple environments together, or expecting `fork` to preserve errors in the type.

## Verification

- See a diagnostic when removing an Ability from the annotation, then when removing its provider; check that compositions and aliases do not hide it.
- Test success, each declared failure, an error outside `throws`, a handler exception, and a need remaining after partial handling.
- Compare an `except` under a direct driver, under `supply`, and under `catch`; check types and behavior, not just the final message.
- Check the same computation with a controlled real service, a recorder, and successive responses; test script exhaustion and crossing a time boundary.
- Test single consumption, discarded descriptions, the exact number of attempts, retry errors, repeated effects, and caching under an environment change.
- Check multiple simultaneously submitted tasks, the error union before fork, an undeclared exception at wait, state concurrency, and executor shutdown.
- Test synchronous launch and `await run_async` in an existing loop; do not claim runtime validation if Stateless is not installed in the verification environment.
