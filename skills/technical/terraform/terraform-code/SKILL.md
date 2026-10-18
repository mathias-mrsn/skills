---
name: terraform-code
description: Use when writing or reviewing Terraform code organization, file responsibilities, naming, input and output contracts, local values, data sources, or version requirements.
version: 0.1.0
author: 'mathias-mrsn, OpenAI'
platforms: [linux, macos, windows]
---

# Terraform Code

## When to Use

- Write or review Terraform root configurations and reusable resource modules.
- Decide how to name identifiers, expose inputs and outputs, place locals, or declare versions.
- Reorganize files without changing resource addresses or infrastructure behavior.
- This skill covers code structure and contracts, not stack architecture or backend operations.

## Read the Relevant Guidance

Read the applicable references before editing the corresponding code. The
summaries below are navigation, not substitutes for the detailed rules.

| Reference | Read when |
| --- | --- |
| [Naming](references/naming.md) | Naming resources, modules, locals, inputs, outputs, object fields, or tags; distinguishing IDs, ARNs, names, and collections. |
| [Variables](references/variables.md) | Deciding what deserves an input and defining its type, description, default, null behavior, validation, or sensitivity. |
| [Outputs](references/outputs.md) | Deciding what to expose to consumers and defining stable, documented output contracts. |
| [Locals](references/locals.md) | Deciding whether an expression needs a local and where that local belongs. |
| [Versions](references/versions.md) | Writing `versions.tf`, distinguishing requirements from provider configurations, or reviewing version selection and lock files. |

All five references are bundled with this skill. Read multiple references
when a change crosses concerns; for example, adding an input requires both
the naming and variable rules.

## File Responsibilities

Terraform loads configuration files in a module together. Filenames do not
create execution order or private scopes. The layout below is a project
convention, not a Terraform language requirement.

| File | Contents and placement |
| --- | --- |
| `main.tf` | Primary resources and module calls. Small sets of data sources may remain here. Always present because project tooling may require it, not because Terraform itself requires this filename. |
| `variables.tf` | All `variable` blocks, and only those declarations with their comments. Never declare variables elsewhere. See [variables](references/variables.md). |
| `outputs.tf` | All `output` blocks, and only those declarations with their comments. Never declare outputs elsewhere. See [outputs](references/outputs.md). |
| `versions.tf` | Terraform version requirements, provider source addresses and version constraints, and required child-module aliases. No provider configurations or backend settings. See [versions](references/versions.md). |
| `providers.tf` | Root `provider` configurations, including aliases and role/region configuration. Never put provider blocks elsewhere or add them to reusable children. |
| `backend.tf` | Root remote backend declaration only. Never put backend configuration in a reusable child module or credentials in committed configuration. |
| `locals.tf` | Necessary locals consumed by multiple files, not a dumping ground for every computed expression. See [locals](references/locals.md). |
| `data.tf` | Data source declarations extracted from `main.tf` when that improves readability; detailed rules below. |
| Thematic `.tf` files | Cohesive resource/module declarations, such as `network.tf` or `workers.tf`, with any necessary file-specific locals at their top. |
| `README.md` | Purpose, usage, requirements, inputs, outputs, dependency contracts, and significant operational behavior. |

- Require `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, and `README.md` in every root and reusable module. An unused interface file may contain a short comment explaining that it has no declarations.
- Other files are conditional on their responsibilities being needed. Do not create empty `locals.tf`, `data.tf`, or `providers.tf` merely to complete a template.
- Dedicated file responsibilities take precedence over proximity: a variable belongs in `variables.tf` even when only one resource uses it.
- Do not add unrelated declarations to dedicated files. Comments documenting their contents are appropriate; necessary file-specific locals at the top of `data.tf` are the explicit supporting-logic exception.
- Group implementation by responsibility instead of putting everything into `main.tf`. Use descriptive `snake_case` thematic filenames.
- Apply these rules to maintained configuration. Do not hand-edit generated files or the dependency lock file to imitate the layout; fix the generator or report an incompatible tool convention.

## Data Sources and `data.tf`

- A `data` block reads an existing external value; it does not declare a resource managed by the current configuration. Use direct resource references when the current configuration already owns the dependency.
- Keep a small, readable set of lookups in `main.tf`. Extract them into `data.tf` when they obscure the main resource/module flow; there is no arbitrary line-count threshold.
- Put extracted `data` declarations in `data.tf`, not unrelated resources, variables, outputs, provider configurations, or backend settings. A justified local used only by those lookups may be declared at its top.
- Resolve external dependencies at the root by default and pass narrowly scoped attributes into children. A child-owned lookup must be a deliberate part of that module's responsibility.
- Make account, region, lookup path, ownership, and selection criteria explicit. Avoid ambiguous name-only searches or hidden assumptions about which environment is active.
- Do not replace every explicit dependency with discovery. Data sources still require permissions, correct ordering, and a reliable published contract.
- For inter-stack values, prefer Parameter Store, Secrets Manager, or AppConfig according to the value's purpose. `terraform_remote_state` is forbidden.
- Ordinary secret data sources may persist returned values in state. External secret storage does not by itself prevent that persistence.
- Image discovery must constrain ownership and image criteria. Document whether the deployment pins an image or deliberately follows a release stream: `most_recent = true` can change a plan without an input change. Avoid unnecessary discovery when an explicit image is supplied.
- Backend initialization precedes data sources. Never try to retrieve a backend's own configuration through `data` blocks.
- Data source names follow the same identifier conventions as managed resources; see [naming](references/naming.md).

## Directory Layout

This tree illustrates a root stack; it is not a deployable configuration.

```text
stack/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
├── README.md
├── providers.tf               # When root provider configuration is needed
├── backend.tf                 # Root remote backend declaration
├── locals.tf                  # Only necessary cross-file locals
├── data.tf                    # Extracted lookups when useful
├── workers.tf                 # Optional cohesive implementation file
├── environments/
│   ├── dev.tfvars.json
│   ├── staging.tfvars.json
│   ├── prod.tfvars.json
│   └── .overwrite.auto.tfvars.json # Optional local override; ignored, never committed
└── .gitignore
```

- Reusable modules retain the five required files but do not contain backend configuration or variable assignment files.
- Environment assignments are JSON files under the root stack's `environments/` directory. Do not duplicate Terraform code into per-environment directories.
- The optional local override is `environments/.overwrite.auto.tfvars.json` and is ignored by Git. Terraform does not auto-load variable files from this subdirectory; pass it explicitly. Intended nonsecret environment files and the root provider lock file remain versioned.
- Ignore `.terraform/`, alternate working metadata directories, state files, generated backend configuration, saved plans, local overrides, and editor artifacts.
- This is the file layout only. Backend retrieval, state identity, locking, workspace checks, and variable-file precedence belong to the deployment workflow, not a new resource-module interface.

## Shared Readability Rules

- Keep expressions direct; use `var.name` rather than redundant interpolation such as `"${var.name}"`.
- Explain non-obvious intent, constraints, and tradeoffs in comments rather than narrating syntax.
- Use `for_each` with stable, plan-known, nonsensitive keys for meaningful resource identities. Reserve `count` for optional singletons or genuinely index-based instances; its count must also be known at plan time.
- Changing a map key used by `for_each` changes resource identity. Review plans and migration requirements before renaming it.
- Keep formatting changes separate from behavior changes when practical. Moving a block between files in one module should not change its address or arguments; moving it across module directories is not merely a file-layout change.

## Supporting Material

- For a distributable module, include `examples/simple/`, `examples/complete/`, automated `tests/`, and a `.pre-commit-config.yaml` with pinned hook revisions for formatting, validation, linting, and documentation checks.
- Public modules require a license chosen by the owner, such as MIT or Apache-2.0. Private internal modules may omit one. Do not assume licensing authority or embed license templates in this skill.
- Examples and human-readable documentation must be in English and contain no credentials or private infrastructure identifiers.

## Procedure

1. Inspect module boundaries, callers, existing workflow, version requirements, and generated files.
2. Read the relevant bundled references for every concern touched by the change.
3. Put declarations into their designated files and keep implementation expressions near their consumers.
4. Check dependency discovery, naming, input/output contracts, local necessity, and compatibility with callers.
5. Format, validate, test representative inputs, and inspect plans without applying infrastructure.

## Verification

- Confirm file responsibilities, required files, bundled reference paths, and the absence of unrelated declarations in dedicated files.
- Run `terraform fmt -check -recursive`, initialize appropriately, and run `terraform validate`. Run the repository's actual lint/documentation checks: validation alone does not enforce these conventions.
- Execute the isolated fixture in [variables](references/variables.md) to check typing, defaults, nulls, and rejection diagnostics.
- Review representative caller plans after interface changes. Do not rename resource labels without considering state migration.
- Report missing tools, providers, credentials, or state access and distinguish syntax checks on fragments from actual runtime verification.
