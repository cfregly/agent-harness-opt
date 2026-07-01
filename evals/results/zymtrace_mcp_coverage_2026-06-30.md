# Matrix Coverage: zymtrace mcp tool-selection matrix

Passed: yes
Tools: 25
Cases: 34
Profiles: 3
Instruction variants: 2
Expected tool coverage: 1.000
Forbidden tool coverage: 1.000
Cases with argument checks: 33
Boundary pairs: 85
Cases with check_family: 34
Case expectation gaps: 0
Identity gaps: 0
Value bars: 0
Value-bar gaps: 0
Required check-family coverage: 1.000
Variant surface parity: 1.000

## Gaps

- Never expected: none
- Never forbidden: none
- Case expectation gaps: none
- Expected without argument checks: none
- Duplicate tool names: none
- Identity gaps: none
- Missing quality checks: none
- Missing required check families: none
- Variant surface mismatches: none
- Source tool count mismatch: none
- Cases without forbidden tools: none
- Cases without check_family: none
- Unknown expected tools: none
- Unknown forbidden tools: none
- Value-bar gaps: none

## Tool Coverage

| Tool | Expected Cases | Forbidden Cases | Argument Cases | Quality Checks |
|---|---:|---:|---:|---|
| flamegraph | 1 | 11 | 1 | yes |
| get_date_time | 1 | 1 | 0 | yes |
| hot_traces | 5 | 9 | 5 | yes |
| project_events_raw | 2 | 8 | 2 | yes |
| project_flamegraph_json | 1 | 2 | 1 | yes |
| project_metrics_activity_aggr | 3 | 1 | 3 | yes |
| project_metrics_query | 1 | 5 | 1 | yes |
| projects_events_aggregate | 1 | 3 | 1 | yes |
| projects_events_aggregate_host_metadata | 1 | 2 | 1 | yes |
| projects_events_aggregate_top_field_values | 1 | 2 | 1 | yes |
| projects_search | 1 | 2 | 1 | yes |
| projects_stats_aggregate_top_architectures | 1 | 2 | 1 | yes |
| projects_stats_aggregate_top_clusters | 1 | 1 | 1 | yes |
| projects_stats_aggregate_top_containers | 1 | 4 | 1 | yes |
| projects_stats_aggregate_top_deployments | 1 | 2 | 1 | yes |
| projects_stats_aggregate_top_hosts | 1 | 3 | 1 | yes |
| projects_stats_aggregate_top_main_exes | 1 | 2 | 1 | yes |
| projects_stats_aggregate_top_namespaces | 1 | 3 | 1 | yes |
| projects_stats_aggregate_top_pods | 1 | 4 | 1 | yes |
| projects_stats_aggregate_top_script_names | 1 | 2 | 1 | yes |
| projects_stats_aggregate_top_thread_names | 1 | 1 | 1 | yes |
| projects_stats_aggregate_top_user_tags | 1 | 1 | 1 | yes |
| recommendations | 1 | 3 | 1 | yes |
| topentities | 2 | 6 | 2 | yes |
| topfunctions | 2 | 25 | 2 | yes |

## Check Families

| Family | Cases |
|---|---:|
| bounded_discovery | 1 |
| default_project | 2 |
| dimension_ranking | 11 |
| drilldown_boundary | 1 |
| entity_ranking | 1 |
| error_recovery | 1 |
| event_aggregate | 1 |
| filter_discovery | 1 |
| gpu_workflow | 2 |
| host_metadata | 1 |
| metric_discovery | 1 |
| metric_query | 1 |
| output_budget | 1 |
| project_selection | 1 |
| rank_first | 2 |
| raw_payload | 1 |
| recommendation | 1 |
| resource_vs_tool | 3 |
| time_window | 1 |
