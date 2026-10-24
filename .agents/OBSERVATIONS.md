# Observation Ledger (Active & Parked Signals)

> Raw signals: corrections, tool failures, mechanical catches, verify fails, rule violations.

## Observation 80: Propose skill for frequent action sequence: orion:evolve -> orion:foundation -> orion:brain
- **id**: 80
- **fingerprint**: 25a5516b06d6
- **status**: open
- **kind**: habit
- **target**: skills
- **rule_id**: OPERATOR_HABIT_SKILL_PROPOSAL
- **siblings_checked**: true
- **scope**: project
- **evidence**: Action sequence [orion:evolve -> orion:foundation -> orion:brain] repeated 3 times
- **created**: 2026-10-24T09:23:10.917668

## Observation 81: Tool failure in orion:scan (Exit Code 2)
- **id**: 81
- **fingerprint**: cba6719a03b4
- **status**: open
- **kind**: violation
- **target**: orion:scan
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['security', '--target', 'echont'], 'exit_code': 2}
- **created**: 2026-10-24T09:25:31.419249

## Observation 86: Tool failure in orion:reflexion (Exit Code 1)
- **id**: 86
- **fingerprint**: da98810931f4
- **status**: open
- **kind**: violation
- **target**: orion:reflexion
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['reflexion', 'observe', '--title'], 'exit_code': 1}
- **created**: 2026-10-24T09:39:24.803538

## Observation 92: Tool failure in orion:resolve (Exit Code 2)
- **id**: 92
- **fingerprint**: 75f23c25f60f
- **status**: open
- **kind**: violation
- **target**: orion:resolve
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['resolve', '88', '--status'], 'exit_code': 2}
- **created**: 2026-10-24T13:23:47.248557

## Observation 93: Tool failure in orion:brain (Exit Code 1)
- **id**: 93
- **fingerprint**: ac8b27d94c6b
- **status**: open
- **kind**: violation
- **target**: orion:brain
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['rollover'], 'exit_code': 1}
- **created**: 2026-10-24T14:13:35.042240

## Observation 97: Propose skill for frequent action sequence: read_file -> replace_file_content -> run_shell_command
- **id**: 97
- **fingerprint**: f48507d408c3
- **status**: open
- **kind**: habit
- **target**: skills
- **rule_id**: OPERATOR_HABIT_SKILL_PROPOSAL
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: Action sequence [read_file -> replace_file_content -> run_shell_command] repeated 3 times
- **created**: 2026-10-24T15:43:16.432757
