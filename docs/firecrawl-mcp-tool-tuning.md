# Firecrawl MCP Tool Tuning

This audit is the first public MCP sweep result in this repo that clears the
adversarially-confirmed to add value bar.

## Boundary

The ambiguous boundary is:

- `firecrawl_scrape`: one known URL, including focused structured fields via a JSON format.
- `firecrawl_extract`: structured extraction across multiple pages or broader URL sets using the
  extraction layer.

Older Firecrawl wording said `firecrawl_scrape` was not recommended for structured data and to use
`firecrawl_extract` instead. Current guidance is more nuanced: use `scrape` with JSON format for one
known page, and reserve `extract` for multi-page or broader structured extraction jobs.

## Matrix

The matrix lives at:

```text
evals/model_matrix/firecrawl_mcp_tool_selection.json
```

It compares:

- `legacy_firecrawl_mcp`: older/legacy-style descriptions.
- `tuned_firecrawl_mcp_boundaries`: boundary descriptions that match current Firecrawl guidance.

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
