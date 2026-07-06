# Demo recipe for the checked-in public GIF.
# Regenerate from the repo root with:
# python scripts/render_demo_gif.py --out demo.gif --mp4-out demo.mp4
Output demo.gif
Output demo.mp4

Set Width 1200
Set Height 720

Run "python -m claude_agent_harness_opt matrix-coverage evals/model_matrix/supabase_mcp_database_tool_selection.json --strict --markdown"
Run "python scripts/optimize_mcp.py supabase --markdown --cases 'ddl create table uses migration,ddl create index uses migration,rls policy uses migration' --providers anthropic,openai,gemini --harnesses prompt_json,native_tools --out /tmp/supabase-demo-optimization.md"
Run "python -c \"print('Supabase live evidence: terse 6/9 -> tuned 9/9'); print('DDL/RLS cases fixed across Anthropic, OpenAI, Gemini, native tools, and prompt JSON'); print('Risk avoided: schema changes bypassing auditable migrations')\""
Run "python scripts/check_finding_packets.py"
Run "python scripts/check_public_links.py"
Run "python scripts/check_human_docs.py"
Run "python -c 'print(\"Supabase PR/evidence bundle: https://github.com/cfregly/agent-harness-opt/tree/main/evals/pr_packets/supabase_mcp_database_tool_tuning_2026-06-25\")'"
