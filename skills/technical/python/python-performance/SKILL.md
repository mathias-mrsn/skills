---
name: python-performance
description: Measure and reduce time and memory costs.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Python Performance and Memory

## When to Use

- A realistic workload exceeds a duration, throughput, or memory target.
- Choose an algorithm, a container, a compact representation, or a lazy pipeline.
- Decide whether a computation cache, slots, or value sharing delivers a real gain.
- Compare interpreters, vectorization, compilation, and parallelism after locating the cost.
- Reduce a large number of equivalent objects with a Flyweight without losing their identity contract.
- Do not use it to justify a rewrite solely on the grounds that Python is supposedly slow.

## Philosophy

Python's first performance benefit is the development speed made possible by clear code.
Keep that simplicity until a realistic measurement proves it insufficient.
Look for where the cost lies rather than optimizing familiar parts or ones that are easy to rewrite.
The best result is fast enough and compact enough, with the lowest cost in understanding and dependencies.
An optimization is established only after checking the result and measuring the entire workload again.

Original synthesis based on Bruce Eckel, Thinking in Python, corpus a8feb860.
Attribution does not imply any new license for the source text.

## Rules

### Establish the Problem Before the Solution

- Set an observable target and measure the straightforward version first.
- Use the volume expected in production; a few elements reveal neither quadratic growth nor memory saturation.
- Distinguish CPU time from waiting time: speeding up a loop does not eliminate a database wait.
- Count copies, allocations, hidden queries, and repetitions that an abstraction makes hard to see.
- Keep a correct reference version to compare each transformation on the same inputs.

### Choose the Instrument for the Question

- `cProfile` locates costs by function and counts calls; its instrumentation can disturb what it measures.
- `tottime` excludes called functions; `cumtime` includes their cost; `ncalls` helps distinguish an expensive call from excessive repetition.
- Do not stop at the module or entry function topping cumulative time: they often encompass the entire application.
- A sampler estimates where time is spent from stack snapshots; it does not give the exact number of calls.
- The corpus describes `profiling.sampling` for Python 3.15; check its presence and support before use.
- Do not require this module in a 3.11 or 3.13 project; `cProfile` remains a measurement path independent of this addition.
- For a targeted question about reaching code or counting, `sys.monitoring` allows selective instrumentation on versions that provide it, not on 3.11.
- With this mechanism, attach events to the relevant code rather than the entire process when the scope is local.
- Reserve an unused identifier, disable events, and release the identifier during cleanup; tools share this resource.
- A local event does not automatically monitor functions called by the targeted code.
- If the only question is whether a location is reached, disabling its event after the first observation avoids paying for subsequent ones.
- A third-party tool such as Scalene becomes relevant if distinguishing Python time, native time, and allocations justifies the dependency.

### Compare Honestly with `timeit`

- Use `timeit` for already localized variants, not as a substitute for profiling the entire application.
- Choose the iteration count explicitly so that a first trial stays bounded.
- The `timeit` result is the total duration of the repetitions, not the duration of one call.
- Repeat and keep the minimum to estimate the least disturbed local cost, as the corpus suggests.
- This minimum is neither production latency, nor a percentile, nor a guarantee under load.
- Compare the same data, results, and effects; distinguish excluded setup from setup actually paid for.
- Include index construction or array conversion when those costs are part of actual use.
- `timeit` normally disables garbage collection; re-enable it in setup if allocations and collections are part of the cost being studied.
- Distinguish cold start, initial compilation, and steady state; do not hide a cost paid on every launch.
- Avoid conclusions based on a small difference buried in machine noise.
- Keep local measurements, their environment, and the scenario; no speedup factor from the corpus is a portable promise.

### Progress from the Least Costly Change to the Heaviest

- Start with a compatible newer CPython, native idioms, and a suitable algorithm.
- Compare the cost of a platform or hardware change with the lasting cost of a rewrite.
- PyPy can help some workloads, but check language and dependencies rather than extrapolating an advertised average.
- The corpus distinguishes the internal tail-call interpreter available since 3.14 from the experimental JIT introduced in 3.13.
- These tail calls concern the interpreter's C implementation, not a recursion optimization for Python functions.
- A version number does not reveal all build options; do not assume these mechanisms are active in every distribution.
- For the JIT, separate availability in the binary, process enablement, and actual code warm-up.
- If the `sys._jit` probes are available, they report these states but must not become a branch in domain computation.
- Compare enabled and disabled operation on a sufficiently long workload, without changing the rest of the experiment.
- The 3.15 developments and future goals described in the corpus are contextual; do not infer a universal gain or default enablement.
- A JIT or a faster machine does not change a poor algorithm's complexity.

### Improve Operations and Growth

- Prefer clear native operations: `sum`, `join`, comprehensions, `itertools`, and `collections` before a reinvented loop.
- Do not retain an obscure comprehension for a small gain; readability remains the main reason.
- Moving an attribute access into a local variable is a micro-optimization that can slow down recent CPython; measure.
- A list suits traversal and small collections; a set or dictionary suits many key lookups.
- Hash lookups have a favorable average cost, without guaranteeing absolute constant time for every key.
- Account for the cost of hashing, equality, index construction, and index updates.
- A `deque` suits additions and removals at both ends, rather than a list used as a queue.
- Choose immutability for invariants and sharing, not as an automatic speedup of the same container.
- Shallow immutability alone does not ensure the hashability of all contained fields.

### Choose Between Sorted Search and a Heap

- `bisect` requires data that remains sorted; its logarithmic search does not make insertion into a list logarithmic.
- `bisect_left` gives the position before equal values; then check bounds and equality to conclude that a value is present.
- `bisect_right`, also named `bisect`, gives the position after equal values; choose according to the duplicate rule.
- A heap serves to extract extremes progressively, especially when insertions and extractions are interleaved.
- `heapify` builds in linear time; the root exposes the minimum, without guaranteeing that the rest of the list is sorted.
- Use `heapq` operations to preserve the invariant; an ordinary `pop(0)` destroys it.
- Try `nsmallest` or `nlargest` for a limited selection before rebuilding the algorithm by hand.
- Compare with a full sort using the actual order in which data is produced; sorting benefits from already ordered sequences.
- The public max-heap variants described in the corpus require Python 3.14 or later, not 3.11 or 3.13.
- A heap shared between threads requires protection; `queue.PriorityQueue` provides dedicated coordination.

### Reduce Materialized Work

- A generator pipeline produces on demand and can avoid the entire suffix that is never consumed.
- It saves intermediate lists, not an accumulation that the consumer would eventually build itself.
- The cost is deferred until consumption; timing creation alone would give a misleading comparison.
- A generator is exhaustible and does not replace a collection for multiple traversals, sorting, or random access.
- Captured sources and resources can remain alive longer; arrange for their closure.
- Measure memory peaks separately with `tracemalloc` so that one variant does not inherit the other's allocations.
- Distinguish current allocation from peak; `tracemalloc` measures neither all native memory nor the entire process.
- Anticipate the RAM limit: swapping or allocation failure can abruptly break a previously acceptable trend.

### Memoize a Computation Without Changing Its Meaning

- `functools.cache` suits a pure computation repeated on the same hashable arguments.
- A function that reads the time, a changing file, or mutable state does not meet that contract without an explicit invalidation policy.
- Memoizing a side effect also prevents its re-execution; it is not simply an equivalent speedup.
- Check that the retained result can be shared; a mutable result changed by a caller contaminates subsequent calls.
- `cache` strongly retains arguments and results; `lru_cache(maxsize=...)` limits the number of entries, not directly their size in bytes.
- Examine hits and misses, key cardinality, value sizes, and recomputation cost before choosing the size.
- A memoized method also retains `self` and can extend the lifetime of every instance used.
- For a value computed per instance, `cached_property` can fit if an instance dictionary exists and the value remains valid.
- A cache's internal coherence does not guarantee that a function missed by several threads executes only once.

### Reduce Storage per Instance and per Number

- For many records, compare `dataclass(slots=True)` with an attribute dictionary per instance.
- `frozen=True` prohibits assignments but does not by itself remove that dictionary; freezing and slots are two independent choices.
- Combine both for frozen values when their constraints suit the model.
- Any custom decorator must actually delegate this generation; a static marker does not replace the generated methods.
- Slots limit dynamic attributes and can break code expecting `__dict__`.
- `cached_property` requires that dictionary; reintroducing it also restores part of the cost that was meant to be removed.
- An unslotted base or a subclass without an appropriate declaration can give instances a dictionary again.
- Two nonempty slot layouts in multiple inheritance can conflict; test the actual hierarchy.
- Weak references require `__weakref__`, or `weakref_slot=True` with a compatible slotted dataclass; this option exists in 3.11.
- `sys.getsizeof` counts only the object itself; do not compare one instance alone with its competitor's entire graph.
- With sharing, naively adding up all referenced objects counts the same allocation multiple times.
- `array` compacts homogeneous numbers; its type and range replace the generality of Python objects.
- This memory gain does not guarantee a faster Python loop over the array; measure computation too.
- `memoryview` shares a buffer instead of copying it; a later conversion to `bytes` copies the data again.
- An allowed write through the view changes the original buffer; a view of an immutable buffer remains read-only.
- Views, including their slices, extend the buffer's lifetime and can prevent resizing it; release all of them before resizing.

### Choose Vectorization or Compilation at a Profitable Boundary

- NumPy removes Python loops for whole-array operations on compact arrays; keep data in this format to benefit.
- Include conversion, temporary allocations, and changes in numerical precision in the assessment.
- Numba suits numerical loops that are hard to vectorize; it does not arbitrarily compile every Python object.
- Separate the first, compiling call from subsequent calls, while reporting the cold cost if it matters to the application.
- NumPy can provide the array and Numba its irregular loop; these are complementary roles, not a universal ranking.
- The corpus notes that its Numba examples are not run for its 3.15 target; do not present this compatibility as established.
- Rust with PyO3 and maturin allows moving an identified hot function, at the cost of a build toolchain and another language.
- Favor a substantial operation per boundary crossing; millions of small calls can consume the entire gain.
- Compare conversions and work per transferred value; object count alone is not a sufficient criterion.
- Preserve results, errors, numerical bounds, and the observable interface; compiled code is not necessarily faster than Numba.
- Choose concurrency for independent waits, or parallelism for divisible computation, only after measuring and bounding the work.

### Flyweight: Share Values, Not Just Avoid a Computation

- A candidate combines many uses, few distinct values, and a genuinely immutable core.
- Separate shared intrinsic state from extrinsic state specific to each use; position, owner, or counter stays in the context.
- The core's fields must themselves be safe to share; freezing a field containing a list does not freeze that list.
- All relevant constructions must go through the sharing mechanism; the direct constructor can bypass a factory.
- Test with `is` or the number of live identities: a set of equal values proves no sharing.
- Do not import this rule into ordinary code: CPython's small integers and interned constants do not justify `is` for comparing values.
- A recomputation cache can forget an entry and then rebuild an equal result without changing the computation.
- An identity pool cannot evict an object that is still alive and then promise that a request will always return that same object.
- `lru_cache` is therefore not a Flyweight pool guaranteeing uniqueness among live users.

### Choose and Secure the Pool

- A closed set known in the code: consider `Enum`, which constructs its members once and provides lookups by name or value.
- An attribute added to an Enum member is not automatically deeply immutable; keep values stable by design.
- A limited set constructed on demand: a `@cache` factory is the shortest mechanism, unless concurrent uniqueness is required.
- Required `Class(...)` syntax: intern in `__new__`, accepting explicit pool management.
- Python can run `__init__` again when `__new__` returns an existing instance; do not unintentionally repeat effects and factories there.
- Include the class in the key if subclasses must not share the same base object.
- A growing set: `WeakValueDictionary` preserves identity while users keep the object alive, then allows its collection.
- This weak contract provides no identity guarantee after all strong references disappear; collection timing depends on the implementation.
- Slotted values in a weak pool must accept weak references; keys must also be included in the retention assessment.
- Constructor syntax and a weak pool address two independent needs and can be combined.
- A lazy check-then-insert can create two objects in two threads, even with `@cache`.
- Prepopulate the pool or protect lookup, complete construction, and publication with appropriate synchronization.
- Never publish an object in the pool if another thread could observe its still-missing fields.
- Also count per-use references and pool structures: the gain concerns duplicated values, not the whole map or collection.

## Procedure

1. Set a threshold and realistic scenario; keep a correct reference result and an initial measurement.
2. Profile and classify the bottleneck: computation, waiting, allocation, copying, or retention; choose the corresponding instrument.
3. Formulate one gain hypothesis and its cost; choose the least heavy change that can test it.
4. Compare outputs and failures before comparing times; test several data sizes and shapes.
5. Measure duration and memory again, distinguishing setup, cold, warm, and full workload.
6. For a cache or pool, check keys, eviction, lifetime, mutation, and concurrent creation according to the intended contract.
7. Keep the change only if the useful gain exceeds noise and complexity cost; stop as soon as the need is met.

## Pitfalls

- A microbenchmark excluding construction and conversion can identify the wrong choice for the application.
- Slots, immutability, caching, and Flyweight solve different problems; none replaces the others.
- An evictable factory can remain correct as a cache while violating an identity promise.
- An experimental-build figure or a measurement from the book is not a portable threshold to turn into a test assertion.
- The 3.14/3.15 options and compiled dependencies require explicit compatibility, not an implicit upgrade.

## Verification

- The target, volume, environment, and observed bottleneck are named.
- The optimized version preserves required values, errors, and effects on edge cases.
- Repeated measurements include the costs actually paid and distinguish a local minimum from real latency.
- The memory assessment handles the peak, retained objects, and sharing without misleading double counting.
- Every cache has a validity policy and a bound or a justification for retention.
- Every Flyweight fulfills its identity, freezing, and lifetime contract, including under concurrency if it is allowed.
- Every recent API or optional dependency remains conditional on the target; no speed factor is promised without measurement.
