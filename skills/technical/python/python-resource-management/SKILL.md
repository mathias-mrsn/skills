---
name: python-resource-management
description: Manage resource acquisition, lending, and release.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Python Resource Management

## When to Use

- Design or verify the closing of files, connections, sockets, and locks.
- Eliminate a leak after partial construction or an exceptional exit.
- Choose between `try`/`finally`, a context manager, a finalizer, and lending through a pool.
- Compose multiple acquisitions, including when their number varies at runtime.
- Manage an acquisition or release that must wait asynchronously.
- Do not introduce a pool for simple immutable values that can be shared without exclusivity.

## Philosophy

Memory reclaimed by Python does not constitute a policy for returning external resources.
Give each resource an owner and a release point visible in the program.
Keep the borrower's job simple by bringing acquisition, return, and failure handling together in a single contract.
Choose the least elaborate mechanism that guarantees this contract on the paths that can actually occur.

Original French synthesis of Bruce Eckel's Thinking in Python, corpus a8feb860; chapters Cleanup and Context Managers.
The corpus targets Python 3.15+; respect the project's version rather than imposing an upgrade.
The usual `with` rules apply to Python 3.11+; isolate the 3.15-specific behavior noted below.

## Rules

### Ownership and Explicit Closing

- Distinguish a resource created by the function from one merely received on loan.
- Close what the function owns; leave a stream supplied by the caller open unless ownership is explicitly transferred.
- Provide an explicit `close()` for a class that owns a resource.
- Make `close()` idempotent: an explicit close after the `with` must not release the same object twice.
- Do not confuse `del name` with destruction: `del` removes that binding, not the other references to the object.
- Do not infer a portable guarantee of immediate destruction from CPython's reference counting.
- Never make `__del__()` the primary return mechanism.
- Exceptions from `__del__()` do not propagate to the caller; a successful process exit does not prove that it succeeded.
- Avoid waiting and acquiring locks in a finalizer: its execution context can be unpredictable.
- Do not depend on finalizer order or on global variables being present during interpreter shutdown.

### The `with` Contract and Partial Acquisitions

- Distinguish expression evaluation, manager construction, entry, the user block, and exit.
- `as` receives the result of `__enter__()`, not necessarily the manager itself.
- After successful entry, `__exit__()` is called on normal exit, on an exception, and on a control-flow exit from the block.
- The guarantee begins only after `__enter__()` returns successfully.
- A constructor that acquires something and then fails must clean up its acquisition before propagating the failure.
- Keeping the constructor resource-free simplifies this risk, but moving acquisition into `__enter__()` is not enough.
- An entry that fails does not receive its own `__exit__()`; clean up all partial work locally.
- Put protection immediately after each successful acquisition, before the next operation that could fail.
- For multiple resources, keep release in the reverse order of successful acquisitions.
- Do not promise a cleanup guarantee against abrupt process termination: the protocol handles ordinary Python exits.

### Minimal Form and `contextlib` Tools

- Keep a local `try`/`finally` when the acquisition/release pair exists in only one place.
- Choose a manager when multiple calls share the protocol or when `with` clarifies the user contract.
- Look first for an existing solution in `contextlib`, then a generator, then a class.
- `closing(obj)` calls `obj.close()` on exit for a closable object lacking the context protocol.
- Do not systematically wrap an object that already provides the right context manager.
- `nullcontext(value)` supplies the value without closing it; use it for a borrowed stream or a branch without acquisition.
- `suppress(*types)` absorbs only the specified exceptions; `suppress()` with no arguments absorbs nothing.
- Do not copy a general-purpose educational exception-catching utility as a production policy.
- A manager that prints an exception does not necessarily check that it occurred: an exception test must fail if nothing is raised.
- Use a class when additional methods, persistent state, or reuse justify its structure.

### Generators, State, and Context Decorators

- A generator decorated with `contextmanager` must reach exactly one `yield` during a successful entry.
- Before the `yield`, acquire and prepare; the yielded value becomes the value bound by `as`.
- Surround the `yield` with `try`/`finally`: code merely placed after it is skipped when the block fails.
- The block's exception is injected back at the `yield`; catching it without re-raising suppresses it.
- Create a new generator manager instance for each `with`; a loop of `yield` statements does not make it reusable.
- A class is reusable only if its entry correctly resets per-use state.
- Do not equate successive reuse with nested reentrancy; a second entry can overwrite the same state attribute.
- Add `ContextDecorator` when the same management must also be usable around an entire function.
- The decorator produced by `contextmanager` recreates a manager on each call; an ordinary `ContextDecorator` subclass reuses its instance.
- Do not expect `ContextDecorator` to transform arguments, inspect the result, or decide to skip the call.
- Before Python 3.15, wrapping a generator function this way covers only generator creation, not its execution.
- In the Python 3.15 behavior described by the corpus, it covers iteration; for multiversion code, prefer a `with` inside the generator.

### Exceptions on Exit

- `__exit__(exc_type, exc, tb)` receives three `None` values on normal exit; otherwise, it receives the exception's type, instance, and traceback.
- Return `None` when the manager should only clean up and let exceptions propagate.
- Then annotate `__exit__()` with `-> None` to make an accidental status return statically detectable.
- Any truthy result suppresses the exception, not just `True`: watch out for counters and strings returned by a cleanup call.
- For intentional suppression, check the type and its subclasses precisely before returning a truthy value.
- Catching `BaseException` also includes `KeyboardInterrupt` and `SystemExit`; do not turn it into blanket suppression.
- Suppression resumes after the `with`, never at the line following the failing statement inside its block.
- If exit raises another exception, that becomes the visible failure; the original normally remains in `__context__`.
- Design exit so that it fails only for a reason that justifies superseding the initial failure; test this scenario explicitly.

### Composition and Asynchronous Operation

- Multiple managers in a `with` enter from left to right and exit from right to left.
- If a later entry fails, earlier entries are unwound; the failing entry retains its obligation to clean up locally.
- Use `ExitStack` for a dynamic or conditional number of managers and `enter_context()` to register successful entries.
- The stack cannot repair a resource acquired and then abandoned before cleanup is registered.
- Use `async with` if entry or exit must use `await`, with `__aenter__()` and `__aexit__()`.
- Use `asynccontextmanager` for an asynchronous generator and `AsyncExitStack` for their dynamic composition.
- Keep the same ordering, partial cleanup, and suppression rules in the asynchronous protocol.

### Finalization and Weak Observation

- Reserve `weakref.finalize()` as a safety net for a forgotten close, not for release at a deterministic time.
- Give the callback the necessary data without giving it a strong reference to the owner.
- Do not register `self.close` or a closure capturing `self`: the finalizer registry would retain the object.
- A finalizer runs at most once; explicitly invoking it allows immediate, repeatable closing without a double callback.
- For a class with `__slots__`, include `__weakref__` if weak-reference support is not already inherited.
- Observe instances with `WeakSet` for a collection of them or `WeakValueDictionary` for lookup by key.
- Avoid a strong registry that would extend the very lifetime it measures; disappearance remains dependent on the collector.
- When an object is retained, examine the references keeping it alive; forcing GC does not fix a strong reference that is still reachable.
- Treat `ResourceWarning` messages as a diagnostic for forgotten closes, not as proof of a correct protocol.

### Lending Objects Through a Pool

- A pool manages temporary exclusive custody of expensive objects; it does not automatically become their creator or destroyer.
- Remove an object when its loan begins and put it back in a `finally`, even when the client fails.
- A synchronized `Queue` can limit simultaneous loans, but `get()` on an empty pool waits indefinitely if no timeout is set.
- Provide validation before lending, reset, a policy for faulty objects, and a wait timeout according to actual requirements.
- Do not use `qsize()` as a lock or acquisition precondition: under concurrency, it is only an approximate snapshot.
- `with` creates no scope and revokes no reference; a client can keep using the object after returning it.
- If this risk must be prevented, expose a handle that can be invalidated on exit rather than promising that the manager alone prevents it.
- Distinguish pooling from sharing immutable values: one lends exclusively, while the other permits simultaneous users.

## Procedure

1. Inventory resources, their owners, their return methods, and the permitted transfers of custody.
2. Trace construction, entry, block, exit, and exit-failure paths; every successful acquisition must have its protection.
3. Choose the minimal form, with an explicit clause for any dependency on Python 3.15.
4. Group acquisitions and arrange their reverse unwinding without delegating partial cleanup to the client.
5. State the exception and reuse policy; for a pool, also define waiting and handle validity.
6. Exercise normal and faulty paths before concluding that the resource is correctly managed.

## Pitfalls

- A demonstration of immediate collection on CPython validates neither a closing deadline nor destruction order elsewhere.
- An entry moved out of the constructor can still leak if it fails after acquisition.
- A status `return` in `__exit__()` can turn a business failure into silent success.
- A pool restored to its initial capacity can still expose an invalid object or one still being used by a former borrower.
- A reusable class without per-call state can cease to be reusable as soon as a mutable attribute is added.

## Verification

- Verify closing on success, exception, and early exit, without relying on collection to trigger the result.
- Inject a failure after each partial acquisition; observe that only resources actually acquired are returned.
- Verify reverse closing order, `close()` idempotence, and propagation of unsuppressed errors.
- Check that a cleanup error retains the initial context and that its visibility matches the contract.
- For a pool, verify removal, return after an exception, reused identity, and documented behavior after the loan expires.
- For async code and decorated generators, execute the body and exit, not just creation of the deferred object.
