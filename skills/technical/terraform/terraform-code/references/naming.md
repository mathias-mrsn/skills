# Terraform Naming

## Identifiers and External Names

- Use descriptive `snake_case` for authored Terraform identifiers: resource/data labels, module labels, locals, variables, outputs, provider aliases, and object attributes or map keys whose schema the module owns.
- A resource address already includes its provider type. Prefer `aws_security_group.database` over `aws_security_group.database_security_group`; the label identifies purpose without repeating the whole type.
- Use `this` only for a genuine singleton of its resource type in a focused reusable module. If multiple resources of that type exist, give them distinct meaningful labels.
- Avoid generic public interface names such as `value` or `type`. Include enough context to distinguish the concept, such as `database_instance_class` or `application_port`, without repeating irrelevant module prefixes everywhere.
- Terraform identifiers and names sent to AWS APIs are different contracts. Do not rewrite provider-defined argument names, external schemas, DNS names, AWS resource names, or published contracts merely to enforce `snake_case`.
- Resource labels may differ from AWS physical names. Changing a label changes the Terraform address; changing an API name may replace a resource. Inspect the plan and migration needs rather than treating either as cosmetic.

## Input and Output Value Kinds

Use the same semantic naming for inputs, locals, and outputs. A suffix identifies
the value's meaning, not merely its primitive Terraform type.

| Meaning | Singular | Collection | Expected value |
| --- | --- | --- | --- |
| AWS resource identifier | `vpc_id`, `subnet_id` | `subnet_ids` | An ID, not an ARN or display name. |
| AWS ARN | `role_arn`, `kms_key_arn` | `role_arns` | A full ARN of the appropriate AWS resource. |
| Physical/logical name | `bucket_name` | `bucket_names` | A name, not a URL, ARN, or Terraform address. |
| URL | `queue_url` | `queue_urls` | A URL with the contractually required scheme. |
| DNS hostname | `database_hostname` | `database_hostnames` | A hostname without a scheme or port. |
| Service endpoint | `database_endpoint` | `database_endpoints` | Document whether it includes a port, scheme, or path. |
| IPv4/IPv6 CIDR | `vpc_cidr_block` | `subnet_cidr_blocks` | A CIDR, not an IP address or subnet ID. |
| Duration | `retention_days`, `timeout_seconds` | Use context-specific names. | State the unit explicitly. |
| Count/limit | `replica_count`, `concurrency_limit` | Use context-specific names. | Document whole-number and range constraints. |

- Do not call an ARN `role_id`, or expose an ID through an output named `bucket_arn`. Trace the actual provider attribute.
- Names do not enforce types or value validity: input type constraints and validation must match the name's meaning.
- Use singular names for single values and plural names for collections. Do not expose `subnet_ids` as one comma-delimited string.
- For maps with meaningful lookup keys, name the relationship, such as `subnet_ids_by_zone` or `roles_by_name`, and document the key/value contract.
- Prefer meaning over implementation-type suffixes. Do not add `_string`, `_list`, `_map`, `_input`, or `_output` merely to describe a container or direction.
- A cohesive output object can be named `database_connection`, with fields such as `hostname` and `port`. Its fields still need unambiguous meanings.
- Use boolean names as predicates or capabilities: `enable_monitoring`, `allow_public_access`, or `is_primary`. Do not encode booleans as strings or inverted flags without a compelling contract.

## Tags

- Use `tags` for a `map(string)` interface representing AWS tags. Name computed collections by purpose, such as `common_tags` or `resource_tags`.
- Use `snake_case` for new project-owned tag keys, such as `environment`, `managed_by`, or `cost_center`, unless an established organizational or external schema mandates another spelling.
- Preserve required external keys exactly, including AWS's conventional `Name` tag or existing organizational `CostCenter` contracts. Do not rename them as a style cleanup without reviewing consumers.
- Do not invent a mandatory tag inventory during a naming refactor. Preserve the agreed ownership, billing, and automation contract.
- Tag values are data, not Terraform identifiers. Do not transform owner names, application names, or environment values mechanically into `snake_case`.
- Document merge precedence and reserved keys. A description claiming caller overrides is correct only if the actual merge order permits it.

## Verification

- Compare input/output suffixes with the provider attributes actually passed or returned.
- Check singular/plural names, collection key semantics, boolean meaning, and duration units.
- Review external names and tag schemas separately from internal labels.
- Inspect resource-address and physical-name changes for state migration or replacement consequences.
