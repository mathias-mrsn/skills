---
name: python-concurrency
description: Choose and bound concurrency for Python tasks.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Python Concurrency

## When to Use

- Several independent waits can overlap, or a computation can usefully be divided across cores.
- Choose between coroutines, threads, processes, subinterpreters, and executors.
- Define supervision, errors, capacity limits, time limits, and work shutdown.
- Fix a race, a blocked loop, a deadlock, or a livelock.
- Connect a blocking call to an asynchronous application without concealing its constraints.
- Do not add a concurrent architecture to an isolated wait or an already fast enough program.

## Philosophy

Measure first: concurrency adds boundaries, coordination, and failure paths.
Overlapping waits does not mean running several computations simultaneously.
Simplicity comes from little shared mutable state and supervised lifetimes, not the number of workers.
Choose the model that fits the workload and its libraries, then bound what it can launch.
Success is complete only when every piece of work launched has a handled result, failure, or shutdown.

Original synthesis based on Bruce Eckel, Thinking in Python, corpus a8feb860.
Attribution does not imply any new license for the source text.

## Rules

### Choose Based on the Actual Bottleneck

- Identify CPU time, external waits, dependencies between operations, and the sequential portion before distributing work.
- For many cooperative I/O operations, choose `asyncio` if the stack provides asynchronous operations.
- For already blocking I/O, a thread pool sometimes avoids a rewrite; respect libraries' threading constraints.
- On CPython with the GIL active, multiple threads do not parallelize CPU-intensive Python bytecode.
- A native extension that releases the GIL can change this diagnosis; measure the code that actually runs.
- For divisible CPU work, the corpus suggests trying a compatible subinterpreter pool, then a process pool.
- This preference assumes compatible versions and extensions; in Python 3.11, choose among the mechanisms actually present.
- Reserve raw processes for persistent workers or exchanges that do not reduce to an input-to-result function.
- A free-threaded variant opens another CPU option but makes neither libraries nor domain state automatically safe.

### Bound Work, Not Just Workers

- Set a limit on workers, active operations, pending work, and retained results.
- Adapt the limit to memory, connections, service throughput, and the cost of each operation, not just core count.
- A semaphore bounds the active section, not the number of already created tasks waiting to enter it.
- For a large or open-ended stream, prefer a fixed number of consumers and a bounded queue to one task per element.
- A bounded queue transmits backpressure to producers instead of accumulating the entire backlog in memory.
- A limited pool can still receive too many submissions; maintain a window of in-flight work or submit in batches.
- Define a per-operation time limit and a global budget, as well as the policy when capacity is reached.
- Do not search for the thread or task limit until the machine is exhausted; even without its own OS stack, a task consumes memory.

### Understand Coroutines and the Loop

- Calling a coroutine function (`async def` without `yield`) produces a coroutine without executing its body; await or schedule it to execute it. An `async def` function containing `yield` produces an asynchronous generator, consumed notably with `async for`, not a coroutine to pass to `TaskGroup.create_task`.
- `await` can yield control to the loop when the operation needs to wait; it does not guarantee suspension at every occurrence.
- A computation loop without suspension monopolizes the loop's thread, even when written in `async def`.
- `[await c for c in coroutines]` awaits coroutines one after another; use concurrent supervision if overlap is intended.
- `asyncio.run` manages a loop at the application's synchronous boundary; do not nest it inside an already active loop.
- `time.sleep`, a blocking driver, or waiting on a synchronous Future freezes the loop's thread.
- Use `asyncio.sleep` to delay and `asyncio.to_thread` to offload a compatible blocking call; adding `await` before a blocking call does not transform it.
- This offloading removes neither the worker's wait, nor its data-access constraints, nor its side effects.

### Give Tasks an Owner

- Choose `TaskGroup` when an ordinary failure should stop the rest of the batch and the scope must await all its children.
- The group keeps their references, cancels remaining tasks on failure, and waits for their termination before exiting.
- For a task outside a group, keep a strong reference and someone responsible for its result and closure: the reference alone supervises nothing.
- A group that cancels does not reset effects already produced; arrange compensation or a transaction separately if the domain requires it.
- Keep Task objects to inspect successes retained after a partial failure; check their cancellation state before `result()` or `exception()`.

### Choose the Failure Contract

- Ordinary `gather` preserves argument order in its results, not completion order.
- When a child raises an ordinary exception, it propagates it without automatically canceling all siblings.
- Choose `gather(return_exceptions=True)` for all responses, failures included, and examine errors without confusing them with successful data.
- This option does not neutralize cancellation of `gather` itself; cancellation of the call and failure of a child are two distinct contracts.
- Ordinary failures from a `TaskGroup` arrive grouped; use `except*` to handle subgroups of relevant types.
- A simple `except ValueError` around the group does not handle its wrapped `ValueError` exceptions, even if only one task failed.
- Groups can be nested; `KeyboardInterrupt` and `SystemExit` have special handling distinct from ordinary exceptions.
- If siblings must continue in a group, transform expected failures inside each task according to an explicit contract.

### Time Limits, Cancellation, and Cleanup

- Python 3.11 provides `asyncio.timeout` for a scope and `wait_for` for an awaitable.
- Catch the `TimeoutError` produced by the scope as it exits, not as though it were raised directly in its body.
- These mechanisms request cooperative cancellation; a blocking CPU loop can delay the deadline, cancellation, and cleanup.
- `asyncio.CancelledError` derives from `BaseException`; an ordinary `Exception` catch lets it pass through.
- Prefer cleanup in `finally`; if cancellation is caught explicitly to clean up, re-raise it afterward.
- An expired time limit does not undo already committed external effects; define what the requester can resume without duplication.
- Canceling the await of `to_thread` does not reliably kill the function running in the thread.
- A running executor Future is not stopped merely by canceling its await.
- Arrange underlying I/O timeouts and a cooperative worker shutdown protocol when this duration must be bounded.
- Exiting an executor can wait for its still-active work; do not promise an immediate return after a timeout.
- The corpus describes `TaskGroup.cancel()` for 3.15: do not use it in 3.11, 3.13, or 3.14 code without a compatible alternative.

### Protect Invariants, Not an Isolated Statement

- A read-modify-write crossing an `await` can lose updates on a single thread.
- Protect the entire invariant with `asyncio.Lock`, or move state to a single owner fed by messages.
- A sequence without suspension is not interleaved with other tasks on that same loop; this property does not protect against other threads.
- An `asyncio.Lock` is not an interthread lock; worker code sharing state needs thread synchronization.
- The GIL protects the interpreter, not multi-operation domain invariants.
- The absence of a race in a counter trial does not prove portable atomicity; the observed scheduling may simply hide the defect.
- With threads, protect the check, read, modification, and publication of a single decision; prefer local data and a final merge when possible.
- A semaphore allows multiple accesses; it does not replace a lock if the invariant requires exclusivity.
- With a semaphore, prefer a managed scope to scattered `release` calls; `BoundedSemaphore` detects excess releases.
- Minimize time under the lock without moving a necessary part of the invariant outside protection.

### Carry Request Context

- Prefer a parameter for domain data; for a request identifier or cross-cutting tracing, use `ContextVar` rather than a global.
- A task normally receives a copy of the context when it is created; its assignments do not automatically propagate back to the parent.
- `asyncio.to_thread` propagates a copy of the context to its worker; do not infer identical propagation for every pool mechanism.
- `threading.local` isolates per thread, not per task: several tasks on a loop would share the same value.
- Restore the token in a `finally` in 3.11/3.13; the context-manager token described in the corpus requires 3.14 or later.
- Copying the context does not deeply clone its values; a contained mutable object can remain shared.

### Use Pools with Their Actual Boundaries

- `ThreadPoolExecutor`, `ProcessPoolExecutor`, and, when it exists, `InterpreterPoolExecutor` share the `Executor` interface.
- This common contract makes neither memory, imports, serialization, nor cancellation equivalent.
- `map` returns in input order; consume the results to make worker exceptions visible.
- For `submit`, retain and examine Futures to make their failures visible.
- A process pool requires importable module-level functions and serializable arguments and results.
- Do not assume a lambda, a local closure, a thread lock, or an open resource is transferable.
- Guard process creation and the main launch with `if __name__ == "__main__"` in an importable module.
- Do not depend on an OS's historical start method; the corpus emphasizes the default change in 3.14.
- Interactive environments may not provide the required importable main module; test the actual launch mode.
- Reuse workers and amortize transport and serialization with sufficient granularity; measure the balance between distribution and overhead on a bounded pool.
- The sequential fraction, copies, and reassembly limit the gain according to Amdahl's law.
- Measure a cold pool and a reused pool separately; a service and a short script do not pay the same costs.

### Distinguish Subinterpreters from Free-Threading

- The public `InterpreterPoolExecutor` pool described in the corpus appears in 3.14; it is not an interchangeable standard option in 3.11 or 3.13.
- Subinterpreters within one process keep isolated interpreter states and can each have their own GIL.
- The same process space does not mean unrestricted sharing of Python objects; arguments and results cross a transfer boundary.
- Check serialization, imports, and extension compatibility with this isolation; Python code can still have unsuitable global assumptions.
- The corpus describes the free-threaded build as experimental in 3.13, supported but still optional from 3.14 onward.
- Do not declare the GIL absent from every Python 3.14 or 3.15; distinguish version, build, and actual process state.
- Without the GIL, threads can parallelize Python, but contention and domain locks can cancel out the gain.
- Favor independent data and queues; an incompatible extension can re-enable the GIL, so check the stack actually loaded.
- The absence of the GIL removes neither OS stacks, thread-creation cost, nor the difficulty of safely canceling an active thread.

### Connect asyncio and Executors Without Blocking the Loop

- A `concurrent.futures.Future` from `submit` is not directly the awaitable Future of `asyncio`.
- Its `result()` can block; do not call it as a normal wait in the loop's thread.
- Use `loop.run_in_executor` as a bridge and await the asyncio Future it returns.
- `TaskGroup.create_task` expects a coroutine: wrap this bridge in a coroutine rather than passing it an arbitrary raw Future.
- Arrange the pool's lifetime so that its synchronous shutdown wait does not run in the loop's thread.
- Construct and close the pool around the asynchronous entry point, or provide shutdown that is explicitly nonblocking for the loop.
- An awaiting bridge unifies result arrival; it does not turn thread or process shutdown into coroutine cancellation.

### Choose a Queue and Arrange Its Shutdown

- `queue.Queue` coordinates threads; waiting on it blocks the calling thread.
- `multiprocessing.Queue` transfers serialized data between processes; do not assume shared identity there.
- `asyncio.Queue` suspends a task but is not safe to use directly from threads outside its loop.
- Use `get` or `await get` without continuous polling; define capacity, consumers, the end of producers, shutdown, and the fate of unprocessed elements.
- The Queue shutdown mechanisms described since 3.13 are absent in 3.11; provide sentinels or an explicit shutdown protocol there.
- `PriorityQueue` also compares subsequent fields when priorities are equal; provide a comparable tiebreaker.
- Reserve workers for consumers: having all workers occupied by producers blocked on a full queue would cause a deadlock.
- For large interprocess messages, drain the queue while producers can still write, before waiting for them to finish.
- Joining before reading can block producers on a full pipe and make waiting for completion impossible.

### Distribute or Duplicate a Stream Without a Race

- An arbitrary shared iterator has no general thread-safety guarantee; values can be duplicated without being lost.
- A generator resumed simultaneously can fail; protect `next` and other relevant resumption operations, not just the loop body.
- Under Python 3.15 as described in the corpus, `threading.serialize_iterator` protects an already created iterator.
- `threading.synchronized_iterator` applies to the function that makes generators, not to an already produced generator.
- `threading.concurrent_tee` addresses the case where each worker must receive the whole stream rather than a distinct share.
- Give each worker a clone; sharing that same clone between threads would require additional serialization.
- Check the presence of these 3.15 APIs before use; in 3.11/3.13/3.14, use a queue or explicit protection of resumption.
- Ordinary `itertools.tee` does not provide thread safety; lagging readers also imply data retention that must be bounded.
- Test the total count, uniqueness, and expected contents; counting only distinct values does not detect duplicate processing.

### Prevent Deadlocks and Livelocks

- Identify exclusive resources, resources held while waiting, and dependency cycles.
- Acquire shared locks in the same global order everywhere; break a condition of the cycle rather than relying on luck.
- A single asyncio thread can produce this cycle between suspended tasks; a timeout bounds the wait but does not fix acquisition order.
- A livelock works without making progress; also measure completed operations, not just CPU activity.
- Break symmetry with a priority or a yielding rule; endlessly repeating the same courtesy solves nothing.
- Do not take a test delay as proof that all schedules have been covered.

## Procedure

1. Measure the sequential version, identify the bottleneck, and set a gain target with a representative volume.
2. Choose the model compatible with Python, its extensions, and I/O constraints; document what is shared or transferred.
3. Define task ownership, errors, result order, capacity limits, time budget, and shutdown protocol.
4. Implement a simple unit of work; reduce shared state or protect its complete invariant.
5. Test success, partial failure, cancellation, timeout, and saturation on a finite workload, without requiring a network for basic verification.
6. Check that all submitted work is observed and that queues, tasks, and workers terminate according to the contract, including after an error.
7. Compare results, total time, and memory with the sequential version; remove concurrency if its cost exceeds its useful gain.

## Pitfalls

- A semaphore around millions of already created tasks does not bound the batch's memory.
- A timeout or coroutine cancellation does not reliably kill the thread performing the blocking call.
- `TaskGroup` supervises and cancels; it performs neither domain rollback nor a distributed transaction.
- A task-memory measurement is not directly a thread resident-memory measurement; a reserved stack is not entirely consumed.
- A correct result under the GIL does not establish the safety of a multi-operation sequence.
- Actors, barriers, CSP, transactional memory, and memory models exceed the tooling detailed here: do not invent APIs from their mere mention.

## Verification

- The expected gain corresponds to overlapping waits or actually parallelizable computation.
- Active operations, pending submissions, queues, and retained results have explicit bounds.
- Results match the sequential version and every worker failure becomes visible to the responsible owner.
- A task's shutdown is never presented as proof that its offloaded work has stopped.
- Tests cover cancellation and cleanup without infinite waits, with an external budget if the model cannot enforce shutdown.
- Shared invariants, context propagation, transferred identity, and iterator access are checked according to the backend.
- Versions 3.11, 3.13, 3.14, and 3.15 are not confused; the free-threaded build and its extensions remain explicit conditions.
- The assessment includes startup, serialization, coordination, and memory; core count is not presented as a guaranteed speedup factor.
