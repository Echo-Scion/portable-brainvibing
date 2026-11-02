# Observation Ledger (Active & Parked Signals)

> Raw signals: corrections, tool failures, mechanical catches, verify fails, rule violations.

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
- **count**: 4
- **evidence**: Args: {'args': [], 'exit_code': 1}
- **created**: 2026-11-01T19:15:47.310626

## Observation 148: Verify gate failure: LINK - Broken rule reference: @AGENTS.md
- **id**: 148
- **fingerprint**: 26c7bd62450e
- **status**: open
- **kind**: violation
- **target**: ..\GEMINI.md:3
- **rule_id**: VERIFY_GATE_LINK
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: Broken rule reference: @AGENTS.md
- **created**: 2026-11-02T16:29:52.754303

## Observation 149: Verify gate failure: LINK - Broken backticked file reference: `references/goldfish-perso
- **id**: 149
- **fingerprint**: 22394da04434
- **status**: open
- **kind**: violation
- **target**: skills\project-architect\SKILL.md:87
- **rule_id**: VERIFY_GATE_LINK
- **siblings_checked**: true
- **scope**: project
- **evidence**: Broken backticked file reference: `references/goldfish-personas.md`
- **created**: 2026-11-02T17:28:19.609627

## Observation 150: Verify gate failure: GHOST - Ghost skill reference: references/goldfish-personas.md
- **id**: 150
- **fingerprint**: 47b18a86191a
- **status**: open
- **kind**: violation
- **target**: skills\project-architect\SKILL.md
- **rule_id**: VERIFY_GATE_GHOST
- **siblings_checked**: true
- **scope**: project
- **evidence**: Ghost skill reference: references/goldfish-personas.md
- **created**: 2026-11-02T17:28:19.625184

## Observation 151: Verify gate failure: GHOST - Ghost skill reference: references/spec-drift.md
- **id**: 151
- **fingerprint**: 5babb86c81cc
- **status**: open
- **kind**: violation
- **target**: skills\project-architect\SKILL.md
- **rule_id**: VERIFY_GATE_GHOST
- **siblings_checked**: true
- **scope**: project
- **evidence**: Ghost skill reference: references/spec-drift.md
- **created**: 2026-11-02T17:28:19.644335

## Observation 152: Verify gate failure: PROTOCOL - Exceeds Antigravity 24,000-byte per-file rule limit (24122 b
- **id**: 152
- **fingerprint**: d1771bfc37ff
- **status**: open
- **kind**: violation
- **target**: AGENTS.md
- **rule_id**: VERIFY_GATE_PROTOCOL
- **siblings_checked**: true
- **scope**: project
- **evidence**: Exceeds Antigravity 24,000-byte per-file rule limit (24122 bytes)
- **created**: 2026-11-02T17:28:19.658477

## Observation 153: DNA compliance score regression (100 -> 64)
- **id**: 153
- **fingerprint**: 779314f4c4b2
- **status**: open
- **kind**: improve
- **target**: core/dna.py
- **rule_id**: DNA_COMPLIANCE_REGRESSION
- **siblings_checked**: true
- **scope**: project
- **evidence**: Latest snapshot score 64 lower than previous 100
- **created**: 2026-11-02T19:10:21.155785

## Observation 154: Propose skill for frequent action sequence: read_file -> replace_file_content -> run_shell_command
- **id**: 154
- **fingerprint**: f48507d408c3
- **status**: open
- **kind**: habit
- **target**: skills
- **rule_id**: OPERATOR_HABIT_SKILL_PROPOSAL
- **siblings_checked**: true
- **scope**: project
- **evidence**: Action sequence [read_file -> replace_file_content -> run_shell_command] repeated 3 times
- **created**: 2026-11-02T19:10:21.513522

## Observation 155: Verify gate failure: GHOST - Invalid orion CLI subcommand: 'design'
- **id**: 155
- **fingerprint**: 0bc2142dbb9f
- **status**: open
- **kind**: violation
- **target**: ..\README.md:82
- **rule_id**: VERIFY_GATE_GHOST
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: Invalid orion CLI subcommand: 'design'
- **created**: 2026-11-02T19:47:13.506914

## Observation 156: Verify gate failure: GHOST - Ghost script reference: foo.py
- **id**: 156
- **fingerprint**: 9bfa2b2774e1
- **status**: open
- **kind**: violation
- **target**: templates\CHANGELOG.template.md
- **rule_id**: VERIFY_GATE_GHOST
- **siblings_checked**: true
- **scope**: project
- **evidence**: Ghost script reference: foo.py
- **created**: 2026-11-02T21:21:00.627400
