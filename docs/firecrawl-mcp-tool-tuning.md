# Firecrawl MCP Tool Tuning

This audit is the first public MCP sweep result in this repo that clears the
adversarially-confirmed to add value bar.

## Summary

| Before | After | Result |
|---|---|---|
| `legacy_firecrawl_mcp` scored 0.000. Baseline focus: single known page structured fields. | `tuned_firecrawl_mcp_boundaries` scored 1.000, a 1.000 gain. | Apply this change: Clarify that `firecrawl_scrape` handles one known page, including structured JSON fields. Reserve `firecrawl_extract` for broader multi-page structured extraction jobs. Add retained cases as regression coverage. |

## Recommended Actions

- Apply this change: Clarify that `firecrawl_scrape` handles one known page, including structured JSON fields. Reserve `firecrawl_extract` for broader multi-page structured extraction jobs.
- Add the 1 retained routing case to upstream CI or release-blocking regression coverage.
- Keep the passing cells visible so maintainers preserve behavior that already works.

## Model Coverage

Provider/model rows are evidence lanes. The target repo actions above are the only primary CTA.

## Public Summary

- Outcome: Confirmed improvement.
- Focus: scrape-versus-extract routing for one known URL.
- Baseline: `legacy_firecrawl_mcp` at 0.000.
- Candidate: `tuned_firecrawl_mcp_boundaries` at 1.000.
- Delta: 1.000 against a 0.010 minimum.

<details>
<summary>LLM / Machine-readable details</summary>

## Boundary

The ambiguous boundary is:

- `firecrawl_scrape`: one known URL, including focused structured fields via a JSON format.
- `firecrawl_extract`: structured extraction across multiple pages or broader URL sets using the
  extraction layer.

Older Firecrawl wording said `firecrawl_scrape` was not recommended for structured data and to use
`firecrawl_extract` instead. Current guidance is more nuanced: use `scrape` with JSON format for one
known page, and reserve `extract` for multi-page or broader structured extraction jobs.

## Matrix

Matrix: [firecrawl_mcp_tool_selection.json](https://github.com/cfregly/agent-harness-opt/blob/main/evals/model_matrix/firecrawl_mcp_tool_selection.json)

It compares:

- `legacy_firecrawl_mcp`: older/legacy-style descriptions.
- `tuned_firecrawl_mcp_boundaries`: boundary descriptions that match current Firecrawl guidance.

The upstream version pin for this result is:

- package: `firecrawl-mcp` 3.22.0
- repository: [firecrawl/firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server)
- commit: `e744bba494c0e77086d66af838d7a64fab52f138`
- checked: 2026-06-25

The most important case is:

```text
single known page structured fields
```

Prompt:

```text
Use Firecrawl on this exact product page and return only structured JSON fields name, price, and
availability: https://example.com/product/123
```

Expected next tool:

```text
firecrawl_scrape
```

Forbidden next tool:

```text
firecrawl_extract
```

## Live Result

Full Anthropic prompt-JSON result:

- Legacy: 11/12.
- Tuned: 12/12.
- Legacy miss: chose `firecrawl_extract` for one exact product URL.
- Tuned pass: chose `firecrawl_scrape` for that task.

Cross-provider adversarial single-case result:

- Anthropic native tools: legacy failed, tuned passed.
- Anthropic prompt JSON: legacy failed, tuned passed.
- OpenAI native tools: legacy failed, tuned passed.
- OpenAI prompt JSON: legacy failed, tuned passed.
- Gemini native tools: legacy failed, tuned passed.
- Gemini prompt JSON: legacy failed, tuned passed.

## Interpretation

This is not a broad claim that Firecrawl needs a rewrite. The current Firecrawl server already
contains much stronger boundary language than the legacy descriptions. The useful claim is narrower:
when a catalog still tells agents to use `extract` for structured data without carving out the
single-known-page case, models across providers route that task to the wrong next tool. Adding the
single-page JSON scrape boundary fixes it.

## Recommended Description Pattern

For `firecrawl_scrape`:

```text
Use when the exact page URL is known and the task needs that page's content, metadata, screenshot,
branding, or structured fields. For one known page plus specific fields, choose scrape with JSON
format rather than extract.
```

For `firecrawl_extract`:

```text
Use when the user asks for specific fields across several pages or a structured extraction job
broader than one known page. Avoid for one known URL. Use firecrawl_scrape with JSON format.
```

## Verifier Lesson

The first verifier was too strict because it required the nested `formats` argument to contain a
literal `json` string. The model chose the right tool but used a different nested shape. The eval now
checks the tool and URL, not incidental JSON-format spelling. That keeps the test focused on tool
selection instead of overfitting one argument shape.

</details>
