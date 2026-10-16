---
name: python-testing
description: Test contracts, effects, properties; no hidden randomness.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Testing and Confidence in Python

## When to Use

- Define behavior, reproduce a defect, or safeguard a refactoring.
- Design a suite isolated from the local machine, clock, randomness, and real services.
- Choose between examples, parametrization, fixtures, test doubles, and generated properties.
- Assess what a passing suite actually demonstrates and what remains an assumption.
- Do not turn still-undecided design exploration into a mandatory TDD exercise.

## Philosophy

A test states an expectation and makes a regression visible when it appears.
A useful suite protects contracts without unnecessarily freezing details that must remain changeable.
Testability depends mainly on boundaries: receiving a clock is more explicit than fetching one.
Purity reduces the number of possible histories to consider; it does not automatically prove correctness.

Original French synthesis of Bruce Eckel's Thinking in Python, corpus a8feb860; chapters Testing and Confidence.
Respect the project's Python version and its already-chosen tool versions.
The principles are usable on Python 3.11+; no Python 3.15 syntax is needed here.
`pytest`, Hypothesis, time-machine, and coverage tools are external to the standard library; do not install them implicitly.

## Rules

### Contract, Development Loop, and Regression

- Name the expected behavior rather than the detail of the line being executed.
- When the behavior is known, write a failing test, observe its cause, implement, then refactor with this safeguard.
- An import error can initially reveal a missing implementation; after creating it, check that the test actually reaches the intended behavior.
- Do not treat a test that fails because of an accidental syntax error as evidence of a reproduced regression.
- For a bug, first obtain a case that fails because of the bug and passes after the fix.
- After the fix, look for the gap that let it through: a forgotten input, an unstated invariant, or a misleading interface.
- Reserve TDD for behavior that is sufficiently understood; explore first when the design direction is still unknown.
- Run tests as changes are made to limit the number of modifications that could explain a breakage.
- Prefer black-box tests of the public interface; reserve internal inspection for mechanisms that justify it.
- A single underscore is a convention and a double underscore performs name mangling, not an access prohibition; respect the contract through discipline.

### Assertions and Exceptions

- In a `pytest` suite, use `test_*.py` files, `test_` functions, and readable direct assertions.
- Keep setup, action, and verification distinct without multiplying abstractions for a simple case.
- Check a business value or an observable effect; calling code without an assertion does not pin down its result.
- Use `pytest.raises` with the expected type; limit its block to the call that is supposed to fail.
- Add `match=` when the message distinguishes causes sharing the same type; its argument is a regular expression.
- After the block, check the invariants preserved by the failure, especially the absence of partial mutation.
- Do not place these assertions after the failing call inside the block: the exception would make them unreachable.
- For a failure represented by a value, explicitly compare that value with the expected result.
- A utility that absorbs or prints an exception without requiring it to occur does not replace an exception test.
- Compare floating-point results with `pytest.approx` and relative or absolute tolerances suited to the contract.
- The standard library provides `math.isclose`; its default tolerances are not those of `pytest.approx`.
- Do not widen a tolerance to hide a real error or wait for a rounding error before choosing a robust comparison.

### Parametrization and Targeted Runs

- Parametrize the same contract over several inputs instead of copying its test function.
- Clearly associate each input with its expected result and include boundaries, empty inputs, and rejection when the domain calls for them.
- Use `pytest.mark.parametrize` for variants specific to one test.
- Parametrize a fixture when the same variation must apply to all its consumers; anticipate the multiplication of cases.
- Reserve `skip` and `skipif` for intentional non-execution, such as an unsupported platform.
- Use `xfail` for a known defect whose test continues to run, not as a substitute for tracking it.
- In `terminal`, `python -m pytest -k pattern` targets a subject, `python -m pytest -x` stops at the first failure, and `python -m pytest --lf` reruns the last failures.
- After the targeted cycle, run the project's designated full-suite command in `terminal` before claiming there is no regression.
- Do not assume all collection modes modify `sys.path` in the same way; respect the project's organization and command.

### Fixtures and Shared State

- A fixture describes what a test needs; request it by its parameter name rather than calling it directly.
- By default, keep a fresh mutable instance per test to avoid order dependencies.
- Put shared fixtures in `conftest.py` for tests in its directory and descendants, without manual imports.
- Limit session fixtures to unmodified values or resources with reliable resetting.
- Justify a broader scope by the cost it saves, then check that it carries no residue from one test to the next.
- A generator fixture prepares before `yield` and cleans up after the test, including when the test fails.
- If setup can fail after acquisition but before `yield`, install local protection: teardown after `yield` will not be reached.
- Read teardown errors separately from assertion failures: a test can pass while still leaving a cleanup error.
- Use `autouse=True` for an essential common effect, not to make all test dependencies invisible.
- An autouse fixture does not inject its value into the function's global namespace; request its parameter to receive that value.
- Avoid indirectly testing state left by another test, even when both tests pass in their usual order.

### Files, Environment, and Temporal Dependencies

- Use a private temporary directory per test, notably `tmp_path`, rather than real data or a shared file.
- Redirect and restore environment variables with `monkeypatch` when the code reads them directly.
- Do not expect a late environment change to alter a constant already computed at import time.
- Read configuration at the usage boundary or supply it explicitly if it must be replaceable.
- Prefer an injected, controlled `random.Random` instance to reseeding the global generator.
- A seed makes the sequence reproducible; it does not let you arbitrarily choose its first value.
- Inject a clock function when doing so keeps dependencies near their boundary and signatures understandable.
- If injection requires disproportionate changes to intermediate calls, a targeted temporary replacement can be simpler.
- `monkeypatch` restores its changes during teardown, but a shared module attribute remains modified for the entire process during the test.
- Do not assume eventual restoration makes a global patch safe in the presence of concurrent code.
- `datetime.datetime` does not allow direct assignment to its methods; prefer an injected clock or a tool already approved by the project.
- If time-machine is already used, `tick=False` freezes wall-clock readings; do not infer that monotonic counters stop advancing.
- Do not use a real wait to prove a time difference that two controlled readings suffice to establish.

### Network, Stubs, and Mocks

- Keep the unit suite off the network; also replace any database or messaging boundaries it would cross.
- A stub supplies a chosen response; a mock also records interactions so they can be verified.
- Choose a stub if the result matters and a mock if the number, absence, or arguments of calls are part of the contract.
- Give the test double the protocol actually used, for example reading bytes and closing for a response managed with `with`.
- Replace the name looked up at the call site: after `from module import function`, patch the local name in the consuming module.
- After `import module`, account for the fact that its module object may be shared by other consumers.
- With `unittest.mock`, `assert_called_once_with` checks both call count and arguments; also test no-call branches if they are contractual.
- An unrestricted `Mock` accepts calls that the real dependency would reject; use `create_autospec` when its signature must be respected.
- Do not make the mock the main object of the evidence: verify the business code's behavior, not just the test double's.
- Distinguish isolated unit tests from any explicitly configured integration check; test doubles do not prove a real service's state.

### Properties, Generation, and Shrinking

- Formulate a law independent of the function body, then ask generation to look for a counterexample.
- A round trip checks recovery of the input; add known examples if two compatible transformations could share an error.
- An invariant checks each output; idempotence checks that a second application no longer changes the result.
- An oracle compares against a simple, independent implementation; do not copy the optimized algorithm into its oracle.
- In Hypothesis, describe the domain through strategies and state the law with `given` in a test function.
- Include relevant edge cases and unusual values, notably Unicode, rather than a comfortable but incomplete alphabet.
- Constrain inputs to the real domain without filtering out the very values likely to reveal a defect.
- Prefer pure functions and immutable values to repeat and shrink calls without depending on their history.
- For a stateful system, explicitly reset each attempt's context; do not declare it pure through a mere annotation.
- Examine the shrunk counterexample: it often explains the defect better than the complex input that first revealed it.
- Normally retain Hypothesis's example database, which replays known failures; do not copy its disabling from a demonstration.
- A homemade search must record the failing input and seed; a large number of trials over a narrow domain does not broaden that domain.

### Levels of Confidence and Limits

- Referential transparency permits reasoning by substitution; reading the clock or mutating an argument invalidates it.
- A cache on an impure computation can skip a necessary effect without raising an exception: compare effects too, not just return values.
- Purity makes evaluations independent of scheduling; it guarantees neither parallel speedup nor serialization compatibility between processes.
- Combine local reasoning, examples, typing, and properties according to risk rather than seeking a single correctness indicator.
- Typing checks the relationships expressed; `Any`, casts, and external data limit what those relationships guarantee.
- Generated properties are more expressive than many types but remain a finite search for counterexamples.
- A formal proof requires explicit assumptions and obligations; it does not appear because a function is pure.
- Imperative code can also be proved; functional discipline mainly reduces the cost of reasoning.
- If coverage is available, interpret unexercised lines as a lead; an executed line is not necessarily verified.

## Procedure

1. State the contract, valid domain, errors, and effects that a call can produce.
2. Inventory hidden dependencies, then choose injection or replacement at the smallest boundary.
3. Build independent cases and a failing regression test for each defect fixed.
4. Implement the behavior, verify the final state, then extend to boundaries and error paths.
5. Add an independent property if it covers a family of cases that examples do not describe sufficiently.
6. Run targeted tests, then the project suite; report results and limits without turning an absence of failures into proof.

## Pitfalls

- A mutable session fixture can make the suite pass only in its usual order.
- An exception of the right type but arising during setup can satisfy an overly broad `raises` block.
- An overly permissive mock can hide a signature that has become incompatible.
- A thousand ASCII trials do not verify Unicode behavior; a copied oracle is not an independent check.
- Difficulty isolating a test can reveal a hidden dependency to fix, not a need for more mocks.

## Verification

- Each important test has a reached assertion about useful behavior and fails for the right cause when the defect is reintroduced.
- No unit case requires the network, personal files, real time, or the random generator's global state.
- Fixtures and patches are cleaned up even on failure, and no test depends on another test having run first.
- Expected exceptions, invariants after rejection, and absent interactions are verified as thoroughly as happy paths.
- Properties cover their stated domain and provide an actionable counterexample on failure.
- The report distinguishes tests run, skipped tests, teardown errors, static guarantees, and assumptions still unverified.
