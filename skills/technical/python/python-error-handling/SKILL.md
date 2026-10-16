---
name: python-error-handling
description: Design and verify failure paths in Python.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Failure Paths in Python

## When to Use

- Define which errors to catch, propagate, translate, or return as values.
- Design a chain of fallible processing steps without losing context, partial results, or cleanup.
- Examine deferred and concurrent failures, notifications, and an effect system's error channels.
- Test what the caller observes after an error, including the state left behind.
- Do not automatically convert every program defect into an ordinary business response.

## Philosophy

A failure deserves a contract: its representation, context, and handling responsibility must be explicit.
Representing it as a value makes its presence visible in a signature; an exception remains suitable for nonlocal propagation.
Choose according to what the caller can do and which work must continue, not a principled opposition between the mechanisms.
The safety of an error path includes the final state, remaining tasks, and acquired resources, not just the displayed message.
An annotation describes an intention; it prevents neither an undeclared exception nor an abandoned result.
This original synthesis draws on Bruce Eckel, Thinking in Python, corpus a8feb860.

## Rules

### Decide the Failure Contract

- List expected failures, programming defects, cancellations, and interruptions before choosing a mechanism.
- Use an explicit result for ordinary failures the caller must distinguish and handle, following the project's conventions.
- Retain an exception for defects or conditions from which this caller cannot reasonably recover.
- The same missing file may be normal in a search and fatal at startup; judge from the operation and its contract.
- Use `T | None` when only absence matters; prefer a structured error if its reason determines what happens next.
- Define who reports, who recovers, and who propagates; avoid catches at every level that add neither action nor context.
- A failed attempt does not undo effects already produced; specify what remains acquired, recorded, or modified.

### Catch in the Right Place

- Limit the `try` to the operation whose failure is expected; place success handling in `else` if its errors must remain distinct.
- Catch precise types, from most specific to most general; a broad clause placed first masks the following ones.
- A bare `except:` also catches interruptions; `except Exception` generally lets them through but can still hide an ordinary bug.
- A broad catch is justified only by a boundary explicitly responsible for those defects, with an observable policy.
- Prefer EAFP when the operation is the true judge of validity: a preliminary test may be incomplete or become false before the action.
- Do not replace actual conversion with a supposedly equivalent predicate; the values they accept may differ.
- EAFP does not permit removing business checks: parsing a shape and accepting a domain value are two decisions.
- An invariant violation must be raised explicitly; a validation assertion may disappear in optimized mode.
- `check` and `TypeFailure` refer to illustrative helpers, not Python primitives already available.
- After rejected construction or mutation, check that the published state remains valid; catching alone repairs nothing.

### Preserve Identity, Cause, and Context

- Use `raise` without an argument to reraise the current exception without replacing it unnecessarily.
- When translating across abstractions, raise the business exception with `from error` to retain an explicit cause.
- Without `from`, an exception raised during handling retains implicit context; that is not absent context.
- `from None` hides that context in the usual report without necessarily erasing information carried by the object; choose it deliberately.
- Use `add_note`, available since Python 3.11, to add locally known context while keeping the exception's type.
- Add notes before returning the error as data; no traceback is printed automatically for a stored object.
- Read external notes with `getattr(error, "__notes__", [])`: their list may not exist before the first addition.
- Prefer structured fields for the business cause and notes for working context; do not parse a message to decide a branch.
- Avoid retaining exceptions indefinitely without need: their tracebacks may retain frames and their data.

### Do Not Lose the Failure During Cleanup

- Clean up in `finally` or a context manager; ban `return`, `break`, and `continue` exits from a cleanup `finally`.
- If cleanup raises, it can become the primary error and relegate the initial failure to its context; test this double failure.
- An `__exit__` returning a truthy value suppresses the block's exception, even if that value is merely a counter or a string.
- Return `None` for cleanup without suppression; suppress only a deliberately handled case.
- With `contextmanager`, surround the `yield` with a `try/finally`; the block's exception is reinjected at that point.
- Catching that exception around the `yield` without reraising it suppresses it; continuing after the block does not mean resuming the interrupted block.
- If `__init__` or `__enter__` fails after acquisition, that manager will not receive its own `__exit__`; clean up partial acquisition locally.
- Multiple managers exit in the reverse order of their entries; `ExitStack` organizes this policy for a dynamic set.
- The manager that fails to enter remains responsible for its own acquisitions; the stack cleans up those already entered.
- Do not use `__del__` to carry a recoverable error: its exceptions do not return to a caller who could handle them.

### Represent Success and Error Unambiguously

- Distinguish tagged success and failure variants rather than a union of potentially confusable payloads.
- `Ok` and `Err` name those roles in a common model; `Result` is not a native type automatically provided by Python.
- Reuse the project's existing representation rather than creating an incompatible family for a single function.
- Narrow with `isinstance` or `match` before reading the success value; do not unwrap without ruling out failure.
- Test the concrete variant classes, not a type alias whose runtime usage is not guaranteed.
- A function annotated with a result can still raise; the exhaustiveness of its outcomes requires review and tests, not just a static verdict.
- The checker may reject an incorrect reading of the result while accepting that it is ignored entirely; inspect all affected callers.
- If an error is a returned exception object, it no longer automatically triggers propagation; the consumer must examine that result.
- Do not claim a total function without specifying its domain, represented failures, and remaining operational limitations.

### Compose and Choose a Batch Policy

- For a dependent sequence, `bind` passes the success payload to the next step and lets failure short-circuit the remainder.
- Each bound step must return a result; an ordinary transformation requires explicit wrapping or a success-mapping mechanism.
- Keep the same error type throughout the chain or declare the actual union of errors; do not erase a variant to simplify the signature.
- To use several earlier successes, keep those values in scope through named steps or nested composition, without unreadable nesting.
- Distinguish computational dependency from input independence: short-circuiting on an independent input may hide other failures.
- For independent validation, decide whether you want the first error, all errors, partial successes, or an indivisible transaction.
- A comprehension interrupted before its assignment does not publish its partial list; retain per-item results if the contract requires them.
- Changing exceptions into values does not automatically preserve work: you must also choose a loop that collects and continues.
- Adapt only expected exceptions; a decorator catching every `Exception` also turns a `NameError` or another bug into an ordinary failure.
- Preserve the parameters and declare an adapter's new return type; `wraps` metadata is not enough to type its signature.
- In a pattern, `ValueError()` tests a class; the bare name `ValueError` captures a value and does not perform that test.
- The optional `returns` library offers result variants, composition, transformation, and combination notation; do not assume their signatures.
- Without an installed and verified version, describe these mechanisms rather than delivering a speculative API example or adding an unnecessary dependency.

### Handle Concurrent Failures and Notifications

- Respect the minimum version: `TaskGroup`, `except*`, and `asyncio.timeout` require Python 3.11.
- A `TaskGroup` supervises its tasks, cancels those still active after an ordinary failure, and waits for their termination.
- Its ordinary failures are grouped; use `except*` for the targeted members rather than assuming a simple `except` for the inner type.
- Do not promise how many failures will be simultaneous: scheduling order and cancellation speed influence the observed group.
- Tasks that have already succeeded retain their responses; inspect cancellation, exception, then result without confusing these states.
- With default `gather`, a first failure propagates while other tasks may continue; retain supervision of them.
- `gather(..., return_exceptions=True)` collects responses and failures in input order; examine each slot rather than treating the entire list as a success.
- Cancellation is not a business failure: `CancelledError` derives from `BaseException`; clean up and then reraise it if caught.
- A block timeout cancels cooperative work and exposes its `TimeoutError` on exit; handle that timeout outside the relevant context.
- Bounding the wait does not arbitrarily kill a blocking operation or undo effects already initiated.
- A synchronous responder that raises interrupts subsequent responders; choose stopping, collection followed by continuation, or a returned error according to the need.
- Changing callbacks to return results changes their contract; adapt those whose return was previously `None`.
- An asynchronous fan-out must not leave orphaned responders after a `gather` failure; supervise them and await their outcomes.
- Do not impose `TaskGroup` if the obligation is to notify all responders despite failures; instead isolate and collect each outcome.

### Make Deferred and Restoration Failures Visible

- A generator's body starts during consumption, not creation; surround the step that actually advances the generator.
- To reject an argument immediately, perform the check in an ordinary function that then returns the inner generator.
- `yield from` relays values, the return, and protocol signals; a loop that only reemits values is not equivalent.
- `throw` injects an exception at the suspension point; if handled, production may continue; otherwise it propagates to the driver.
- `close` requests termination through `GeneratorExit`; clean up without producing another `yield`, or a `RuntimeError` results.
- `hasattr` masks only `AttributeError`; a `PermissionError` from `__getattr__` can therefore make simple introspection fail.
- For a state machine, choose rejection or retention of state for an unexpected event; remaining in the state may repeat its action.
- During persistent restoration, reject or migrate an incompatible format before publication; successful loading may leave a missing or phantom field.
- Restorations that bypass the constructor may also bypass new invariants; reconstruct and check at that boundary.

### Locate Errors Within an Effect System

- Distinguish a declared error, a caught exception, and an actually handled failure; these operations do not offer the same guarantees.
- A deterministic exception and purity have several theoretical interpretations; prioritize outcome visibility here over a universal verdict on purity.
- To simplify a computation, compare an explicit result, targeted local handling, and a domain type excluding the bad value.
- Excluding a bad value moves rejection to its construction; handle that rejection at the boundary without claiming all errors have disappeared.
- In Stateless, the channel contains failures raised and then explicitly converted, or produced by the effect's failure mechanism.
- Declaring that channel does not require emptying it: final execution may still raise the remaining errors.
- A Python catch around a delegation may depend on the driver and intervening handlers; do not confuse it with handling the typed channel.
- Converting a declared failure into a value moves responsibility to a consumer branch; it does not turn the value into a business success.
- A catch of the entire channel also absorbs its future variants; retain an explicit return or exhaustive checking to make evolution visible.
- Unconverted exceptions remain outside the channel and can pass through its handlers; consistency of declarations does not prove their completeness.
- The `fork` mechanism described by the corpus loses the error type; convert declared errors into values before that parallel boundary.
- A retry policy reruns the entire body: check idempotence, effects already committed, attempt count, and maximum delay.
- The described retry acts on the entire channel; first move out deterministic rejections that have no chance of changing on the next attempt.
- After retry, the error type may be an exhaustion error containing the attempts; handle the final type, not just the initial error.
- Stateless's limitations belong to the implementation studied, not to Python's laws; check the installed version before any concrete use.

## Procedure

1. Enumerate fallible operations, including deferred calls, cleanup, and restoration; specify the expected observable state after each.
2. Choose propagation, recovery, translation, or a value for each family, then designate its responsible consumer.
3. Minimize protected blocks and add context where it is known; retain causes needed for diagnosis.
4. Audit resources and concurrent work on all paths, including entry failures, cancellation, and double failure.
5. Define the composition or batch policy and check that no result or still-active work is silently abandoned.
6. Run targeted tests, then the project's tests; distinguish static guarantees, executed behaviors, and unverified limitations.

## Pitfalls

- An error recorded and then ignored is not handled; an error suppressed by `finally` or `__exit__` is not a success.
- Recovery that returns a fallback value must respect the domain; do not invent zero, empty, or infinity without business meaning.
- An overly broad exception test may pass for the wrong statement; a test placed after the raising point in the same block does not execute.
- An explicit result offers neither automatic rollback, exhaustive catching, nor a guarantee that all callers examine it.
- Repeated or concurrent effects may remain visible after failure; do not promise atomicity absent from the mechanism used.

## Verification

- Test success, each expected error, and an unexpected defect that must pass through adapters; limit each exception-expectation block to the failing call.
- Check type, fields, useful message, cause, and notes; check final state after the exception-expectation block.
- For composition, prove that forbidden steps do not run and that independent steps run when the contract requires them.
- Inject failures after each acquisition, in the body, and then during cleanup; check release, order, and preservation of the initial error.
- Test cancellation, timeout, and multiple failures with controlled synchronization; check that every task has a supervised outcome.
- Test failing generator consumption, its termination, a failing notification, and incompatible restoration if those paths exist.
- Look for counterexamples to invariants using boundary inputs and property tests; a failure-free sample is not a proof.
- Report what was actually executed and the checker or dependency limitations without claiming unproven exhaustive handling.
