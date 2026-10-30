# Observation Ledger (Active & Parked Signals)

> Raw signals: corrections, tool failures, mechanical catches, verify fails, rule violations.

## Observation 115: Verify gate failure: SECURITY - AST_COMMAND_INJECTION: subprocess.run() called with shell=Tr
- **id**: 115
- **fingerprint**: eb7f0d129a20
- **status**: open
- **kind**: violation
- **target**: .agents/scripts/core/accelerators.py
- **rule_id**: VERIFY_GATE_SECURITY
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: AST_COMMAND_INJECTION: subprocess.run() called with shell=True or dynamic shell flag (line 209) | AST_COMMAND_INJECTION: subprocess.run() called with shell=True or dynamic shell flag (line 268)
- **created**: 2026-10-30T21:20:57.582815

## Observation 116: Verify gate failure: SECURITY - AST_SQL_INJECTION: SQL injection risk via dynamic string for
- **id**: 116
- **fingerprint**: 20944ac15cda
- **status**: open
- **kind**: violation
- **target**: .agents/scripts/core/memory.py
- **rule_id**: VERIFY_GATE_SECURITY
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: AST_SQL_INJECTION: SQL injection risk via dynamic string formatting in execute() (CWE-89) (line 592) | AST_SQL_INJECTION: SQL injection risk via dynamic string formatting in execute() (CWE-89) (line 240)
- **created**: 2026-10-30T22:43:20.679987

## Observation 117: Verify gate failure: SECURITY - SECRET_LEAK_GITHUB_TOKEN: Hardcoded secret detected: GITHUB_
- **id**: 117
- **fingerprint**: 79f1892ce045
- **status**: open
- **kind**: violation
- **target**: .agents/scripts/tests/audit_accelerator_benchmarks.py
- **rule_id**: VERIFY_GATE_SECURITY
- **siblings_checked**: true
- **scope**: project
- **evidence**: SECRET_LEAK_GITHUB_TOKEN: Hardcoded secret detected: GITHUB_TOKEN (line 288)
- **created**: 2026-10-30T23:11:42.820884

## Observation 118: Verify gate failure: SECURITY - SECRET_LEAK_GENERIC_SECRET: Hardcoded secret detected: GENER
- **id**: 118
- **fingerprint**: 931cdaea2106
- **status**: open
- **kind**: violation
- **target**: .agents/scripts/tests/audit_accelerator_benchmarks.py
- **rule_id**: VERIFY_GATE_SECURITY
- **siblings_checked**: true
- **scope**: project
- **evidence**: SECRET_LEAK_GENERIC_SECRET: Hardcoded secret detected: GENERIC_SECRET (line 288)
- **created**: 2026-10-30T23:11:42.830054

## Observation 119: Tool failure in orion:verify (Exit Code 1)
- **id**: 119
- **fingerprint**: 9768e55d0d77
- **status**: open
- **kind**: violation
- **target**: orion:verify
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: Args: {'args': [], 'exit_code': 1}
- **created**: 2026-10-30T23:11:42.881295

## Observation 120: Verify gate failure: PROTOCOL - Exceeds Antigravity 24,000-byte per-file rule limit (24705 b
- **id**: 120
- **fingerprint**: 9eb0bca8e646
- **status**: open
- **kind**: violation
- **target**: GEMINI.md
- **rule_id**: VERIFY_GATE_PROTOCOL
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: Exceeds Antigravity 24,000-byte per-file rule limit (24705 bytes)
- **created**: 2026-10-30T23:31:10.520331

## Observation 121: Tool failure in orion:brain (Exit Code 1)
- **id**: 121
- **fingerprint**: ac8b27d94c6b
- **status**: open
- **kind**: violation
- **target**: orion:brain
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['handoff', 'resolve', '--help'], 'exit_code': 1}
- **created**: 2026-10-31T00:58:30.658898

## Observation 122: DNA compliance score regression (100 -> 64)
- **id**: 122
- **fingerprint**: 779314f4c4b2
- **status**: open
- **kind**: improve
- **target**: core/dna.py
- **rule_id**: DNA_COMPLIANCE_REGRESSION
- **siblings_checked**: true
- **scope**: project
- **evidence**: Latest snapshot score 64 lower than previous 100
- **created**: 2026-10-31T01:02:41.815647

## Observation 123: Propose skill for frequent action sequence: read_file -> replace_file_content -> run_shell_command
- **id**: 123
- **fingerprint**: f48507d408c3
- **status**: open
- **kind**: habit
- **target**: skills
- **rule_id**: OPERATOR_HABIT_SKILL_PROPOSAL
- **siblings_checked**: true
- **scope**: project
- **evidence**: Action sequence [read_file -> replace_file_content -> run_shell_command] repeated 3 times
- **created**: 2026-10-31T01:02:42.008102

## Observation 124: Tool failure in orion:scan (Exit Code 1)
- **id**: 124
- **fingerprint**: 9c40799095d4
- **status**: open
- **kind**: violation
- **target**: orion:scan
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['audit-validate', '.agents/skills/integrity-sentinel/references/report-schema.json'], 'exit_code': 1}
- **created**: 2026-10-31T01:04:30.570779

## Observation 125: Verify gate failure: HYGIENE - Bytecode cache leak detected: scripts/core/__pycache__
- **id**: 125
- **fingerprint**: c82886bbaef7
- **status**: open
- **kind**: violation
- **target**: scripts/core/__pycache__
- **rule_id**: VERIFY_GATE_HYGIENE
- **siblings_checked**: true
- **scope**: project
- **evidence**: Bytecode cache leak detected: scripts/core/__pycache__
- **created**: 2026-10-31T01:34:08.083248

## Observation 126: Verify gate failure: HYGIENE - Bytecode cache leak detected: scripts/core/__pycache__/__ini
- **id**: 126
- **fingerprint**: c0a764557842
- **status**: open
- **kind**: violation
- **target**: scripts/core/__pycache__/__init__.cpython-314.pyc
- **rule_id**: VERIFY_GATE_HYGIENE
- **siblings_checked**: true
- **scope**: project
- **evidence**: Bytecode cache leak detected: scripts/core/__pycache__/__init__.cpython-314.pyc
- **created**: 2026-10-31T01:34:08.096795

## Observation 127: Tool failure in orion:verify_agents (Exit Code 1)
- **id**: 127
- **fingerprint**: b123583fa637
- **status**: open
- **kind**: violation
- **target**: orion:verify_agents
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: Args: {'args': [], 'exit_code': 1}
- **created**: 2026-10-31T01:34:08.142365

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
