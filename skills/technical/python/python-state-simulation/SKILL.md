---
name: python-state-simulation
description: Model states, histories and simulations in Python.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# States, Histories and Simulations in Python

Original synthesis of Bruce Eckel's Thinking in Python, local corpus a8feb860.
The corpus targets Python 3.15 and later; `TaskGroup` requires Python 3.11+, `copy.replace` Python 3.13+.
The scope covers transitions, preservation of the past and model evolution; graphical interfaces remain separate.

## When to Use

- Replace scattered conditions with explicitly named states, events and transitions.
- Add snapshots, undo, redo or partial restoration without corrupting earlier states.
- Evolve a save format rather than discovering its incompatibility far from the loading boundary.
- Simulate agents and their local interactions, control time and randomness, verify emergent behavior.
- Do not create a state hierarchy for a simple decision without memory or variation in behavior.

## Philosophy

A state machine makes permitted paths and the handling of other inputs visible.
A history preserves past values, not new names for a mutable present.
A simulation is not its image: its rules, scheduling and limitations must be observable without a screen.
Use the smallest mechanism that shows these choices; a plausible trajectory does not replace invariant verification.

## Rules

### Choose the Machine's Representation

- Name states, events, carried data, conditions and actions before writing the engine; distinguish a state from the message that changes it.
- A Surrogate with an interchangeable implementation becomes a state machine when a rule automatically chooses the next implementation.
- Choose state objects when each carries behavior and few transitions; combine the entry action and successor selection in that object.
- Describe their contract through a `Protocol` containing the methods actually called; an empty base does not detect their omission.
- An ABC with abstract methods prevents incomplete construction; a base method raising `NotImplementedError` fails only when called.
- Share a state object between machines only if it carries no mutable state specific to a machine.
- A per-state table reduces repetitive branching; populate it after all states are created if transitions name them directly.
- Choose a global table if the machine comes from a diagram, if events carry values or if guards arbitrate transitions.
- `Enum` states prevent misspelled strings; data-carrying events can be separate dataclasses.
- Do not index by class a set of events represented by a single Enum expecting to distinguish its members: they all share the same class.
- Store functions or methods in the table; do not create condition and action hierarchies to replace first-class callables.

### Specify Transition Semantics Exactly

- Distinguish a state entry action from a transition action: factor an action common to all entries into the state or a shared helper.
- In an object-based engine, fix the order: request the successor, change the current state, then execute its entry action.
- Do not start overridable behavior in a still-incomplete constructor; separate initialization from startup if an action reads the machine.
- For unexpected input, choose remaining in the state or explicit failure; do not let a silent default decide in place of the domain.
- Remaining in the state may rerun the entry action if the engine calls it after every event; it is therefore not necessarily a no-op.
- In a global table, associate `(state, exact event class)` with an ordered list of `(condition, action, successor)`.
- Take the first satisfied guard; put the unconditional row last, otherwise it masks the others.
- Test simultaneously true guards: their order then decides which business explanation wins, not just which path is faster.
- Distinguish an absent row from all guards being false in diagnostics if the domain needs it; both can produce a dedicated impossible-transition exception.
- Prefer this dedicated exception to indiscriminately catching `RuntimeError`, which actions may also raise.
- A lookup by `type(event)` does not inherit a base's rows; explicitly test derived events.
- If the action executes before the new state is assigned, a failure preserves the old state name but does not undo the action's partial mutations.
- Do not promise transactions or rollback without implementing them; validate before effects when necessary.
- Build tables containing bound methods per instance; such a method retains the machine whose data it modifies.
- `Callable[..., ...]` allows varied signatures but does not check that the event type matches each callback in its row.
- Leave rendering to the caller: record results and messages rather than printing inside a reusable engine.
- When requirements become hierarchical or outgrow a small, readable engine, weigh a specialized library against the dependency cost; do not expand the homegrown framework indefinitely.

### Produce a True Snapshot

- Assignment shares an object; it does not capture a mutable value before modification.
- Copy at the level where mutation occurs: a list of immutable strings needs a shallow copy, while a list of lists still shares its inner elements.
- Use a deep copy or explicit structural conversion when nested mutable levels must be isolated.
- Measure the cost of repeated deep copies: they traverse the copied structure even if only one small part has changed.
- In a classic Memento, the owning object produces and restores the snapshot; the history caretaker stores it without interpreting its contents.
- A separate memento class avoids confusion with an arbitrary tuple; a type alias does not create a new runtime type and `NewType` does not make contents opaque at runtime.
- A frozen memento prevents accidental rebinding of its fields, not deliberate access to their contents; opacity remains a convention.
- Copy in both directions if the present remains mutable: restoration must not give the present a mutable list belonging to the snapshot.
- Do not treat a connection, a live widget or an entire external object as a restorable value without choosing the useful data and how to reconstruct it.

### Prefer Immutable Values Without Ignoring Their Cost

- If the model allows it, represent state as a frozen dataclass itself containing immutable values; a list in a frozen field remains mutable.
- Have each modification return a new state; retaining the old object then becomes a valid snapshot without an additional copy.
- Use `dataclasses.replace` to change selected dataclass fields while preserving the others.
- Sharing strings or immutable subvalues is safe; it does not mean the container gathering them is shared.
- Adding an element to a tuple constructs a new tuple of references; retaining all versions of a field that grows with every edit may consume quadratic memory.
- Bound history, group edits or choose a persistent data structure if this cost becomes significant.
- Command-based undo stores changes rather than states, but requires writing and testing an inverse for each action; choose it for a measured cost, not reflexively.
- Keep classic Memento if state is too costly to reconstruct at every keystroke or the mutable class belongs to an external component.

### Manage Past, Present and Future

- Separate the present state, the past stack and the future stack; move immutable states rather than editing them in those stacks.
- A new edit pushes the present and then clears the future: undone states can no longer be redone after branching.
- Undo first pops from the past and then stores the present in the future; redo performs the symmetrical operation.
- Define the boundaries: is availability exposed, an exception raised or a no-op performed when a stack is empty? The minimal mechanism may raise `IndexError` without changing history.
- Provide an operation that receives the edit itself and applies it to the present; this avoids computing a new state and then forgetting to record it.
- Retain an entry point accepting an already constructed state for snapshots produced otherwise; it must apply the same branching rules.
- Partial restoration combines past fields with present ones and produces a new state; recording it as an edit makes the restoration itself undoable.
- Do not make a generic caretaker read business fields to guess what undo must restore.
- `copy.replace`, available from Python 3.13, generalizes replacement to compatible types; for a dataclass on Python 3.11+, use `dataclasses.replace`.

### Load Saved Data at a Validated Boundary

- Distinguish an in-memory snapshot from a durable format: the latter must survive application evolution, not just the next mutation.
- Never load an untrusted pickle: its deserialization can execute code.
- A trusted pickle can still be incompatible: it records the module and class name, not a complete historical definition of the schema.
- Reconstruction may bypass `__init__`, `__post_init__` and a frozen class's assignment checks; successful loading proves no invariant.
- An added field may be absent and fail only on a later read; do not rely on its default being applied automatically.
- On a class with an instance dictionary, a removed field may survive as a ghost attribute ignored by the generated representation and equality.
- Renaming combines a residual old attribute with a missing new field; an equality test alone may miss this drift.
- Define a schema version and explicit migrations, then reconstruct and validate the current state at the loading boundary.
- JSON carries data without executing pickle code, but does not automatically validate the schema and notably turns tuples into lists.
- For durable storage needs, compare load-time validation and explicit schemas: msgspec, Pydantic and Protocol Buffers are options, not guarantees conferred on any raw document.
- Do not extrapolate ghost attributes from the non-slotted case to every class form; test the forms actually persisted.

### Design and Schedule Simulations

- Separate world representation, local rules, coordination and rendering; an agent receives only the operations it needs.
- A blackboard lets agents coordinate through shared state without calling each other; define the operations authoritative over that state.
- During exploration, testing and reserving a cell in the same operation prevents two agents from obtaining the same location.
- With cooperative `asyncio` on a single loop and thread, a synchronous sequence without suspension between testing and marking is not interleaved by other tasks.
- This guarantee disappears if an `await` is introduced between the two or other threads access the same state; do not present it as general Python atomicity.
- Let each agent yield control at an explicit boundary; async organizes trajectories here but does not accelerate computation compared with a synchronous worklist.
- For agents creating other agents, a `TaskGroup` also awaits tasks added while it is open.
- A `gather(*tasks)` covers only the list expanded at call time; it does not automatically await new agents added later.
- Compare the visited set with an independent exploration to verify coverage; count successful reservations separately to prove their uniqueness.
- Include a loop in the test world: an acyclic maze may never expose two concurrent reservations of a new cell.
- For a robot, delegate encounters to the room's occupant; walls, food, teleportation and the destination each define their local action.
- A boundary object returning the current room avoids a special case for a missing door; it remains distinct from a genuinely visitable room.
- Assemble rooms, their connections and then teleporters in separate passes; verify robot placement and pairs before allowing movement.
- Preserve room identity during search: two locations with equal contents are still two different vertices.
- Breadth-first search gives a minimum-length path in this graph of unit-cost moves; mark vertices when enqueuing them.
- Do not call a side-effecting interaction merely to inspect a destination: it could consume food or end the game during search.
- If the destination predictor reproduces movement rules, test their agreement when adding a new occupant; duplication does not magically disappear.
- A tour choosing the nearest food each time must recalculate after consumption and does not guarantee the shortest overall tour.

### Make Randomness, Time and Emergence Observable

- Supply a local `random.Random` instance initialized with a seed rather than implicitly sharing the global generator.
- Record parameters, seed, update order and number of steps to reproduce a run in the same environment.
- A seed alone does not promise the same trajectory after a change in algorithm, random-call order or scheduling.
- Separate model steps from display cadence: a graphical timer is not the physical definition of simulated time.
- Set the stopping condition, world size and movement limits; also validate degenerate cases before deriving a statistic.
- In a grain model, a local rule may read a field and adjust movement without knowing the other grains or the collective pattern.
- Distinguish the geometry imposed by the field from the observed concentration of agents on that geometry; only the latter is revealed by simulation.
- Test bounds and an aggregate measure rather than imposing an arbitrary final position on each agent.
- An improving metric does not prove the desired shape: extreme parameters can produce a good score while destroying the pattern.
- Single-bounce boundary reflection assumes sufficiently small steps; it does not handle an arbitrarily large displacement crossing the domain multiple times.
- Modify only one rule or parameter, then run the model to observe the effect; do not conclude about emergent behavior from reading alone.
- The plate model lets lines become finer as the step count increases; it does not represent the dynamic equilibrium of real sand. State this limitation instead of selling nonexistent physical fidelity.
- A view can drive or replay the model without a subscription system; model-view separation does not automatically mean Observer.

## Procedure

1. Describe states, events, invariants and expected effects; make impossible inputs and actions at each step visible.
2. Choose state objects or a table according to where transitions are most readable; test priorities and failures before rendering.
3. Define values to retain, their mutability and copy depth; prove that a current modification changes no past snapshot.
4. Implement history rules and boundaries, then test undo, redo, branching and partial restoration.
5. If states outlive the process, choose format, trust, version and migration; reject an invalid save at load time.
6. For a simulation, isolate the local rule, random source, logical clock, coordination and stopping; run a bounded scenario without a GUI.
7. Compare invariants and metrics with an independent oracle or an expected property; also observe behavior not summarized by the score.

## Pitfalls

- Remaining in a state may repeat an action; still being in the old state after a failure does not mean no data changed.
- A tuple of lists or a frozen dataclass containing a list is not enough to preserve the past.
- A history of immutable values does not necessarily have linear cost if every version reconstructs a growing container.
- Coverage of a visited set masks double reservations; a correct image may hide incorrect coordination.
- A fixed seed and low agitation prove neither statistical robustness nor the model's physical fidelity.

## Verification

- Cover every transition, simultaneously true guards, an absent input, a subtype and an action failure with its possible mutations.
- Verify entry and transition actions, the initial state, machine isolation and independence from rendering.
- Test a snapshot before mutation, nested mutation, restoration and then another mutation: no retained snapshot must change.
- Exercise empty history, an undo/redo round trip, a new edit after undo, the depth limit and undoable partial restoration.
- Load data from old schemas, including field addition, removal and renaming; verify invariant validation at the boundary.
- Run the model with a fixed seed; verify local reproducibility, bounds, stopping condition and aggregate properties without conflating them.
- Compare exploration with a coverage oracle, count reservations and test a cycle; also verify completion of all created agents.
- For a robot, verify walls, boundaries, consumption, teleporters, absence of mutation during search and actual arrival after executing the path.
- Report what is actually observed and the model's limitations, without turning a visual demonstration into a general proof.
