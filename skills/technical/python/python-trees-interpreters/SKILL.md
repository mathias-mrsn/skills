---
name: python-trees-interpreters
description: Design and interpret Python trees.
version: 0.1.0
author: 'mathias-mrsn, Hermes Agent'
platforms: [linux, macos, windows]
---

# Python Trees, Composites, and Interpreters

Original operational synthesis of Bruce Eckel's ideas, Thinking in Python, local corpus a8feb860. The source corpus is attributed to Bruce Eckel and carries CC BY-NC-ND 4.0; no new license is granted here.

## When to Use

- Represent a leaf, a group, and an entire tree with the same processing contract.
- Build an expression language, add evaluations, or produce rewritten trees.
- Preserve the distinction between literal text and interpolated values until they reach the consumer.
- Do not impose a tree if a sequence suffices; do not close a node family that plugins must be able to extend freely.

## Philosophy

- Composite organizes recursive data; Interpreter gives it meaning through traversal. The same structure can support multiple interpretations.
- Choose the extension axis: methods make adding node types easier; external functions make adding operations on a closed family easier.
- Defer rendering or execution decisions: retain a usable structure rather than an already flattened result that has lost its provenance.
- An annotation describes a contract; it does not automatically validate objects received at runtime.

## Rules

### Recursive Model and Extension

- Define each variant by its fields and express the closed family as an explicit union. A group contains elements of this union, not just groups.
- A common base can carry shared operators without replacing the union as the input type for traversals: a base is extensible; a union enumerates the cases to cover.
- For a closed structure, separate data from aggregation, search, rendering, evaluation, and rewriting functions; add an operation without modifying existing nodes.
- For nodes supplied by plugins, prefer a polymorphic contract: a central `match` would otherwise require editing the host program for each new type.
- In a traversal typed over a union, end the cases with `case _` and `typing.assert_never` on the subject. A compatible checker flags an added but unhandled variant; at runtime, an unexpected case triggers an assertion, not automatic support.
- Frozen records containing tuples allow subtree sharing if their other fields are also immutable. A frozen field containing a list does not prevent `append`.
- The corpus uses a helper decorator, `record`: it is not a standard Python API. Without this helper, explicitly choose a project representation, for example `dataclasses.dataclass(frozen=True, slots=True)` with children in tuples.
- For Python 3.11, write recursive unions using deferred annotation forms compatible with that version. The declaration `type Name = ...` requires Python 3.12+; do not transplant the deferred annotation resolution of the corpus targeting Python 3.15+ without adaptation.

### Traversal and Aggregation

- Each leaf provides its contribution; each group recursively combines those of its children. The same call must accept an isolated leaf, a subtree, or the root.
- For an empty directory, define the identity element: a zero sum, an empty stream of paths. Do not treat emptiness as an error by default.
- A traversal generator combined with `yield from` provides a lazy stream, flat for the consumer, without exposing the structure of recursive calls.
- Define whether a search includes matching groups and whether it continues into their children after a match.
- When a new node represents a link, specify its policy: whether to follow the target, what to count, and which repetitions to avoid. Do not silently assign it ordinary-file semantics.
- `pathlib.Path` identifies a location; it does not contain the children. The actual composite belongs to the filesystem, and reads query the operating system.
- `Path.stat().st_size` on a directory is not the sum of descendant files. A total-size calculation must select the files, traverse them, and then sum their sizes, accounting for possible errors and changes in the real system.

### Building a Language with Operators

- Give each grammar construct its own variant: constants, variables, and operators with their children. Meaning must remain in the interpreters.
- The `__add__` and `__mul__` methods can construct nodes instead of calculating; `__radd__` and `__rmul__` cover a scalar on the left when the native operand declines the operation.
- Explicitly promote accepted scalars to constant nodes. Return `NotImplemented` for an unsupported type, including in reflected methods; an annotation alone would allow invalid trees to be constructed.
- Here Python supplies the parser and its precedence only for expressions written in Python source in which each operator encounters at least one node. Two ordinary integers are calculated before any tree construction.
- A language received as user text requires a real parser and a defined grammar; operator overloading does not replace them.
- A narrow annotation for `self` accepted by one checker may be rejected by another. Do not copy a signature specific to `ty` as though it were portable; keep the union contract explicit and check conversions.
- Choose between structural equality and expression-building `==`. Equality generated by a dataclass masks an inherited method; use `eq=False` if the project wants to construct a node with `==`, giving up that automatic structural equality.
- `and`, `or`, and `not` cannot be overloaded as tree operators. If the language uses `&` and `|`, document their meaning and parenthesize comparisons, because their precedence differs from that of Boolean operators.

### Multiple Interpretations and Environment

- Evaluate a tree by destructuring: a constant returns its value, a variable consults the environment, and an operation combines the children's values.
- Keep the environment explicit to reevaluate the same tree under multiple bindings without modifying it. Choose and test the missing-variable policy; direct dictionary access raises `KeyError`.
- An `**env` parameter is convenient but rebuilds a dictionary at each recursive call. A shared explicit mapping avoids this cost on deep trees.
- If the evaluator's first parameter coexists with variables passed as keywords, make it positional-only with `/` to avoid a name collision.
- Add rendering or differentiation as a new traversal. Fully parenthesized rendering preserves the structure; minimal rendering requires an explicit precedence and associativity policy.
- For a Python AST rather than a project-specific language, `ast.parse` provides the nodes and `ast.NodeVisitor` a visitor mechanism; do not confuse this API with the variants of your own model.

### Bottom-Up Rewriting and Sharing

- Simplify the children before choosing the parent's rule. A multiplication simplified to zero can then trigger the elimination of an addition at its parent.
- Distinguish patterns from construction: `Num(0)` after `case` tests a shape without calling the constructor; the same notation in an expression constructs an object.
- Alternatives separated by `|` must bind exactly the same names; a mismatch is a syntax error, not a problem to catch during traversal.
- Apply explicit rules: identity elements, absorption by zero, and constant folding. Specify their numeric domain and error semantics before adding other operators.
- An algebraic identity is not automatically an equivalence of all observations: removing a subtree can remove a missing variable or an error. Define whether you preserve a mathematical value on valid inputs or also evaluation failures.
- Return a new tree without mutating the input. Return the existing node when its children remain the same objects; share unchanged subtrees without copying them.
- Use `is` for this sharing test. Structural equality may retraverse descendants at every level and unnecessarily increase the cost.
- A recursive traversal consumes one frame per level: a generated chain of several thousand nodes can produce `RecursionError`. Use an explicit stack for these inputs rather than promising unlimited depth.

### Templates and Interpolation Provenance

- T-strings and `string.templatelib.Template` / `Interpolation` require Python 3.14+; this mechanism is not available in Python 3.11. Do not confuse it with `string.Template`.
- A t-string retains literals and interpolation objects; an f-string immediately produces a string and erases this separation. A t-string does not apply any security policy on the consumer's behalf.
- Iterating a `Template` provides a single level of `str | Interpolation`. Read `Interpolation.value` for the value and `Interpolation.expression` for the retained expression text.
- An interpolation can contain another `Template`: recurse into this value if the consumer accepts composition. Concatenating templates, by contrast, produces a flat sequence.
- Iteration skips empty literals; `template.strings` retains their positions. Choose this latter API when the exact alternation matters.
- To produce a parameterized query, add literals to the SQL text and each ordinary value to a parameter list; emit a placeholder in its place and pass text and values separately to the driver.
- Choose the placeholder style expected by the driver; `?` is not universal. Do not inject a value back into SQL text on the grounds that it comes from a template.
- A nested template is syntax composition: allow this route only for fragments whose provenance is controlled. User data must remain parameters, not become grammar fragments.
- For an HTML consumer, process interpolations according to the output context; simply using a t-string performs neither escaping nor validation.

## Procedure

1. Enumerate variants and axes of change; decide between a closed family and plugin extension. Criterion: the chosen mechanism supports the extension actually expected.
2. Specify fields, children, immutability, and domain errors. Criterion: an isolated leaf, an empty group, and a shared subtree have a written meaning.
3. Separate construction from interpretation; write one traversal per desired result. Criterion: adding rendering does not modify the data.
4. Build rewrites from the bottom up and retain sharing. Criterion: rules triggered by simplified children are covered.
5. For templates, specify allowed types, recursion, and the destination of values. Criterion: no user value enters the syntax through implicit conversion.
6. Check versions and the depth of real inputs. Criterion: ordinary paths and limits are tested with the project's runtime and checker.

## Pitfalls

- Confusing a tree constructor with immediate computation or an arbitrary-text parser.
- Replacing the closed union with an open base and losing missing-case checking.
- Believing that a frozen object makes all its descendants immutable or that an annotation checks runtime types.
- Reusing mathematical identities without specifying the errors and effects the rewrite can remove.
- Flattening an interpolation too early and then trying to recover the text's provenance afterward.
- Increasing the recursion limit without measuring stack consumption and without considering an iterative traversal.

## Verification

- Test an isolated leaf, an empty group, a subtree, and a complete tree with the same operation; check path order and contents.
- Temporarily add a variant to the union: the checker must identify every incomplete traversal, with no catch-all that hides the omission.
- Compare manual construction with construction through operators; test left-hand scalars, wrong types, and precedence.
- Evaluate the same tree under several environments, including a missing variable and a variable sharing the first parameter's name.
- Check constant folding, nested rules, stability of a normal form, and identity of retained parts; compare evaluations over the domain where equivalence is promised.
- Test a deep chain; if an iterative traversal is required, compare its results with the recursive traversal on small trees.
- With compatible Python, test adjacent interpolations without a literal, a nested template, and a value resembling an injection; check produced text and parameters separately.
