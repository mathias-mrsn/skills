---
name: python-collections
description: Choose and transform Python collections.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Python Collections, Sharing and Comprehensions

## When to Use

- Choose a container based on dominant operations, expected order and mutation possibilities.
- Copy, share, merge, sort or unpack data without losing elements or intent.
- Replace a construction loop with a comprehension, or break down an expression that has become opaque.
- Decide between materialization and lazy processing when consumption, memory or resource lifetime matters.
- This scope does not turn an ordinary container into a storage, concurrency or business-validation system.

## Philosophy

Choose the shape of the data first according to what the program does with it most often.
A comprehension defines a collection; a loop expresses actions; a generator defers work until consumption.
A shorter construct is better only if its shape, evaluation order and object sharing remain readable.
Operational synthesis of Thinking in Python, by Bruce Eckel; corpus a8feb860.
Respect the project's target Python; do not impose recent features from the corpus on older environments.

## Rules

### Choose the Container and Its Contract

- Use a list for an ordered sequence that needs to grow, be traversed or be modified by position.
- Use a tuple for a fixed-length record whose positions have meaning, or for a sequence that must no longer change.
- Use a dictionary to associate a key with a value and a set for uniqueness and membership lookups.
- Do not choose a specialized collection without a specific operation or measurement to justify it; built-in containers cover the general case.
- A list can contain multiple types, but if each position plays a different role, prefer a record or separate collections.
- Name fields when indices no longer make the record understandable; `namedtuple` retains indexing and unpacking.
- Use `typing.NamedTuple` if a named tuple's fields need types; a dataclass suits a record whose fields need to change.
- Distinguish sequence order, dictionary insertion order and a set's lack of guaranteed order.
- Freeze data when it no longer needs to evolve, provided that the mutability of its contents is also checked.

### Manipulate Lists Without Surprises

- Indices start at zero, and negative indices count from the end; express a position near the end this way instead of recalculating the length.
- Read a slice as `start:stop:step`, with `stop` excluded; a list slice produces a new list.
- Choose `append()` to add an object and `extend()` to add an iterable's elements; passing a list to `append()` creates a nested element.
- Use `insert()` for insertion by position, `remove()` for the first equal value and `del` to delete by index.
- Use `sorted(iterable)` to obtain a new sorted list; use `list.sort()` to reorder the existing list.
- Never reassign a list to the result of `sort()`: this method returns `None`.
- Express the criterion with `key=` and the direction with `reverse=`; raw string sorting distinguishes code points, and thus uppercase from lowercase.
- Reserve lists for operations they can perform efficiently; repeated insertions and deletions at the front move the other elements.
- Do not delete elements while traversing that same list: shifting positions can cause neighbors to be skipped without an error.
- Build the filtered result separately, traverse a copy or collect deletions before applying them, according to the desired sharing.

### Copying, Aliases and Immutability

- An assignment passes a reference, not a copy; determine whether the recipient should share the object or own a distinct container.
- Repeating a list repeats its references; do not build independent mutable rows by multiplying a single sublist.
- Build a new sublist on each iteration to obtain independent rows; a comprehension suits this repeated creation.
- A shallow copy isolates the outer structure, not nested objects; test an internal mutation before claiming independence.
- If the contract requires copying internal objects too, consider `copy.deepcopy()` rather than an additional slice of the outer container.
- A tuple forbids replacing its positions but can contain a mutable list; do not present it as deeply immutable.
- Use `frozenset` for a set that must no longer change and that can serve as a key or element if its contents are hashable.
- Hashability requires a stable hash, not merely an object described as immutable; a tuple containing a list remains unhashable.
- `MappingProxyType` prevents writes through the view but reflects mutations of the original dictionary: it is not an independent snapshot.
- To share without a defensive copy, check immutability all the way to the leaves; a frozen container of mutable elements is not enough.
- The corpus presents `frozendict` for its recent target: check its actual presence in the runtime before adopting it, without assuming availability in Python 3.11.
- Do not automatically add a package of the same name to reproduce this presentation; distinguish an owning frozen mapping from a read-only view.
- A frozen mapping does not magically make its values hashable or turn shallow immutability into deep immutability.

### Tuples and Unpacking

- The comma forms the tuple; write a trailing comma for a singleton, and `()` for the empty tuple.
- Unpack multiple return values into names rather than repeating positional access when the shape is known.
- Without a starred target, the number of targets must equal the number of elements; a mismatch raises `ValueError`.
- Use at most one starred target per unpacking level; it collects the remaining elements into a list, even if the source is a tuple or string.
- Place this target at the beginning, middle or end according to the values to name; nest targets to reflect nested data.
- `_` is only a conventional name in an assignment; use it to signal an ignored value without attributing special semantics to it.
- Distinguish `*rest` on the left, which collects, from `*source` in a list or tuple construction, which unpacks an iterable.
- A collection display can unpack multiple iterables and mix them with ordinary elements; unlike `+` on lists, they do not all have to be lists.

### Dictionaries: Access, Merging and Collisions

- Use only hashable keys: built-in mutable lists, dictionaries and sets are unsuitable as keys.
- Choose `d[key]` when absence must be an error; choose `d.get(key, default)` when a fallback value is part of the contract.
- A `key in d` test and direct iteration concern keys, not values or pairs.
- To traverse pairs, write `d.items()`; directly unpacking a two-character key can succeed while producing the wrong result.
- Use `keys()`, `values()` and `items()` as needed; key views support set operations, as do item views if the values are hashable.
- Use the dictionary's guaranteed insertion order without confusing it with sorted order.
- With `a | b` or `{**a, **b}`, the rightmost values win for shared keys; make this priority intentional.
- Distinguish merging that creates a dictionary from `|=` or `update()`, which modify the existing one and are therefore visible through its aliases.
- Build a dictionary from pairs when the source already provides this shape; check duplicates and the length contract of `zip`.
- Use `pop()` to remove and retrieve a value; use `del` when only deletion is wanted.
- Do not add or remove keys while traversing the dictionary; build another dictionary or apply the changes after traversal.
- Inversion by comprehension requires hashable, unique values if it must preserve all associations; otherwise later occurrences overwrite earlier ones.

### Sets and Specialized Containers

- Write `set()` for the empty set: `{}` builds a dictionary.
- Set elements must be hashable; duplicates collapse, which is a data transformation, not a mere optimization.
- Use `&`, `|`, `-` and `^` for intersection, union, difference and symmetric difference; check the direction of subtraction.
- Use `<=` and `>=` for inclusion, `<` and `>` for strict inclusion; these operators do not express a total order on sets.
- Prefer set methods when inputs are non-set iterables or when multiple operands are useful; `isdisjoint()` tests for the absence of shared elements.
- Use `add()` to add; choose `remove()` if absence must raise `KeyError`, or `discard()` if absence is acceptable.
- Augmented forms modify the set; do not change its size while traversing it.
- For repeated lookups, compare a list's linear scan with a set's generally constant-time hash lookup; measure at the actual size without promising absolute speed.
- Use `Counter` to count occurrences; reading a missing key yields zero without inserting that key.
- Use `most_common()` for the highest frequencies; operations between counters represent multiset operations, not ordinary unions of keys.
- Use `defaultdict(factory)` to create and store a value on the first missing indexed access; provide a callable such as `list`, not an already constructed list.
- Reading `d[missing]` from a `defaultdict` therefore modifies the dictionary; use `in` or `get()` to observe without triggering the factory.
- `setdefault(key, [])` may suit a local need, but its argument is constructed on every call; `defaultdict` states the creation policy once.
- Use `deque` for a single-threaded queue with additions and removals at the ends; accessing its middle does not have the cost of list indexing.
- `deque(maxlen=n)` automatically evicts from the opposite end when an addition exceeds capacity; do not use it if losing an element is forbidden.
- For a queue shared between threads, choose `queue.Queue`; for priorities, consider `heapq` rather than inferring these contracts from a simple deque.

### Comprehensions: Result, Order and Scope

- Use a comprehension when its collection is the useful result; do not create an unused list of return values from `print()` or other effects.
- Choose a loop for actions, complex control or steps that need to be understood and checked separately.
- Choose delimiters according to the result: brackets for a list, braces for a set, `key: value` pairs within braces for a dictionary.
- A conditional expression before `for` chooses the value produced; an `if` after `for` chooses whether an element is produced.
- In a comprehension with multiple `for` clauses, retain the order of the equivalent nested loops: each source must be bound before use.
- Two `for` clauses in a single comprehension flatten; a comprehension in the output expression builds subcollections.
- Check variables already present in the outer scope: a reversed clause can use an old name and produce the wrong result without a `NameError`.
- Separate selection, flattening, sorting and rendering if their combination requires several readings or an explanatory comment; name each step's result.
- Prefer a direct comprehension to `set(temporary_list)` or `dict(temporary_list)` when no intermediate list is useful.
- Prefer a comprehension to nested lambdas in `map` and `filter`; these functions remain relevant with an already available named callable.
- Do not assume that a `filter` with a lambda narrows types for the checker; an explicit test in the comprehension is often clearer and better understood.
- `filter(None, values)` eliminates all false values, not just `None`; explicitly preserve zero and empty values if they are valid.
- A comprehension's iteration variable does not replace the outer name; conversely, an ordinary `for` leaves its variable in the enclosing scope.
- In a class body, a comprehension does not see other class attributes as local variables; only the outer iterable source is evaluated in that body.
- A walrus in a comprehension binds its name in the enclosing scope; use it mainly to avoid repeated computation, not to hide accumulation.
- Test `is not None` after an optional computation when zero is a valid result; do not filter on its truth value alone.
- Do not reassign the iteration variable with a walrus, place a walrus in the source after `in`, or use one in a class-body comprehension: these forms are forbidden.
- With `zip`, use `strict=True` if lengths must match; otherwise traversal stops at the shortest source.
- For a file search by name, prefer a suitable glob to a comprehension over a manual traversal; choose detailed traversal if structure or other criteria are needed.
- Starred unpacking in comprehension output presented for recent Python is conditional on the target parser; keep double `for` clauses on incompatible versions.
- Such unpacking flattens only one level; merging mappings retains the priority of later keys, not all associations.

### Generators: Consumption and Lifetime

- Lists, sets and dictionaries built by comprehension are constructed immediately; a generator expression produces an iterator consumed on demand.
- Parentheses do not form a tuple comprehension; use `tuple(iterable)` if the result must be a tuple.
- Passing a generator to `sum`, `any`, `all`, `min` or `max` can avoid an intermediate collection; `any` and `all` may stop before exhaustion.
- Building a `set` or `dict` from a generator still consumes all its values; this does not create a lazy set or dictionary.
- Do not present a generator passed to `str.join()` as a guarantee of memory savings: the implementation may materialize its inputs.
- A generator does not replay: a second consumer sees only the remaining values, possibly none, without an error signaling exhaustion.
- If multiple traversals are needed, materialize the source or create a new generator; do not compare computations performed on two different consumption states.
- The outermost iterable source is evaluated at creation; transformations, filters and free variables are consulted afterward as consumption proceeds.
- Do not defer traversal of files or another resource beyond its lifetime; materialize the required values inside the block that guarantees that lifetime.
- Closures created during traversal also read their variables later; do not assume the comprehension froze their values.
- A generator expression alone as an argument does not require its own parentheses; add them as soon as another argument accompanies the call.

## Procedure

1. Establish order, uniqueness, access, sharing and lifetime requirements; choose the minimal container that satisfies them.
2. Define absence, collision and mutation policies; identify shared nested elements.
3. Write the transformation in readable steps; replace it with a comprehension only if the result remains understandable in one reading.
4. Choose when computation occurs and the number of traversals; check that resources and free values remain valid at consumption time.
5. Run cases with empty inputs, duplicates, missing keys, different lengths and a nested mutation; compare with explicit expectations.
6. If a performance gain motivates the change, measure at a representative size and retain the same result guarantees.

## Pitfalls

- An outer copy or frozen container can retain mutable sharing that is invisible in a simple display.
- Inverting or merging a dictionary can lose associations without an exception; check collisions before promising preservation.
- A `defaultdict` observed by indexing may change during diagnosis; a bounded window can lose elements during normal operation.
- An immediately created collection can be correct where the equivalent generator waits for a resource that has already disappeared.
- Compactness is not a sufficient goal: do not combine filtering, sorting, formatting and effects in an opaque expression.

## Verification

- The chosen container matches the dominant operations and stated order; no test depends on a set's order.
- Absence, duplicate and collision rules are explicit and tested; eliminated data is eliminated intentionally.
- Mutation of a nested element confirms the promised sharing or independence; rows meant to be distinct really are distinct.
- Every comprehension produces a used result, and its clauses respect the expected evaluation order.
- Multiple consumers, partial consumption and the end of resource lifetimes have been exercised if a generator is involved.
- All syntax and containers used exist on the supported Python versions; no package is added to mimic an assumed API.
