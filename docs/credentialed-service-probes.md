# Credentialed Service Probes

The service probes check whether local `.env` credentials authenticate without printing secrets and
without mutating vendor state.

```bash
python scripts/probe_service_keys.py --env-file .env
python scripts/probe_service_keys.py --env-file .env --no-fail
```

For repeatable CI-shaped service checks, use the JSON E2E specs:

```bash
python -m claude_agent_harness_optimization mcp-e2e evals/e2e/github_readonly.json --env-file .env
python -m claude_agent_harness_optimization mcp-e2e evals/e2e/github_readonly.json --dry-run
```

The probe script is a broad local credential check. `mcp-e2e` is the auditable harness check that
can be committed as a spec and rendered into reports.

The probes are intentionally read-only:

- Firecrawl: reads recent team activity.
- GitHub: reads the authenticated user.
- Cloudflare: verifies a user API token when possible, then falls back to reading
  `CLOUDFLARE_ACCOUNT_ID` because account and R2 tokens may not pass the user-token verify endpoint.
- Cloudflare R2: reads the account R2 bucket list through the REST API and reports the specific R2
  entitlement state.
- ClickHouse Cloud: reads visible organizations through the Cloud API.
- Stripe: reads the account attached to the secret key.

Cloudflare R2 has two credential shapes:

- `CLOUDFLARE_R2_API_TOKEN`: Cloudflare account token used by the REST API for account/R2 checks.
- `R2_ACCESS_KEY_ID` plus `R2_SECRET_ACCESS_KEY`: S3-compatible credentials for R2 object access.

When Cloudflare shows an R2 token value, the S3 Secret Access Key is the SHA-256 hash of that token
value, and the Access Key ID is the token id shown by the dashboard.

ClickHouse has two credential layers. `CLICKHOUSE_CLOUD_KEY_ID` and
`CLICKHOUSE_CLOUD_KEY_SECRET` prove ClickHouse Cloud control-plane access. The official ClickHouse
MCP server also needs database connection variables such as `CLICKHOUSE_HOST`, `CLICKHOUSE_USER`,
`CLICKHOUSE_PASSWORD`, `CLICKHOUSE_DATABASE`, and `CLICKHOUSE_ALLOW_WRITE_ACCESS=false` for
credentialed end-to-end query traces.

Use test or sandbox credentials for mutation-capable services. A live Stripe key should only be used
for read-only checks unless the task explicitly requires live account changes.
