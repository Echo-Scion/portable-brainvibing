# Observation Ledger (Active & Parked Signals)

> Raw signals: corrections, tool failures, mechanical catches, verify fails, rule violations.

## Observation 132: Tool failure in orion:resolve (Exit Code 2)
- **id**: 132
- **fingerprint**: 75f23c25f60f
- **status**: open
- **kind**: violation
- **target**: orion:resolve
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **count**: 4
- **evidence**: Args: {'args': ['resolve', '128', 'Resolved by adding upgrade to explicit subcommand forwarding in orion.py'], 'exit_code': 2} | Args: {'args': ['resolve', '129', 'Resolved by importing Path in cmd_upgrade'], 'exit_code': 2} | Args: {'args': ['resolve', '130', 'Resolved by adding explicit encoding to subprocess.run'], 'exit_code': 2} | Args: {'args': ['resolve', '131', 'Resolved by implementing safe dir removal without shutil.rmtree'], 'exit_code': 2}
- **created**: 2026-10-31T02:46:20.310590

## Observation 133: Verify gate failure: LINK - Broken backticked file reference: `rules/core-guardrails.md`
- **id**: 133
- **fingerprint**: 52dd191506a4
- **status**: open
- **kind**: violation
- **target**: skills\internal\references\knowledge-sync.md:32
- **rule_id**: VERIFY_GATE_LINK
- **siblings_checked**: true
- **scope**: project
- **count**: 5
- **evidence**: Broken backticked file reference: `rules/core-guardrails.md`
- **created**: 2026-10-31T03:58:21.001144

## Observation 134: Verify gate failure: GHOST - Ghost path reference: `rules/core-guardrails.md`
- **id**: 134
- **fingerprint**: fbf10a9a71df
- **status**: open
- **kind**: violation
- **target**: skills\internal\references\knowledge-sync.md:32
- **rule_id**: VERIFY_GATE_GHOST
- **siblings_checked**: true
- **scope**: project
- **evidence**: Ghost path reference: `rules/core-guardrails.md`
- **created**: 2026-10-31T03:58:21.010378

## Observation 135: Verify gate failure: SECURITY - AST_DANGEROUS_IMPORT: Import of high-risk module: 'ctypes' (
- **id**: 135
- **fingerprint**: 819e4d24b6d9
- **status**: open
- **kind**: violation
- **target**: .agents/hooks/rtk-pre-tool.py
- **rule_id**: VERIFY_GATE_SECURITY
- **siblings_checked**: true
- **scope**: project
- **evidence**: AST_DANGEROUS_IMPORT: Import of high-risk module: 'ctypes' (line 19)
- **created**: 2026-10-31T17:02:01.721193

## Observation 136: Tool failure in orion:sync-ai (Exit Code 2)
- **id**: 136
- **fingerprint**: c66efc7fcf17
- **status**: open
- **kind**: violation
- **target**: orion:sync-ai
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['sync-ai'], 'exit_code': 2}
- **created**: 2026-10-31T22:05:55.115084

## Observation 137: DNA compliance score regression (100 -> 64)
- **id**: 137
- **fingerprint**: 779314f4c4b2
- **status**: open
- **kind**: improve
- **target**: core/dna.py
- **rule_id**: DNA_COMPLIANCE_REGRESSION
- **siblings_checked**: true
- **scope**: project
- **count**: 3
- **evidence**: Latest snapshot score 64 lower than previous 100
- **created**: 2026-11-01T16:21:50.048959

## Observation 138: Tool failure in orion:brain (Exit Code 1)
- **id**: 138
- **fingerprint**: ac8b27d94c6b
- **status**: open
- **kind**: violation
- **target**: orion:brain
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['handoff', 'resolve', '--help'], 'exit_code': 1}
- **created**: 2026-11-01T16:54:45.788484

## Observation 139: Tool failure in orion:observe (Exit Code 2)
- **id**: 139
- **fingerprint**: 4f263a81642c
- **status**: open
- **kind**: violation
- **target**: orion:observe
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['observe', 'status'], 'exit_code': 2}
- **created**: 2026-11-01T16:56:46.241593

## Observation 140: Verify gate failure: HYGIENE - Hardcoded user machine path found in CHANGELOG.md
- **id**: 140
- **fingerprint**: 67c9e54f1536
- **status**: open
- **kind**: violation
- **target**: CHANGELOG.md
- **rule_id**: VERIFY_GATE_HYGIENE
- **siblings_checked**: true
- **scope**: project
- **evidence**: Hardcoded user machine path found in CHANGELOG.md
- **created**: 2026-11-01T17:25:48.589584

## Observation 141: Tool failure in orion:verify (Exit Code 1)
- **id**: 141
- **fingerprint**: 9768e55d0d77
- **status**: open
- **kind**: violation
- **target**: orion:verify
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': [], 'exit_code': 1}
- **created**: 2026-11-01T17:25:48.633011

## Observation 142: Propose skill for frequent action sequence: read_file -> replace_file_content -> run_shell_command
- **id**: 142
- **fingerprint**: f48507d408c3
- **status**: open
- **kind**: habit
- **target**: skills
- **rule_id**: OPERATOR_HABIT_SKILL_PROPOSAL
- **siblings_checked**: true
- **scope**: project
- **evidence**: Action sequence [read_file -> replace_file_content -> run_shell_command] repeated 3 times
- **created**: 2026-11-01T18:39:48.384805

## Observation 143: Tool failure in orion:scan (Exit Code 1)
- **id**: 143
- **fingerprint**: 9c40799095d4
- **status**: open
- **kind**: violation
- **target**: orion:scan
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **count**: 3
- **evidence**: Args: {'args': ['security', 'C:\\Users\\USER\\AndroidStudioProjects\\_foundation'], 'exit_code': 1} | Args: {'args': ['prose', 'README.md'], 'exit_code': 1} | Args: {'args': ['prose', 'README.md', 'CHANGELOG.md'], 'exit_code': 1}
- **created**: 2026-11-01T19:15:37.358293

## Observation 144: Tool failure in orion:push (Exit Code 1)
- **id**: 144
- **fingerprint**: 6f603408238c
- **status**: open
- **kind**: violation
- **target**: orion:push
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['push', '--dry-run', '--skip-tests'], 'exit_code': 1}
- **created**: 2026-11-01T19:15:37.613745

## Observation 145: Verify gate failure: HYGIENE - subprocess.run() text mode missing explicit encoding='utf-8'
- **id**: 145
- **fingerprint**: 8790cc2fd2a5
- **status**: open
- **kind**: violation
- **target**: scripts/commands/foundation.py
- **rule_id**: VERIFY_GATE_HYGIENE
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: subprocess.run() text mode missing explicit encoding='utf-8' (scripts/commands/foundation.py:3729)
- **created**: 2026-11-01T19:15:47.240763

## Observation 146: Verify gate failure: HYGIENE - open() text mode missing explicit encoding='utf-8' (scripts/
- **id**: 146
- **fingerprint**: c5cc46fbfa26
- **status**: open
- **kind**: violation
- **target**: scripts/tests/test_project_push.py
- **rule_id**: VERIFY_GATE_HYGIENE
- **siblings_checked**: true
- **scope**: project
- **count**: 4
- **evidence**: open() text mode missing explicit encoding='utf-8' (scripts/tests/test_project_push.py:91) | open() text mode missing explicit encoding='utf-8' (scripts/tests/test_project_push.py:74)
- **created**: 2026-11-01T19:15:47.248578

## Observation 147: Tool failure in orion:verify_agents (Exit Code 1)
- **id**: 147
- **fingerprint**: b123583fa637
- **status**: open
- **kind**: violation
- **target**: orion:verify_agents
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: Args: {'args': [], 'exit_code': 1}
- **created**: 2026-11-01T19:15:47.310626
