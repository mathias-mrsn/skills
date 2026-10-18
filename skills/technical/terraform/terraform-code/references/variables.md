# Terraform Input Variables

## Decide What to Expose

- Root inputs represent values that differ between environments or are expected to change frequently; the latter is uncommon. A value being technically configurable is not enough.
- Require one of those two concrete reasons before adding an input and record which applies. Hypothetical future flexibility is not sufficient.
- Availability zones, retention days, and concurrency limits are candidates only when actual supported deployments differ or require frequent changes.
- If a value must change independently of infrastructure deployments, put it in an appropriate configuration service rather than forcing Terraform runs for application configuration changes.
- Do not mirror every provider argument, expose implementation invariants, or introduce arbitrary option bags. Split responsibilities when flags select unrelated architectures.
- Keep constants and values derived entirely from other inputs or resource attributes in direct expressions or justified locals. Do not expose redundant derived values unless independent override is a real requirement.
- Reference managed resources directly instead of copying their attributes into variables.

## Source of Truth and Composition

- For cross-stack values, prefer a published contract in Parameter Store, Secrets Manager, or AppConfig according to whether the value is a shared parameter, a secret, or dynamic application configuration.
- Define producer ownership, stable lookup paths, environment/account/region scope, permissions, and deployment ordering. Publication does not eliminate dependencies or automatically redeploy consumers.
- Resolve published infrastructure values at the root through supported data sources or deployment integrations. Let applications retrieve runtime configuration when it must change independently.
- Variable files contain minimal deployment decisions, not inventories of resource IDs, copied service-managed values, or all application configuration.
- Pass narrowly scoped dependency attributes from roots to children. A child may need `subnet_id` even when the root obtains it from a resource or published parameter, not a root deployment variable.
- Root variable files do not populate child arguments automatically. A child interface is not a reason to copy its dependencies into root variable files.
- Keep the child interface focused on genuine caller decisions and dependency contracts, not every internal literal.

## Declarations and Types

- Declare every variable in `variables.tf`, never another file. Follow [naming](naming.md) for semantic names, suffixes, and units.
- Declare an explicit type. Reserve `any` for genuinely opaque pass-through values that the implementation does not inspect, not avoidance of interface design.
- Use `object` for records with known fields and `map` for caller-defined keys with one value type. Group fields by a cohesive concept, not merely to reduce declaration count.
- Use `list` when order or duplicates matter, `set` for unordered unique membership, and `map` for stable caller-defined identities. Never promise ordering for a set.
- Terraform type constraints allow compatible conversions, and object conversion can discard extra attributes. They are not strict schemas rejecting every unknown or misspelled key.
- Optional object attributes need defined omission semantics. Stable `optional(type, default)` requires Terraform 1.3 or later; omitting a non-null default can leave null values.

## Defaults and Null

- Omit `default` when a caller must decide. Do not invent production accounts, network IDs, or locations to avoid required inputs.
- Add a default only when safe and meaningful across supported use cases. Explain operational tradeoffs instead of calling a contextual default universally safe.
- Defaults must be literal values; derive values involving variables, resources, or functions outside the declaration.
- Use `nullable = false` when top-level null is unsupported. With a non-null default, explicit null selects that default; without a default, null is invalid.
- With default `nullable = true`, explicit null can override a non-null default. Distinguish omission, null, empty strings, and empty collections.
- Top-level non-nullability does not prevent null collection elements or nested attributes. Validate or normalize them separately.
- Do not use undocumented empty-string sentinels for discovery, disabled behavior, or missing identifiers. Prefer a documented nullable value or a cohesive object.

## Descriptions and Validation

- Give every input a nonempty English description beginning with its purpose and the behavior or resources controlled, not a repetition such as "The name" or "The tags".
- Explain units, allowed values, identifier scope, optional fields, null/omission behavior, ordering, keys, and merge precedence where relevant.
- Explain significant replacement, deletion, downtime, or default consequences only when verified against the actual implementation/provider. Keep documentation consistent rather than mechanically repeating defaults.
- Use heredocs for multi-line contracts; never include real credentials or private infrastructure IDs in examples.
- Validate module-specific invariants beyond the type: permitted modes, numeric ranges, whole-number counts, or nonempty identifiers.
- Error messages must identify the input/field and the accepted value/unit. Prefer "retention_days must be a whole number from 1 through 365" to "Invalid value".
- Distinguish provider requirements from deliberate module policy; do not copy constraints from an unrelated service.
- Make validations safe for every type-accepted value, including supported nulls and null elements. Use conditionals to guard null-rejecting operations; `&&` and `||` are not safe short-circuit guards.
- Use `can` for fallible operations such as regex matching; do not conceal malformed required input with broad `try` fallbacks.
- Cross-object variable validation requires Terraform 1.9 or later. On older supported targets, use a suitable blocking resource/output precondition or redesign the input; preconditions require 1.2 or later.
- A failed `check` block reports a warning rather than blocking an operation, so it is not a substitute for input validation.

## Sensitivity and Compatibility

- Mark confidential inputs `sensitive = true`. Redaction is not encryption and does not prevent persistence in state or saved plans.
- Never put credentials in defaults, committed variable files, examples, or command-line arguments. Prefer provider credential mechanisms or approved secret delivery and protect state/plan access.
- Reading from a secret service or injecting a value through an environment variable does not by itself keep it out of state.
- Ephemeral variables require Terraform 1.10 or later and supported ephemeral contexts. They avoid persistence, but cannot replace ordinary inputs to persisted resource arguments indiscriminately.
- Trace retained inputs to real uses. Remove unused inputs deliberately, checking callers and migrations.
- Renames, required additions, tighter validation, type/default/null changes, and source-of-truth changes can break callers; review real consumers and plans.

## Decision Examples

| Candidate | Decision |
| --- | --- |
| Retention differs between dev and prod. | Root input. |
| Worker concurrency adjusted frequently through infrastructure releases. | Input if the requirement is demonstrated. |
| Fixed implementation protocol or suffix. | Keep internal. |
| Total CPU calculated from replicas and CPU per replica. | Derive it, not a second synchronized input. |
| Subnet ID managed in the current stack. | Reference it directly; pass to a child when needed. |
| Subnet ID published by another stack. | Resolve the published contract, not a manually copied variable-file value. |
| Application feature flag changed independently of infrastructure. | Runtime configuration service. |
| Database credential. | Approved secret delivery, never committed configuration. |

## Executable Validation Fixture

This provider-free fixture requires Terraform 1.3 or later. Split the blocks
into the files indicated by comments; add `main.tf` containing a comment that no
resources are needed and a README explaining the fixture. It is an isolated
test, not a deployed stack using local state. The simple, single-use total stays
inline in the output rather than becoming a local.

```hcl
# versions.tf
terraform {
  required_version = ">= 1.3.0"
}

# variables.tf
variable "capacity" {
  description = <<-EOT
    Worker capacity for the deployment. replicas is a whole number from 1
    through 20. cpu_per_replica is a whole number of CPU units from 1 through
    8 and defaults to 2 when omitted or null. The capacity object is required
    and cannot be null.
  EOT
  type = object({
    replicas        = number
    cpu_per_replica = optional(number, 2)
  })
  nullable = false

  validation {
    condition = var.capacity.replicas == null ? false : (
      var.capacity.replicas >= 1 &&
      var.capacity.replicas <= 20 &&
      floor(var.capacity.replicas) == var.capacity.replicas
    )
    error_message = "capacity.replicas must be a whole number from 1 through 20."
  }

  validation {
    condition = (
      var.capacity.cpu_per_replica >= 1 &&
      var.capacity.cpu_per_replica <= 8 &&
      floor(var.capacity.cpu_per_replica) == var.capacity.cpu_per_replica
    )
    error_message = "capacity.cpu_per_replica must be a whole number from 1 through 8."
  }
}

# outputs.tf
output "total_cpu_units" {
  description = "Total CPU units requested across all worker replicas."
  value       = var.capacity.replicas * var.capacity.cpu_per_replica
}
```

## Verification

- Audit every root input and variable-file entry against the two admission criteria, and distinguish root decisions from child arguments.
- Check that constants, derived values, and managed attributes are not unnecessarily exposed; verify cross-stack publication contracts and independent runtime configuration.
- For the fixture, run `terraform init -backend=false -input=false`, `terraform fmt -check -recursive`, and `terraform validate`.
- Run `terraform plan -input=false -var='capacity={replicas=3}'` and confirm 6 CPU units. Explicit CPU count 4 yields 12; null CPU count yields 6. Test lower and upper boundaries.
- Confirm missing/null capacity, null/fractional replicas, and out-of-range/fractional CPU counts fail with the intended messages, not merely a nonzero exit.
- Inspect sensitive-value flow, nested nulls, descriptions, and real caller compatibility. A description does not enforce constraints, and defaults can suppress necessary decisions or defer failures.
