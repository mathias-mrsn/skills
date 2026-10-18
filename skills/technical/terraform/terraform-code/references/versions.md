# Terraform and Provider Requirements

## What Belongs in `versions.tf`

- Put the `terraform` block declaring `required_version` and `required_providers` here, never in implementation or provider-configuration files.
- `required_version` constrains the Terraform CLI, not AWS provider versions or module source versions.
- For each provider, declare its explicit source address and supported version constraint.
- Child modules declare required provider aliases with `configuration_aliases`; configurations themselves come from the caller.
- Do not put `provider` blocks, credentials, regions, role configuration, or backend settings in `versions.tf`. Root provider configurations belong in `providers.tf`; the S3 backend declaration belongs in root `backend.tf`.
- Keep `versions.tf` present even when no external provider is needed; an isolated provider-free fixture can declare just `required_version`.

## Runtime and Provider Selection

- The deployment standard is the latest stable Terraform release, with controlled upgrades and one exact selected release across local tooling and CI.
- A language constraint is a compatibility declaration, not a runtime installer or automatic upgrade mechanism. Record the selected runtime in the project's toolchain configuration.
- Keep the declared floor compatible with every feature used. Native S3 locking requires at least 1.10, cross-object variable validation 1.9, native tests 1.6, and provider mocking 1.7. Feature floors are not recommendations to run an older deployment runtime.
- Never silently raise an existing module's minimum supported version during a formatting or file-layout change. Treat that as a compatibility decision and update tests/documentation deliberately.
- Roots select provider releases reproducibly through constraints and their committed `.terraform.lock.hcl`.
- Reusable modules declare tested compatibility constraints rather than imposing the root's exact provider selection on every caller. Do not invent upper compatibility bounds without a reason; use them when known limitations or tested policy justify them.
- A constraint such as `~> 5.0` allows compatible selections below 6.0; it is not an exact pin. Distinguish a constraint from the selected release.
- Review provider upgrades with plans and tests; do not run `terraform init -upgrade` as a routine formatting or provider-removal step.

## Provider Aliases

- Children declare provider requirements, not provider configurations. Root modules configure accounts/regions and pass the needed configurations.
- Unaliased default configurations can be inherited for multiple provider types. Aliases are never inherited automatically.
- If a child requires `aws.primary` and `aws.replica`, declare both aliases and require the caller's explicit `providers` map.
- For multi-account/multi-region calls, verify every mapping intentionally; a correct version requirement does not prevent routing resources to the wrong account.

This `versions.tf` fragment illustrates source, constraints, and aliases. It is
not a current-provider-version recommendation or a complete runnable module:

```hcl
terraform {
  required_version = ">= 1.10.0"
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 5.0, < 6.0"
      configuration_aliases = [aws.primary, aws.replica]
    }
  }
}
```

Each relevant child resource chooses `provider = aws.primary` or
`provider = aws.replica`, and the caller supplies both configurations explicitly.

## What `versions.tf` Does Not Lock

- The provider lock file locks provider selections and checksums, not the Terraform CLI or remote module source versions.
- Registry module versions belong in the consuming `module` block's `version` argument, not `required_providers`.
- Git module sources use immutable commit references for reproducibility; the registry `version` argument does not apply to Git or local paths.
- Local path modules are versioned with their containing repository.
- Changing source versions, minimum runtimes, or provider compatibility bounds needs deliberate review rather than being hidden inside a file move.

## Verification

- Verify file placement, provider source addresses, version meanings, and required aliases.
- Compare the installed runtime and toolchain/CI selection with declared requirements.
- Initialize and validate representative roots/examples without upgrading dependencies unnecessarily.
- Review lock-file changes and test provider alias routing in realistic callers.
- Report syntax-only checks on fragments separately from initialized validation and real-cloud tests.
