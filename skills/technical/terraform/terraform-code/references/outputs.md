# Terraform Outputs

## Decide What to Expose

- Add an output only for an identified consumer: a parent module, deployment integration, operator workflow, or intentionally published dependency contract.
- Do not export every resource attribute for hypothetical reuse or debugging. Keep the public interface small and intentional.
- A child output exposes a value to its caller; a root output exposes a value to root-level consumers. Child outputs are not automatically root outputs.
- Use direct references inside the same module. An output is not an internal variable or a way for sibling files to access each other.
- Root outputs do not themselves publish values into Parameter Store or another service. Cross-stack contracts require explicit publication; `terraform_remote_state` is forbidden.
- Check whether an existing cohesive output already serves the consumer before adding duplicate representations.

## Define the Contract

- Declare all outputs in `outputs.tf`, never another file. Include a nonempty English description explaining intended use.
- Follow [naming](naming.md): `_id`, `_arn`, `_name`, `_url`, collection plurals, and object field names must match the actual returned values.
- Return stable attributes or a cohesive object with a deliberate field set, not entire provider/resource objects that leak implementation details.
- Group related values when consumers use one coherent concept; keep independently useful values separate when that produces a clearer interface.
- Explain units, identifier scope, field meanings, ordering, map keys, and null/absence behavior. Document whether an endpoint contains a hostname, port, scheme, or path.
- Terraform output blocks do not support an input-style `type` argument. The output type is inferred from `value`; make its shape intentional and document/test it.
- Treat output shape, primitive types, collection semantics, and field names as public contracts. Do not change a scalar into a list or an ID into an ARN under the same name.
- Keep natural expression dependencies. Add explicit `depends_on` only when a genuine hidden dependency affects output readiness; do not use broad dependencies to order whole modules unnecessarily.
- For optional resources, define whether absence is null or an empty collection according to meaning. Do not invent an undocumented empty-string sentinel.

## Sensitivity

- Mark confidential outputs `sensitive = true`; ensure composite outputs do not accidentally expose secret fields.
- Sensitivity redacts ordinary display, not persistence or access through authorized raw/JSON output consumers. Protect state, plans, logs, and output-export workflows.
- `sensitive = false` is the default and does not declassify sensitive expressions. Do not use `nonsensitive` merely to silence Terraform's protection.
- A value retrieved from Secrets Manager is not automatically absent from state. Expose a secret reference rather than its payload when that meets the consumer's need.

## Example

These `outputs.tf` fragments assume existing resources and are not standalone
configurations:

```hcl
output "database_security_group_id" {
  description = "Security group ID for clients wiring database access rules."
  value       = aws_security_group.database.id
}

output "database_security_group_arn" {
  description = "Security group ARN for policies or inventory requiring an ARN."
  value       = aws_security_group.database.arn
}

output "database_connection" {
  description = "Database hostname and TCP port for application connection configuration."
  value = {
    hostname = aws_db_instance.database.address
    port     = aws_db_instance.database.port
  }
}
```

The first two outputs are justified only if real consumers require both forms.
The object deliberately excludes credentials and unrelated database attributes.

## Verification

- Identify the consumer for every output; remove unused public surface only after compatibility review.
- Confirm names match returned value kinds, inferred types, object fields, ordering, and optional-resource behavior.
- Test attributes and shapes with representative callers, including absent resources.
- Review sensitive output flows and automated JSON/raw exports.
- Treat renamed/removed outputs and changed shapes as possible breaking changes; document migrations rather than assuming documentation changes are harmless.
