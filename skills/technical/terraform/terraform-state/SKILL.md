---
name: terraform-state
description: Use when configuring AWS Terraform state in S3, native state locking, Parameter Store backend bootstrap, Makefile or Bazel initialization, JSON tfvars, CLI workspaces, or safe state operations.
version: 0.1.0
author: 'mathias-mrsn, OpenAI'
platforms: [linux, macos, windows]
---

# AWS Terraform State and Deployment Selection

## When to Use

- Bootstrap or review S3 state storage and its native lockfile permissions.
- Implement the Parameter Store to Makefile/Bazel initialization workflow.
- Select a stack and environment consistently across state, credentials, and JSON inputs.
- Investigate lock contention or prepare an explicitly authorized destructive operation.

## Philosophy

- Use one standard AWS workflow, not a catalog of alternative backends.
- Run the latest stable Terraform release, with controlled upgrades and the same exact release in local tooling and CI. Native S3 locking requires at least Terraform 1.10; that is a feature floor, not a recommendation to run an old release.
- Backend settings are bootstrap-owned configuration, not deployment variables.
- A state boundary is an ownership and failure boundary; input files and workspace names are not access controls.

## Rules

### State Storage and Bootstrap

- Always store deployed stack state in AWS S3. Do not offer local state, other cloud backends, or hosted Terraform services as deployment alternatives.
- Bootstrap the state bucket, access policies, and backend parameter before initializing consuming stacks. Use an already established administrative deployment path; do not silently fall back to local state to solve the bootstrap dependency.
- Enable S3 versioning, explicit encryption at rest, public-access blocking, and a bucket policy enforcing TLS. Protect the bucket and any encryption key from accidental destruction.
- Configure access auditing and retain recoverable object versions according to an explicit policy. Periodically test recovery; versioning without a working recovery procedure is insufficient.
- Use scoped short-lived AWS credentials from SSO, assumed roles, or CI federation. Restrict state and lock access by environment and stack; sharing a bucket does not imply sharing permissions.
- Grant `s3:ListBucket` with the appropriate prefix scope, and `s3:GetObject`/`s3:PutObject` for the state object. Routine state access does not require `s3:DeleteObject` on the state object.
- Separately grant `s3:GetObject`, `s3:PutObject`, and `s3:DeleteObject` on `<state-key>.tflock`. Lockfile deletion is required for normal lock release.
- When using a customer-managed KMS key, grant only the necessary encryption, decryption, and data-key permissions on that key. Include version-read permissions for the authorized recovery role, not every deployment role.
- Treat state, downloaded backups, and saved plans as confidential. `sensitive = true`, environment variables, or reading a secret from Secrets Manager do not by themselves prevent persistence.
- `terraform_remote_state` is forbidden. Publish narrow dependency values through Parameter Store, Secrets Manager, or AppConfig instead of granting consumers access to state snapshots.

### Backend Configuration in Parameter Store

- During bootstrap, publish the common S3 backend settings as a JSON document in AWS Systems Manager Parameter Store. This is the authoritative configuration, not a preference or an optional alternative to copied backend files.
- Share that configuration across the stacks using the same backend boundary. If accounts or security boundaries require different settings, publish separate scoped documents without duplicating stack code.
- Store noncredential backend attributes such as bucket, region, encryption settings, and `use_lockfile = true`. Never store AWS access keys, session tokens, or secret credential material in the backend document.
- The root declares the S3 backend type in `backend.tf`. The common JSON omits the per-stack state key; the shared launcher derives it from the validated deployment identity.
- Makefile, Bazel, or an equivalent shared launcher must retrieve the parameter automatically before `terraform init`. Terraform data sources cannot retrieve their own backend configuration before initialization.
- Define the parameter's name, owning account, region, bootstrap owner, and read permissions explicitly. The backend account and workload account may differ; verify the effective identity for each rather than assuming provider credentials also configure the backend.
- Parse and validate the JSON against a known schema. Fail closed on retrieval errors, unexpected accounts, missing fields, disabled encryption/locking, unknown attributes, or invalid values. Never continue with stale cached settings or an implicit local backend.
- Render a backend-supported partial configuration file or explicit backend arguments from validated values. The hosted document is JSON; do not assume it can be passed unchanged to `-backend-config`. A conventional generated `.tfbackend` file has top-level HCL attributes, not a `terraform` wrapper.
- Keep generated configuration and Terraform working metadata ignored by Git, with restrictive file permissions. Backend arguments are retained in working metadata and can be retained in plans; they must not contain credentials.
- Maintain documented break-glass access to recover backend configuration when Parameter Store is unavailable, without making that an automatic fallback.

### State Identity and CLI Workspaces

- Use one common codebase per stack and one state per deployment identity. Derive a stable key from workload account, workload region, environment, and stack, for example `<account>/<region>/<environment>/<stack>/terraform.tfstate`.
- Validate stack/environment selections against known targets before deriving paths. Include a project namespace when multiple projects could otherwise collide.
- Confirm the workload identity, backend identity, bucket, region, and key before running a plan. Backend region describes the bucket, not necessarily the workload region.
- Use only the Terraform CLI workspace `default`. Do not create or select named workspaces for dev, staging, prod, branches, or teams, and do not derive resource configuration from `terraform.workspace`.
- Reject a non-default `TF_WORKSPACE` and check `terraform workspace show` after initialization. Do not silently switch away from an unexpected workspace and continue.
- Named S3 workspaces alter object paths through `workspace_key_prefix`; they do not provide IAM isolation. Keep environment selection in the launcher and explicit state key instead.
- Isolate Terraform working metadata per deployment identity using a separate `TF_DATA_DIR` or isolated working directory. Ignore these generated directories and serialize operations sharing one local working directory.
- Use `terraform init -reconfigure -input=false` with the resolved backend configuration when binding a working directory to the selected identity. Reconfiguration does not copy or migrate existing state.
- Changing an environment must select its own existing state, never migrate another environment's state. A genuinely new deployment must be explicitly recognized; unexpected empty state for an existing deployment is a stop condition, not permission to recreate infrastructure.

### JSON Variable Files

- Store environment input assignments at the stack root under `environments/<environment>.tfvars.json`, always in JSON. Do not duplicate `.tf` code into per-environment directories or put variable assignment files inside reusable modules.
- Select the input file from the same validated identity used to derive the state key and choose AWS roles. If inputs include environment/account/region fields, verify they agree with that identity.
- Keep variable files minimal: deployment decisions that differ between environments or genuinely change frequently, not all application configuration or manually copied inter-stack identifiers.
- Use the exact path `environments/.overwrite.auto.tfvars.json` for optional local overrides and exclude it from Git. Version intended nonsecret environment JSON files; do not blanket-ignore all variable files.
- Pass `-var-file=environments/<environment>.tfvars.json` first and, if present, `-var-file=environments/.overwrite.auto.tfvars.json` last. Terraform does not auto-load variable files from subdirectories, regardless of their `.auto.tfvars.json` suffix; the launcher must pass both files explicitly in that order.
- Variable files replace whole variable values, not recursively merge objects. Test optional-field defaults after replacement rather than assuming base fields survive.
- Do not let variable overrides change the validated state/deployment identity, backend settings, or target credentials. Report the presence of local overrides without logging their values.
- CI must start without an unapproved local override. Reject unexpected auto-loaded variable files and uncontrolled CLI/environment variable sources that would bypass the launcher's selection.
- Use the same effective inputs for planning and execution. When applying an approved saved plan, apply that plan artifact rather than adding new variable arguments; bind its identity and source revision to the reviewed run.

### Native S3 Locking

- Set `use_lockfile = true` for every deployed state. Native locking is opt-in in Terraform, so the launcher must validate it explicitly.
- Do not configure DynamoDB locking or provide a legacy-locking fallback. This workflow targets current Terraform.
- Never bypass locking with `-lock=false`, delete a lock object manually, or make force-unlock automatic.
- Use a bounded Terraform lock acquisition wait, such as `-lock-timeout=5m`. A timeout around an entire apply is not a substitute and can interrupt active work.
- Serialize CI by the full state identity, not Git branch alone. Queue competing operations; do not cancel an active apply merely because a newer commit arrives.
- On contention, inspect lock ownership, operation, creation time, and the associated CI job/operator. Wait for a live operation.
- Before any force-unlock, prove no writer remains active, confirm the exact state and lock ID, obtain explicit authorization, and record the incident. A failed runner or lost network connection alone does not prove the writer stopped.

### Recovery and Destructive Operations

- Freeze writers before recovery or state migration; verify identities, take a protected backup, and document rollback before changing state.
- Restore only through an explicitly reviewed procedure using the correct S3 object version and Terraform state safety checks. Restoring a snapshot does not revert real AWS resources.
- Do not manually edit state, use forced state pushes to bypass lineage/serial checks, or present state removal as resource deletion. Imports, moves, removals, restores, and backend migrations require review of their exact consequences.
- For destruction, generate and review a destroy plan first. Inspect every planned deletion and replacement, including resources pulled into scope by dependencies, locals, or collection expressions.
- Targeted plans are exceptional and may omit other relevant changes; inspect dependencies and follow up with a full plan. A target list is not the complete deletion list.
- Obtain explicit authorization for the full destructive scope and execute only the approved plan. Never use production `destroy -auto-approve` or treat a prior implementation request as permission to destroy.
- After any authorized recovery or state change, run a fresh plan against the correct identity and reconcile differences before resuming automation.

## Configuration Examples

These are configuration illustrations, not a deployable bootstrap or a complete
launcher. Example names are placeholders, and no credentials are included.

Root `backend.tf`:

```hcl
terraform {
  backend "s3" {}
}
```

Example JSON value published by bootstrap at an agreed Parameter Store path:

```json
{
  "bucket": "example-terraform-state",
  "region": "eu-west-1",
  "encrypt": true,
  "use_lockfile": true
}
```

For the validated deployment identity `111122223333 / eu-west-1 / staging /
networking`, the launcher combines the shared settings with a derived key.
The resulting ignored `backend.tfbackend` contains top-level HCL attributes:

```hcl
bucket       = "example-terraform-state"
region       = "eu-west-1"
encrypt      = true
use_lockfile = true
key          = "111122223333/eu-west-1/staging/networking/terraform.tfstate"
```

The launcher retrieves the parameter through the AWS CLI/SDK, validates and
renders it, then invokes `terraform init -reconfigure -input=false
-backend-config=backend.tfbackend` with an identity-specific `TF_DATA_DIR`.
It verifies workspace `default` and then plans with
`-lock-timeout=5m -var-file=environments/staging.tfvars.json`, appending
`-var-file=environments/.overwrite.auto.tfvars.json` only when that approved file exists.

Example `environments/staging.tfvars.json`:

```json
{
  "capacity": {
    "replicas": 3
  }
}
```

An optional local override `{"capacity": {"replicas": 4}}` replaces the whole
capacity value when passed last. Any omitted fields then follow the variable
type's defaults, not a recursive merge with the environment file.

## Procedure

1. Bootstrap and protect S3 storage, native lock access, scoped IAM permissions, and the backend JSON parameter.
2. Resolve an allowed stack/environment and expected workload/backend identities using the shared launcher.
3. Retrieve and validate the Parameter Store document; derive the unique state key and isolate working metadata.
4. Initialize the S3 backend with native locking, verify workspace `default`, and reject unexpected state identity or empty state.
5. Select the matching JSON inputs, validate approved overrides and their precedence, and plan with a bounded lock wait.
6. Review the plan, bind its artifact to the deployment identity, and obtain explicit authorization before applying or performing destructive/state-changing work.
7. Record operational failures and follow reviewed recovery procedures; never bypass locking or silently change backend selection.

## Pitfalls

- Configuring providers correctly while the backend authenticates to the wrong account.
- Sharing common bucket settings but accidentally sharing a state key.
- Attempting to read backend settings with a Terraform data source or variable.
- Believing native S3 locking is enabled by default or omitting lockfile delete permission.
- Assuming a workspace name or JSON variable file supplies environment isolation.
- Applying against unexpected empty state after reconfiguration.
- Reading secrets through ordinary data sources and assuming their external origin keeps them out of state.

## Verification

- Check current Terraform release selection and local/CI parity. Test examples using the actual installed release and report its version; do not call an older test runtime "latest".
- Validate the bootstrap's S3 versioning, encryption, public-access/TLS protections, IAM scope, lockfile permissions, auditing, and Parameter Store ownership.
- Test launcher behavior with a stubbed parameter service: retrieval failure, malformed JSON, encryption/locking disabled, unexpected fields, identity mismatches, and key collisions must stop initialization.
- Check workspace handling, working-directory isolation, matching environment files, and rejection of identity-changing overrides. Verify the generated backend file contains the expected native locking settings and derived key.
- Run `terraform fmt -check -recursive` and `terraform validate` after appropriate initialization. Check generated partial backend files separately; they are not root Terraform configurations.
- In an authorized AWS test backend, verify concurrent operations contend on the same `.tflock`, normal completion releases it, and IAM prevents cross-environment access. A formatting check or mocked run does not prove S3 locking works.
- Test override precedence and whole-object replacement locally without cloud access. Restore a disposable test snapshot only with authorization and verify recovery against actual resources.
- Report unperformed cloud/bootstrap/locking/recovery checks. Do not run apply, destroy, force-unlock, migration, or state restoration as routine documentation validation.

## Source Context

Consulted Anton Babenko's `terraform-skill` state-management reference at
`https://github.com/antonbabenko/terraform-skill/blob/master/skills/terraform-skill/references/state-management.md`.
The upstream collection identifies Copyright 2026 Anton Babenko,
terraform-best-practices.com, Compliance.tf - Terraform Compliance for
Cloud-Native Enterprise, and Apache License 2.0.
This independently written project guidance uses the requested AWS-only
workflow rather than reproducing that document. It intentionally omits
multi-cloud backend catalogs, legacy locking recipes, remote-state data sharing,
and broad migration tutorials. All operational rules are included above;
the source is attribution, not a required reference.
