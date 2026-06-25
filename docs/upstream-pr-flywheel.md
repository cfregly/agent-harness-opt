# Upstream PR Flywheel

Use this workflow when a harness matrix finds a real tool-selection or harness failure in a public
project. The goal is a small upstream pull request backed by enough data that a maintainer can
reproduce the claim.

Every promoted pull request must clear the adversarially-confirmed to add value bar.

## When To Open A PR

Open an upstream pull request when all of these are true:

- a baseline and candidate were run on the same task slice
- the candidate improved the measured result by the configured threshold
- held-out or adversarial cases did not regress
- the target source is pinned to an exact version, package, or commit
- the suggested patch is smaller than the evidence packet

Do not open an upstream pull request when stock and tuned descriptions both pass, when the miss was
an unfair verifier, or when the finding only works on one brittle prompt.

## Packet Command

Run the matrix first and save JSON:

```bash
python -m claude_agent_harness_optimization model-matrix evals/model_matrix/firecrawl_mcp_tool_selection.json \
  --env-file .env \
  --live \
  --require-live \
  --providers anthropic,openai,gemini \
  --harnesses prompt_json,native_tools \
  --variants legacy_firecrawl_mcp,tuned_firecrawl_mcp_boundaries \
  --instruction-variants firecrawl_host_rules \
  --cases "single known page structured fields" \
  --out /tmp/firecrawl-matrix.json
```

Then generate the upstream packet:

```bash
python -m claude_agent_harness_optimization upstream-pr-packet /tmp/firecrawl-matrix.json \
  --matrix evals/model_matrix/firecrawl_mcp_tool_selection.json \
  --target-name "Firecrawl MCP" \
  --target-repo https://github.com/firecrawl/firecrawl-mcp-server \
  --baseline-variant legacy_firecrawl_mcp \
  --candidate-variant tuned_firecrawl_mcp_boundaries \
  --change-summary "Clarify the single-page scrape versus extract boundary." \
  --evidence-url https://github.com/cfregly/claude-agent-harness-optimization/blob/main/docs/confirmed-improvements.md \
  --out-dir /tmp/firecrawl-upstream-pr
```

The packet contains:

- `PR_BODY.md` for the upstream pull request
- `REPRODUCTION.md` with exact command, source pin, scores, and cases
- `evidence.json` with result JSON, case definitions, source pins, and comparison data

## What Goes In The Upstream PR

Keep the upstream patch narrow. Good patches usually touch one of these:

- tool description
- input schema description
- README tool-choice guidance
- host harness instruction
- example prompt or usage snippet

The pull request body should include:

- catchy title that names the specific workflow value
- value proposition before implementation details
- source package, version, repo, and commit
- baseline and candidate variant names
- provider, model, harness, instruction variant, and case names
- provider profile and tier when present
- pass counts, scores, delta, and minimum threshold
- one failed baseline example and one passing candidate example
- confusable alternatives checked, not accusatory forbidden wording
- reproduction command
- public harness repo backlink
- specific result artifact link when the packet has a published matrix result

## Check Families

Use the check catalog to decide what failure class a pull request is proving:

```bash
python -m claude_agent_harness_optimization harness-checks --markdown
```

The current catalog covers adjacent tool boundaries, no-tool safety, argument quality, error
recovery, output budget, resource versus tool routing, directed thinking, harness parity, and
reproducibility.

## Flywheel Narrative

The public narrative is simple:

- popular MCP and agent projects expose tool surfaces
- each model and harness can interpret those surfaces differently
- this repo runs reproducible cross-model harness evals
- confirmed failures become tiny upstream pull requests
- each accepted pull request points back to a reusable eval packet
- every new project adds more matrices, pins, and public examples

That creates a feedback loop: maintainers get concrete fixes, and this repo becomes the receipt
layer for model and harness optimization.
