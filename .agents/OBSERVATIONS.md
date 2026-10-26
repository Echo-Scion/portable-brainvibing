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
- **count**: 3
- **evidence**: Args: {'args': ['security', '--target', 'echont'], 'exit_code': 2} | Args: {'args': ['grep', 'taxonomy', '--path'], 'exit_code': 2} | Args: {'args': ['map', '.agents/scripts/commands', '.agents/scripts/core'], 'exit_code': 2}
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
- **count**: 6
- **evidence**: Action sequence [read_file -> replace_file_content -> run_shell_command] repeated 3 times
- **created**: 2026-10-24T15:43:16.432757

## Observation 98: DNA compliance score regression (100 -> 64)
- **id**: 98
- **fingerprint**: 779314f4c4b2
- **status**: open
- **kind**: improve
- **target**: core/dna.py
- **rule_id**: DNA_COMPLIANCE_REGRESSION
- **siblings_checked**: true
- **scope**: project
- **count**: 4
- **evidence**: Latest snapshot score 64 lower than previous 100
- **created**: 2026-10-25T16:18:02.526132

## Observation 99: Tool failure in orion:orion_ops (Exit Code 1)
- **id**: 99
- **fingerprint**: 713f0f7a5eb4
- **status**: open
- **kind**: violation
- **target**: orion:orion_ops
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['orion_ops', 'init'], 'exit_code': 1}
- **created**: 2026-10-26T17:02:03.542012

## Observation 100: Verify gate failure: SECURITY - AST_DESTRUCTIVE_FS: Recursive directory deletion via shutil.
- **id**: 100
- **fingerprint**: c8a30b094b3a
- **status**: open
- **kind**: violation
- **target**: .agents/scripts/tests/test_stack_detection.py
- **rule_id**: VERIFY_GATE_SECURITY
- **siblings_checked**: true
- **scope**: project
- **evidence**: AST_DESTRUCTIVE_FS: Recursive directory deletion via shutil.rmtree() (line 24)
- **created**: 2026-10-27T01:15:16.698315

## Observation 101: Tool failure in orion:verify_agents (Exit Code 1)
- **id**: 101
- **fingerprint**: b123583fa637
- **status**: open
- **kind**: violation
- **target**: orion:verify_agents
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: Args: {'args': [], 'exit_code': 1}
- **created**: 2026-10-27T01:15:16.726064

## Observation 102: Verify gate failure: HYGIENE - Hardcoded user machine path found in .agents/docs/07-python_
- **id**: 102
- **fingerprint**: 9f183f3da0a2
- **status**: open
- **kind**: violation
- **target**: .agents/docs/07-python_scripts___scripts.md
- **rule_id**: VERIFY_GATE_HYGIENE
- **siblings_checked**: true
- **scope**: project
- **evidence**: Hardcoded user machine path found in .agents/docs/07-python_scripts___scripts.md
- **created**: 2026-10-27T01:48:43.277339

## Observation 103: Verify gate failure: HYGIENE - Hardcoded user machine path found in .agents/docs/09-darwini
- **id**: 103
- **fingerprint**: 8af26ffafada
- **status**: open
- **kind**: violation
- **target**: .agents/docs/09-darwinian_evolution_lifecycle.md
- **rule_id**: VERIFY_GATE_HYGIENE
- **siblings_checked**: true
- **scope**: project
- **evidence**: Hardcoded user machine path found in .agents/docs/09-darwinian_evolution_lifecycle.md
- **created**: 2026-10-27T01:48:43.282210

## Observation 104: Tool failure in orion:compact (Exit Code 1)
- **id**: 104
- **fingerprint**: 4106edcf1c46
- **status**: open
- **kind**: violation
- **target**: orion:compact
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['compact', '--text', "It is not just a tool, it's a game changer! Serves as a gateway. Let that sink in."], 'exit_code': 1}
- **created**: 2026-10-27T03:28:09.845977
