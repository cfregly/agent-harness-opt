# Supabase MCP Tool Tuning

This audit adds a second high-profile public MCP result that clears the
adversarially-confirmed to add value bar.

## Boundary

The critical Supabase database boundary is:

- `apply_migration`: DDL and schema-changing SQL that must be tracked as a migration.
- `execute_sql`: ordinary SQL that does not change database schema.

The failure mode is common in agent harnesses with short tool descriptions. If `execute_sql` only
says it executes raw SQL, models often treat `CREATE TABLE`, `CREATE INDEX`, and `CREATE POLICY` as
one-off raw SQL calls. Supabase's official source explicitly says to use `apply_migration` for DDL
operations and `execute_sql` for regular queries that do not change schema.

## Matrix

The matrix lives at:

```text
evals/model_matrix/supabase_mcp_database_tool_selection.json
```

It compares:

- `terse_supabase_database_mcp`: short descriptions like the ones often copied into custom
  harnesses.
- `tuned_supabase_database_boundaries`: explicit DDL, migration, and raw-query boundaries.

The adversarial cases are:

- `ddl create table uses migration`
- `ddl create index uses migration`
- `rls policy uses migration`

Each case asks the model to "run this SQL" while the SQL is a schema change. The expected next tool
is `apply_migration`, not `execute_sql`.

## Live Result

Full Anthropic prompt-JSON result:

- Terse: 6/9.
- Tuned: 9/9.
- Terse misses: `CREATE TABLE`, `CREATE INDEX`, and RLS policy creation chose `execute_sql`.
- Tuned passes: all schema-changing cases chose `apply_migration`.

Cross-provider adversarial DDL result:

- Anthropic native tools: terse 0/3, tuned 3/3.
- Anthropic prompt JSON: terse 0/3, tuned 3/3.
- OpenAI native tools: terse 1/3, tuned 3/3.
- OpenAI prompt JSON: terse 3/3, tuned 3/3.
- Gemini native tools: terse 0/3, tuned 3/3.
- Gemini prompt JSON: terse 0/3, tuned 3/3.

The tuned wording improves every failing provider and harness cell without regressing the passing
OpenAI prompt-JSON cell.

## Recommended Description Pattern

For `apply_migration`:

```text
Apply DDL or schema-changing SQL as a tracked Supabase migration. Use for CREATE TABLE, ALTER TABLE,
DROP TABLE, CREATE INDEX, RLS policy changes, functions, triggers, and extension enablement. Name
the migration in snake_case. Changes go directly to the remote project.
```

For `execute_sql`:

```text
Run regular SQL that does not change database schema. Avoid DDL and schema changes such as CREATE
TABLE, ALTER TABLE, DROP TABLE, CREATE INDEX, policies, triggers, functions, or extension
enablement. Use apply_migration for those.
```

## Why This Matters

This is not just tool polish. For Supabase, using `execute_sql` for schema changes bypasses the
migration pathway that makes changes auditable and replayable. In a real agent harness, that can
create drift between remote state, local migrations, and reviewable code changes.

The optimization is valuable because it fixes a high-impact tool-selection error before execution.
