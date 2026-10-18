# Terraform Local Values

## Decide Whether a Local Is Necessary

- Inline a simple expression used once. Do not introduce a local solely to rename a literal, variable, or resource attribute at its only call site.
- Count code references, not the number of instances eventually created. One `for_each` argument remains one expression location.
- A single-use local is justified when it names substantial logic: a transformation for `for_each`, nested comprehensions, filtering, flattening, or a nontrivial conditional.
- A simple map supplied to `for_each` is not automatically complex. Do not use the presence of `for_each` alone to justify indirection.
- For expressions used in multiple locations, introduce a local when it expresses one shared meaning or avoids meaningful duplication.
- Do not merge coincidentally equal values with different meanings or create chains of aliases to manufacture reuse.
- Use locals for internal constants and derived values, not as another caller-configurable interface.
- Names should express intent; use [naming](naming.md) for semantic suffixes, units, tags, and collection keys.

## Placement

- If multiple files consume the local, declare it in `locals.tf`.
- If all consumers are in one implementation file, put its `locals` block at the top of that file before resource/module declarations. This includes justified single-use complex locals.
- Do not put every local in `locals.tf` because there are many or because one calculation is complex. Cross-file consumption is the criterion.
- Dedicated declaration files such as `variables.tf`, `outputs.tf`, `versions.tf`, `providers.tf`, and `backend.tf` must retain their responsibilities.
- When an output-only expression needs substantial supporting logic, keep it inline if readable or place that logic in a cohesive implementation file; do not turn `outputs.tf` into a mixed implementation file.
- A necessary local used only by lookups in `data.tf` may sit at its top.
- Local values are module-scoped regardless of placement; file proximity communicates intent, not private scope or execution order.
- Reassess placement when consumers change: move a local to `locals.tf` when another file begins using it, and back to its implementation file when cross-file reuse disappears.

## Examples

These examples illustrate placement and decisions, not complete deployable
configurations.

- Use `var.retention_days` directly for one retention argument; do not create `local.retention_days = var.retention_days`.
- A `common_tags` merge consumed in both `network.tf` and `workers.tf` belongs in `locals.tf`; document which keys win.
- A filtered `enabled_workers_by_name` map consumed once by a resource's `for_each` can be a justified local at the top of `workers.tf`.
- A total computed by one simple multiplication in an output stays inline; a descriptive output name already explains it.

Example at the top of `workers.tf`, assuming `var.workers` is a map of objects
with a non-null boolean `enabled` field:

```hcl
locals {
  enabled_workers_by_name = {
    for name, worker in var.workers : name => worker
    if worker.enabled
  }
}
```

The resource consumes `local.enabled_workers_by_name` as its `for_each`.
Keep keys stable and known at plan time. Do not use sensitive values as keys.

## Verification

- Trace every local to its actual reference locations and files.
- Inline trivial single-use aliases and retain names that clarify substantial logic.
- Confirm `locals.tf` contains genuinely cross-file values, not all calculations.
- Test transformed collections with empty, enabled/disabled, and relevant null cases.
- Review key changes and resulting resource addresses; a refactor of a transformation can change identity even when the resource block itself stays unchanged.
