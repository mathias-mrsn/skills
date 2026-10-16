# Python — Thinking in Python

24 self-contained thematic skills that turn the philosophy of Bruce Eckel's *Thinking in Python* into directly actionable development rules.

## Principle

Each directory contains only a `SKILL.md`: philosophy, rules, decision criteria, procedure, pitfalls, and verification. No rule requires loading a chapter, document, or another skill. Each skill can be copied independently without losing its content.

The rules favor simple language mechanisms, abstractions justified by actual variation, explicit invariants, separation of effects, and observable checks. Advanced techniques remain conditional choices, not requirements.

## The 24 Skills

| Directory | Topic |
| --- | --- |
| `python-code-quality` | Readability, simplicity, coupling, and refactoring. |
| `python-collections` | Containers, data sharing, and comprehensions. |
| `python-control-flow` | Conditions, loops, and structural pattern matching. |
| `python-functions` | Signatures, scope, and callable behavior. |
| `python-modules` | Imports, namespaces, and packages. |
| `python-object-design` | Responsibilities, composition, inheritance, and polymorphism. |
| `python-type-checking` | Gradual typing, generics, and structural contracts. |
| `python-data-modeling` | Invariants, construction, and data representation. |
| `python-error-handling` | Exceptions, errors as values, and propagation. |
| `python-resource-management` | Acquisition, cleanup, and context managers. |
| `python-testing` | Tests, isolation, and levels of confidence. |
| `python-decorators` | Decoration, signatures, and wrapper composition. |
| `python-metaprogramming` | Descriptors, hooks, and class creation. |
| `python-performance` | Measurement, algorithms, caches, and memory. |
| `python-concurrency` | I/O, CPU work, tasks, threads, and processes. |
| `python-iterators-generators` | Laziness, consumption, and the generator protocol. |
| `python-functional-programming` | Purity, composition, and functional tools. |
| `python-object-creation` | Construction, factories, and uniqueness. |
| `python-interfaces-dispatch` | Adaptation, delegation, and operation selection. |
| `python-event-handling` | Subscriptions, notifications, and lifetimes. |
| `python-state-simulation` | Transitions, snapshots, and reproducible simulations. |
| `python-trees-interpreters` | Recursive structures and interpretation. |
| `python-effect-management` | Identifying, declaring, and handling effects. |
| `python-stateless-effects` | Effect composition with the Stateless library. |

## Validation

From the repository root, using Python 3.11 or later with no third-party libraries:

```sh
python3 -m unittest discover -s tests -v
```

Structural checks alone do not establish the semantic quality of the rules. Embedded examples and consistency with the sources are also reviewed during authoring.

## Attribution

Intellectual source: *Thinking in Python*, Bruce Eckel, working corpus at revision `a8feb860b4bdb4a7c90ab80d38eb743a5488ed3f`. The rules are operational syntheses written in English; the book's full text and diagrams are not bundled.

The source corpus states a CC BY-NC-ND 4.0 license. Its original notice is retained at the collection level for provenance, without assigning a new permissive license to the collection.
