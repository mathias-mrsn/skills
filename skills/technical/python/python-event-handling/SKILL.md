---
name: python-event-handling
description: Design subscriptions and notifications in Python.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Subscriptions and Notifications in Python

Original synthesis of Bruce Eckel's Thinking in Python, local corpus a8feb860.
The corpus targets Python 3.15 and later; the concurrency mechanisms noted here are available as of Python 3.11.
This skill covers the publication contract, subscriber lifetime and the effects of a notification, not the internal evolution of a state machine.

## When to Use

- Make several functions, services or views react to a change without naming them in the model.
- Decide when to connect, disconnect, filter or batch notifications.
- Fix subscribers being skipped, retained in memory, called recursively or abandoned after a failure.
- Choose between synchronous broadcasting and asynchronous fan-out according to responders' actual expectations.
- Do not use broadcasting when the need is to select a single handler and retrieve its response.

## Philosophy

Observer decouples what changes from what reacts; it requires neither an observer interface nor a class per reaction.
A broadcaster holds callables and defines what it sends them.
Decoupling and dynamic subscriptions are two different choices: pay the costs of the latter only if subscribers really come and go.
Notification is an observable contract: who is called, with what, when, and what happens to the others after a failure?

## Rules

### Define the Channel and Its Contract

- Represent a simple reaction with a function, a bound method or a callable object; require a class only if it holds useful state.
- Give the synchronous callback a signature such as `Callable[[T], None]` when broadcasting expects no business response.
- Do not rely on an ignored result to influence the broadcaster; a policy of returning errors requires a different contract and explicit collection.
- The model knows its subscribers as callables, not as specific views; a new view connects without changing the model.
- With push, send the relevant value; the responder works directly from the message.
- With pull, send the model and let each responder read the necessary data; this choice couples the responder to the model's interface.
- Match the types to pull: a callback requiring a specific model does not automatically satisfy a contract accepting a generic subject.
- Choose automatic notification after a change or an explicit notification after several modifications; the latter batches changes but can be forgotten.
- Update the model before notifying so that reads triggered by notification see the new value.
- Initialize without announcing a partially constructed object; populate its storage directly before making notifications possible.

### Choose When Subscriptions Are Established

- If responders are known at construction, receive them in a tuple retained without rebinding; this preserves decoupling without a disconnection API.
- This fixed form does not need a snapshot for every notification; it nevertheless retains the risks of exceptions and reentrancy.
- If views open and close, provide runtime connection and disconnection rather than freezing their set.
- Registration during import provides a registry initialized at load time, but retains shared state and import side effects; it is not per-instance injection.
- Direct calls to reactions named in the model are not decoupling: they fix the dependencies in its code.
- For several categories of change on one object, prefer multiple channels held through composition to an artificial broadcaster hierarchy.
- If inheritance provides the broadcaster, initialize its list through its constructor; a dataclass's generated constructor does not automatically call an ordinary base's constructor.
- Do not replace a small, clear constructor with a dataclass requiring more repair in `__post_init__`.

### Stabilize Recipient Selection

- Iterate over a copy of the subscriber list during a synchronous notification; modifying the list being traversed may silently skip the next subscriber.
- The snapshot fixes recipients at the start: a disconnection in progress does not necessarily remove an already selected call.
- A new connection during that notification waits for the next one; test this boundary rather than promising immediate removal.
- Preserve connection order if storage is a list; do not convert to a set without changing the stated contract.
- Decide whether duplicates are allowed: in the minimal mechanism, two connections produce two calls and a disconnection removes only one.
- Decide the absent case: `list.remove` propagates `ValueError` when no subscription matches; do not advertise an idempotent API if it is not one.
- Keep a reference to a lambda if it must be disconnected; writing the same lambda again creates another object.
- Separately obtained bound methods may be equal without being identical; disconnection by equality finds the same instance-function pair.
- The subscription snapshot is neither a lock between threads nor a copy of the payload.

### Control Lifetimes

- A callback list contains strong references; a bound method retains the instance it comes from.
- When the broadcaster lives longer, disconnect the responder when its owner departs to avoid obsolete subscribers remaining alive.
- Do not add weak references as a matter of principle: a broadcaster with the same lifetime already releases its subscribers when it disappears.
- For a weakly held bound method, use `weakref.WeakMethod`, not a plain `weakref.ref(obj.method)` to the temporary method object.
- Resolve the reference at call time, keep the live method locally for that call and remove the subscription if the target has disappeared.
- Do not simultaneously capture the instance strongly in the weak wrapper; that would defeat the intent of the weak reference.
- The wrapper can disconnect during notification if the loop uses the snapshot; test its disappearance without depending on a graphical view.

### Define Reentrancy and Synchronous Errors

- A responder that writes to the model may re-enter the setter and then trigger notification before the initial notification finishes.
- Use an equality guard if messages represent changes: writing the same value again becomes a no-op.
- Do not use this guard if every reading counts: two equal values may represent two distinct observations.
- A reentrancy flag can block nested writes while allowing a new identical notification after the previous one.
- Define what happens to different writes during a notification; ignoring reentry is not a queue and may lose an update.
- Reset a flag in `finally`, including when a responder fails, otherwise subsequent notifications may remain blocked.
- An equality guard breaks an identical echo, not every cycle in which responders successively transform values.
- In a simple loop, an exception propagates immediately and subsequent responders are not called; the already modified model is not automatically restored.
- Explicitly choose fail-fast or collect-and-continue; this choice belongs to the broadcasting contract, not to a randomly added `except`.
- If all must be called, collect ordinary exceptions, continue and then expose them to the caller; Python 3.11+ supports an `ExceptionGroup`.
- Do not absorb control-flow interruptions by indiscriminately catching `BaseException`.
- If responders return success or error as a value, adapt those returning `None` and actually process the collected results.

### Evaluate General Attribute Interception

- Reserve `__setattr__` for objects that genuinely intend to publish multiple assignments with a name and a value.
- Create the internal list without re-entering this hook, then store through `object.__setattr__` or the base hook; recursive assignment inside the hook does not terminate.
- An annotation without a value does not create the list; create a separate list per instance rather than a shared mutable class list.
- Internal writes, counters and caches are published too unless explicitly excluded; do not expose these details accidentally.
- This mechanism broadens messages to `object` values and often forces responders to filter by name.
- A `__setattr__` accepting any name may also let a typo pass static checking; dedicated properties retain a more precise contract.

### Broadcast Asynchronously Without Abandoning Responders

- Stay synchronous for fast in-memory reactions; async is useful when responders wait for I/O.
- The async contract is a callable returning an `Awaitable[None]`; an ordinary synchronous function and an unawaited coroutine are not interchangeable.
- Expose an awaitable method for mutation and notification; assigning to a property cannot await its async setter.
- Construct the set of awaitables before yielding control; expanding calls to `async def` functions fixes the coroutines before they execute.
- This property explains the implicit snapshot of this specific fan-out; if a callable produces an awaitable while synchronously changing subscriptions, copy subscribers first.
- Concurrent task effects do not necessarily follow connection order; `gather` results remain in argument order.
- Without errors, `gather` awaits all tasks; with its ordinary setting, the first failure may propagate while other responders continue.
- Do not confuse failure propagation with batch completion; those remaining tasks are no longer awaited by the notification that just failed.
- If every responder must finish, use `gather(..., return_exceptions=True)`, examine the outcomes and then report failures after awaiting.
- Distinguish cancellation from ordinary errors during this collection; do not blindly put every outcome into an `ExceptionGroup` of ordinary exceptions.
- `TaskGroup`, available since Python 3.11, cancels the other tasks after one task fails; this is a different contract, unsuitable when complete delivery is required.

### Put Decisions in the Right Component

- The publisher decides which change it publishes; each responder can only filter what has reached it.
- A global threshold chosen for display loses small changes from the log; put the presentation threshold in the display responder.
- Specify the threshold's baseline: comparing to the last reading and comparing to the last displayed value do not produce the same filtering.
- If every subscriber repeats a category filter, split lists by event type rather than asking everyone to sort the same channel.
- A table indexed by `type(event)` selects exact types: it does not automatically deliver derived events to subscribers of a base.
- Use a `.get` read for an event without a handler to avoid creating an empty entry in a default registry.
- A bus broadcasts to all selected handlers, unlike a chain that stops at the first success; also keep its mutation and error policy explicit.
- Handlers marked by a decorator may name their event in an annotation; this registration adds runtime checks and is not a universal static guarantee.
- Prefer explicit type-handler subscription until eliminating this repetition justifies the extra registry machinery.
- Keep business rules independent of the screen; a view translates input and a rendering callback displays published state.
- Document-View may combine input and rendering; MVC separates them so the controller can change without modifying the model or view.
- Refresh a view initially without waiting for a future notification and release replaced graphical resources instead of accumulating them.

## Procedure

1. Define the published value, notification time, recipients and meaning of repeated readings; establish a testable contract.
2. Choose fixed or dynamic subscribers, push or pull, a single channel or categories; eliminate mechanisms without a real need.
3. Define order, duplicates, absent removal and the effect of subscription mutation during notification.
4. Identify callback owners and their lifetimes; provide disconnection or a weak reference where necessary.
5. Set reentrancy and failure policy before writing the notification loop; test their effect on other responders.
6. If async is necessary, guarantee that all tasks the contract promises to complete are awaited and make every failure observable.
7. Exercise the model with recording lists, then connect views without moving business decisions into rendering.

## Pitfalls

- A subscriber snapshot prevents index skips, not reentrant loops or payload modifications.
- A lambda whose reference is not kept remains connected without a convenient way to find that exact subscription again.
- An equality guard may suppress legitimate measurements; an incorrectly reset flag may suppress all future measurements.
- Simply switching to async changes the order of effects and what happens to tasks after a failure.
- A broadcast returning without error does not prove that an initial view has already been drawn.

## Verification

- Test zero, one and several subscribers, their order, a late connection, a duplicate and an absent removal.
- During a notification, remove one subscriber and add another; verify the recipients of that notification and the next.
- Make the first responder fail and verify exactly which others still receive the message, according to the chosen policy.
- Exercise a reentrant echo, a second identical measurement and a notification after an exception; no guard must remain stuck.
- Test the end of a subscription owner's lifetime and, if used, the weak reference without retaining its target in the test.
- With async, verify slow responders, collected failures and cancellation; no promised task remains unsupervised.
- Verify the model and its notifications without a GUI, then confirm that multiple views see the same change.
