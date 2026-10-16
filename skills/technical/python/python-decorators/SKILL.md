---
name: python-decorators
description: Decorate while preserving signatures, state, and binding.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Python Decorators

## When to Use

- Centralize a cross-cutting concern genuinely shared by several functions.
- Write or review a wrapper, a decorator factory, or a class decorator.
- Preserve a method's parameters, return value, metadata, and binding.
- Understand a decorator stack, its execution order, or its state sharing.
- Choose between `@` syntax, a configured callable object, and wrappers in the Decorator pattern.
- Do not add a layer when the behavior concerns only one function and remains clearer in its body.

## Philosophy

A decorator centralizes behavior that does not define the wrapped function's own work.
Its value depends on its observable contract: a transparent wrapper must preserve more than the function's name.
Make the configuration, decoration, and call phases explicit to avoid effects running at the wrong time.
Do not choose a class or pattern for its name; require a real structural or behavioral gain.

Original French synthesis of Bruce Eckel's Thinking in Python, corpus a8feb860; chapter Decorators.
The corpus targets Python 3.15+; keep the project's Python version and adapt only the necessary syntax.
For Python 3.11, use `typing.ParamSpec`, `TypeVar`, and traditional annotations; bracketed generic declarations require Python 3.12+.

## Rules

### What Decoration Does

- Read `@d` above a definition as assigning the result of `d(defined_object)` to the defined name.
- The decorator runs when Python executes the definition, often during import, not on every subsequent call.
- In a parameterized decorator, separate evaluation of its configuration from its application to the function.
- The returned wrapper, in turn, executes its body on calls; do not confuse its state with temporary decoration variables.
- A closure keeps the original function and its configuration accessible as long as the wrapper exists.
- Explicitly return the wrapper if the decorated name must remain callable; forgetting to do so binds that name to `None`.
- Do not assume the decorator calls the original: replacement, registration, or immediate computation are also possible.
- A decorated result may even cease to be callable; reserve this change of nature for a clearly documented intention.
- `@` syntax applies to a `def` or `class` definition, not to an assignment or a type alias declaration.
- Calling a decorator directly also allows wrapping a lambda, a bound method, a `partial`, or a compatible callable object.

### Dynamic Interface, Parameters, and Return Value

- Forward `*args` and `**kwargs` without reordering or transforming them if the contract promises transparency.
- Return the original function's result; a call whose result is not returned silently turns its result into `None`.
- Preserve exception propagation unless handling them is precisely the declared behavior.
- Do not promise work "after the call" on all paths with a mere statement following the call: use `finally` if necessary.
- Use `functools.wraps` on a function wrapper to preserve, among other things, its name, documentation, and annotations.
- `wraps` also sets `__wrapped__`, allowing introspection to find the original function.
- `inspect.signature` normally follows this chain; this result does not change the wrapper's actual `*args`/`**kwargs` parameters.
- Calling `__wrapped__` bypasses this layer; do not treat a decorator as an impenetrable security boundary.
- For an already-constructed wrapper object, use `functools.update_wrapper` rather than looking for an internal function to decorate.
- An arbitrary callable does not necessarily have `__name__`; do not implicitly require this detail in generic tracing.
- Choose either a contract restricted to functions or a fallback diagnostic name for other callable objects.

### Static Preservation

- Describe parameters with a `ParamSpec` and the return value with a distinct type parameter.
- Connect input and output through `Callable[P, R]` so that an interface-preserving decorator remains typed like the original.
- Use `P.args` and `P.kwargs` together on the wrapper's variadic parameters.
- Do not replace this relationship with `Any` or `Callable[..., R]` if the aim is to check arguments of decorated calls.
- `wraps` preserves metadata at runtime; it does not provide a precise static signature on its own.
- The return annotation `R` helps detect a forgotten result; keep this constraint in the wrapper's different branches.
- On Python 3.12+, the declaration form `def decorator[**P, R]` expresses these parameters; do not copy it into a 3.11 project.
- On Python 3.11, declare `P = ParamSpec("P")` and `R = TypeVar("R")` with the same type relationships.
- When the decorator really changes the interface, type the resulting interface instead of falsely claiming preservation.
- For a decorated class that is preserved, connect `type[T]` on input and output so as not to erase its concrete type.

### Coroutines and Deferred Execution

- Calling an `async def` function creates a coroutine without immediately executing its body.
- A synchronous wrapper tracing this call measures object creation, not the asynchronous work or its final value.
- To wrap this work, write an `async def` wrapper, await the call with `await`, then return the resulting value.
- Then relate parameters `P` and expected result `R` to the asynchronous form rather than declaring a synchronous return.
- Put error handling and cleanup around the actual await if they must cover execution of the body.
- The same distinction concerns generators: iterator creation and consumption are different phases.
- For a generator function wrapped with `ContextDecorator`, the corpus describes coverage of iteration starting in Python 3.15.
- Before 3.15, this tool wraps only creation; a `with` inside the generator avoids this version dependency.

### Arguments and Optional Parentheses

- A parameterized decorator is a configuration that returns the callable that subsequently receives the function.
- In function form, distinguish the outer factory, the intermediate applicator, and the call wrapper.
- Validate configuration as soon as it is created so that a bad option fails at the decoration line.
- Explicitly reject a repetition count below one if the contract promises at least one call and a final result.
- Do not silently correct an invalid option; that hides the usage error and makes the contract ambiguous.
- With a factory requiring arguments, `@factory` without parentheses passes the function as configuration and does not denote the same protocol.
- Add both `@d` and `@d(...)` forms only if they genuinely simplify common use.
- Reserve the first optional parameter for the function and make options keyword-only to distinguish the two calls.
- When the function is received immediately, return its wrapper; when it is absent, return the configured applicator.
- Detection using `callable` assumes that an option cannot occupy the same position with a callable value.
- An absence sentinel such as `None` and keyword-only options avoid mistaking a callable option for the function to decorate.
- Describe both forms with overloads: function to function, or configuration to decorator.
- Do not let an `Any` return from the implementation lose the overloads' precision at call sites.

### Stacking, Multiplicity, and Cost

- Decorators apply from bottom to top: the one closest to the definition wraps the original first.
- On a call, the outer layer starts before the inner layers; their subsequent processing then unwinds in reverse order.
- Mentally rewrite a stack as a composition before changing its order.
- Tracing around repetition observes one call encompassing several executions; the reverse order observes each execution separately.
- Test interactions when layers repeat, catch a failure, record state, or can skip the call.
- Repetition or retrying also reproduces side effects; do not present it as transparent merely because it preserves the signature.
- Apply metadata preservation at every layer to retain the introspection chain.
- `wraps` removes neither the wrapper's frame from the traceback nor the cost of the extra call.
- Avoid piling on decorators in a very hot loop without measuring the actual cost.

### Class Form, Lifetime, and Method Binding

- Without arguments, a decorator class receives the function in `__init__()`, and its instance can execute the wrapper in `__call__()`.
- With arguments, `__init__()` receives configuration; `__call__()` then receives the function and can return a wrapper function.
- Do not assume `__call__()` always means "business call": in the second form, it performs decoration.
- Choose a closure for simple private state and an instance when exposed attributes or separate phases clarify the whole.
- Determine whether state belongs to a call, a decorated function, a business object instance, or all decorated functions.
- A new decorator instance per function isolates these functions; a class attribute can instead make them share a counter.
- State created when a method is decorated may be shared by all business object instances, not automatically specific to each `self`.
- A function stored in a class is a descriptor: accessing it through an instance automatically supplies that instance as the first argument.
- An object with only `__call__()` does not provide this binding and can cause a misleading missing-argument error.
- For methods, return an ordinary function or provide a correctly designed `__get__()`; do not add this protocol unnecessarily.
- A parameterized decorator class that returns a function avoids this problem: the stored result is still a function descriptor.
- Test two distinct business object instances if state isolation or binding is part of the contract.

### Decorated Classes and the Decorator Pattern

- Distinguish "a class used as a decorator" from "a class receiving a decorator."
- A class decorator receives the already-constructed class; it can modify it, replace it, or return it unchanged after registration.
- For simple registration, return the same class to preserve identity and normal construction.
- A registry populated during decoration knows only the modules actually imported.
- Define a collision policy: two classes with the same name in different modules must not overwrite each other without a decision.
- Avoid `@lambda` to compute a constant: the appearance of a function definition then conceals a result of a different nature.
- Prefer an ordinarily computed constant, or a named and typed decorator if construction in a local scope truly justifies it.
- `property`, `staticmethod`, and `classmethod` produce objects with descriptor behavior; not all decorators return a function wrapper.
- The Decorator pattern wraps individual objects at runtime while retaining their interface; `@` syntax acts at definition time.
- Define this common interface, possibly with `Protocol`, so that each layer remains substitutable for the base object.
- Do not manufacture a subclass for every combination of features: compose independent behaviors.
- If the additions are only data to add or join, a list and a calculation are simpler than a chain of wrappers.
- Reserve wrappers for real conditional behaviors, transformations, or a need for each layer to be substitutable.
- Distinguish intentions: Decorator adds behavior, Proxy controls access, Adapter changes the interface, and Façade simplifies a set of components.

## Procedure

1. Name the cross-cutting behavior and the contract to preserve: parameters, return value, errors, effects, and synchronous or deferred mode.
2. Separate configuration, application, and call; decide at which phase each validation and effect must occur.
3. Choose function or class based on state and method binding, then express the types using syntax compatible with the project.
4. Preserve metadata and the result; put any cleanup guarantee around actual execution.
5. Check composition order, state sharing, and multiplicity of effects before adding another layer.
6. Execute representative calls, error branches, and introspection before considering the decorator transparent.

## Pitfalls

- A correct name after `wraps` guarantees neither a correct return nor a statically checked signature.
- An apparently async function may merely be a synchronous wrapper around a coroutine that has not yet executed.
- A decorator counter placed on a method can aggregate calls from all instances.
- A decorator class without `__get__()` can fail while blaming the wrong missing parameter.
- A changed stacking order can multiply traces or effects without changing visible signatures.

## Verification

- Test positional and keyword arguments, the exact result, and propagation of the expected exception.
- Verify the name, documentation, inspected signature, and consistent presence of `__wrapped__` across multiple layers.
- Verify both offered call forms and immediate rejection of invalid configurations.
- Check the number and order of executions and the stated independence or sharing of state.
- Call methods through instances, and await or consume deferred results to actually exercise the body.
- Run the type checker already designated by the project; do not confuse preserved metadata with a static guarantee.
