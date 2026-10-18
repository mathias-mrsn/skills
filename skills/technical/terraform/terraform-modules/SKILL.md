---
name: terraform-modules
description: Use when defining reusable Terraform resource boundaries, splitting stacks, sharing code across environments, designing dependency contracts, or wiring providers.
version: 0.1.0
author: 'mathias-mrsn, OpenAI'
platforms: [linux, macos, windows]
---

# Terraform Resource Modules and Stacks

## When to Use

- Decide whether a resource group warrants a reusable module.
- Separate infrastructure into independently deployed stacks with bounded state.
- Design module dependency contracts, version compatibility, and provider aliases.
- Set up shared stack code with independent deployment boundaries.
- This skill governs architectural boundaries and wiring, not declaration style or file-layout conventions.

## Philosophy

- Create a reusable module like a Python function: encapsulate a cohesive resource group that must be repeated across multiple stacks.
- A module is not a folder for hiding complexity or wrapping an entire application architecture.
- Separate deployment concerns into small stacks; reuse each stack's code across environments rather than copying it.
- Small state boundaries reduce blast radius and can reduce plan work. They do not guarantee a particular runtime: provider calls, dependencies, and resource counts still matter.
- These are architectural conventions, not limitations imposed by Terraform.

## Rules

### Resource Modules, Not Infrastructure Wrappers

- Require a concrete cross-stack reuse case before extracting a resource module. Keep one-off resource groups directly in their owning stack.
- Give a reusable module one responsibility: a VPC with subnets and routing, a security group with rules, or an RDS instance with its subnet group.
- Do not create infrastructure/composite modules such as `web-application` that orchestrate VPC, ALB, ECS, databases, and unrelated concerns behind one interface.
- Do not create nested wrapper layers solely to forward inputs into other modules. Root stacks own composition; reusable modules own focused resource groups.
- Keep roots and reusable modules distinct. Roots own deployment identity, provider configurations, remote backend, environment selection, and dependency discovery. Child modules receive explicit contracts and do not own backend or environment selection.

### Stack Boundaries and Shared Environment Code

- Separate stacks by concern and lifecycle: networking, compute, data, storage, and IAM are useful starting boundaries. Do not place everything into one giant root and state.
- Refine boundaries according to ownership, permissions, change frequency, and failure isolation; do not split every resource into an independently operated stack.
- Use one common codebase per stack for dev, staging, and production. Do not create `environments/prod/main.tf`, `environments/staging/main.tf`, or other copied environment roots.
- Deploy one environment per invocation with a distinct remote state identity for each stack/environment pair. Do not iterate over environments with resource/module `for_each` or `count` in one state.
- Do not use variable files as a database of inter-stack identifiers. Publish shared values through Parameter Store, Secrets Manager, AppConfig, or an equivalent service appropriate to the value.

### Dependency Contracts

- Do not hardcode environment-specific AMIs, instance sizes, subnet IDs, or production tags in resource modules. Parameterize genuine caller decisions and dependency attributes.
- Do not interpret "configurable" as "every literal must become a variable". Keep implementation invariants and derived expressions internal; avoid provider-shaped option bags and speculative inputs.
- Resolve external dependencies through data sources at the root by default, then pass narrowly typed attributes to children. A module-owned lookup is appropriate only when it is a deliberate part of that module's responsibility.
- `terraform_remote_state` is forbidden, including at team boundaries. Publish narrow dependency contracts in the appropriate AWS service rather than granting consumers access to another stack's state.
- Document producer ownership, lookup paths, account/region/environment scope, permissions, deployment order, and freshness of published values. A remote output change does not automatically deploy a consumer.
- For image discovery, constrain ownership and image criteria deliberately; `most_recent = true` introduces updates without input changes. Document whether the deployment pins an image or intentionally follows a release stream.
- Avoid unnecessary image discovery when the caller supplies an explicit image ID.

### Providers and Module Versions

- Choose a Terraform/provider version floor that supports the syntax used and tested upper compatibility bounds where needed.
- Reusable children declare provider source addresses, supported constraints, and required aliases; they do not configure providers themselves. Roots own provider configurations.
- Unaliased default provider configurations can be inherited for multiple provider types. Aliased configurations are never automatically inherited: declare `configuration_aliases` and pass them explicitly.
- For multi-account or multi-region calls, map every required configuration deliberately to prevent accidental use of a root default provider.
- Use registry `version` constraints for registry modules and immutable commit references for Git sources; the registry `version` argument does not apply to Git or local paths.
- A constraint such as `~> 5.0` bounds compatible updates but is not an exact pin. Choose exact versions when reproducibility requires them, and review updates deliberately.
- Commit the root provider lock file. It locks provider selections, not remote module versions. Local path modules are versioned with the containing repository.
- Treat changed defaults, required inputs, stricter validation, resource address changes, and removed outputs as compatibility decisions; document migrations rather than hiding them behind a version bump.

## Architecture and Wiring Examples

These trees illustrate structure; they are not runnable configurations.

```text
infra/
├── modules/
│   ├── vpc/                 # VPC + subnets + route tables
│   ├── security-group/      # Security group + rules
│   └── rds/                 # RDS instance + subnet group
└── stacks/
    ├── networking/          # Common code; distinct state per environment
    ├── compute/
    ├── data/
    ├── storage/
    └── iam/
```

Do not add `modules/web-application/` that wraps VPC, ALB, and ECS calls.
Do not duplicate the stack's `.tf` files under environment directories.

The following provider-wiring fragments are not standalone configurations.
They assume a focused replicated-storage module, declared inputs, and root
provider aliases configured for the intended accounts/regions.

Child `versions.tf`:

```hcl
terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 5.0, < 6.0"
      configuration_aliases = [aws.primary, aws.replica]
    }
  }
}
```

Root `main.tf`:

```hcl
module "replicated_storage" {
  source      = "../../modules/replicated-storage"
  bucket_name = var.bucket_name

  providers = {
    aws.primary = aws.us_east_1
    aws.replica = aws.eu_west_1
  }
}
```

Inside the child, each relevant resource explicitly selects
`provider = aws.primary` or `provider = aws.replica`. Declaring aliases without
the caller's provider map is incomplete.

## Procedure

1. Identify reusable resource groups and actual consumers; leave one-off code in its stack.
2. Define bounded stacks, one shared codebase per concern, and distinct remote state identities per environment.
3. Design narrow dependency publication contracts without reading another stack's state.
4. Define focused dependency contracts, public outputs, provider requirements, and aliases.
5. Check that each environment uses the same stack code and only one environment is targeted per deployment.
6. Verify that dependency discovery and provider configurations target the intended accounts and regions.
7. Add examples and tests, document compatibility and source versions, and verify representative consumers.

## Pitfalls

- Extracting a god module or a wrapper without demonstrated reuse.
- Copying roots per environment, or provisioning all environments in one state.
- Calling `.tfvars` a configuration store and copying service-managed identifiers into it.
- Replacing module inputs with broad discovery that silently selects the wrong account or region.
- Using `terraform_remote_state` as a shortcut, even across ownership boundaries.

## Verification

- Verify module boundaries, shared code across environments, and unique state identities.
- Confirm no `terraform_remote_state` blocks, copied environment roots, or infrastructure wrapper modules exist.
- Run `terraform fmt -check -recursive`, validate examples and consumer roots after initialization, and run the project's lint/documentation hooks.
- Exercise valid inputs, defaults, nulls, invalid values, and output attributes. Native `terraform test` requires Terraform 1.6 or later; provider mocking requires 1.7 or later. Match features to the declared version floor.
- Use provider mocks for isolated tests where appropriate; gate real-cloud integration runs on explicit authorization, credentials, cleanup, and cost controls. Test idempotency and provider alias routing in realistic consumers.
- Inspect plans without applying infrastructure. Report which checks require remote access and were not run; do not claim layout illustrations or provider-wiring fragments are deployable examples.
