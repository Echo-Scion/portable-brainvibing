# Observation Ledger (Active & Parked Signals)

> Raw signals: corrections, tool failures, mechanical catches, verify fails, rule violations.

## Observation 153: DNA compliance score regression (100 -> 64)
- **id**: 153
- **fingerprint**: 779314f4c4b2
- **status**: open
- **kind**: improve
- **target**: core/dna.py
- **rule_id**: DNA_COMPLIANCE_REGRESSION
- **siblings_checked**: true
- **scope**: project
- **count**: 6
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
- **count**: 6
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

## Observation 157: Verify gate failure: SECURITY - REMOTE_BOOTSTRAP: Remote shell script pipe execution (line 4
- **id**: 157
- **fingerprint**: fa0304a541f6
- **status**: open
- **kind**: violation
- **target**: .agents/skills/integrity-sentinel/references/ai_llm_attacks.md
- **rule_id**: VERIFY_GATE_SECURITY
- **siblings_checked**: true
- **scope**: project
- **evidence**: REMOTE_BOOTSTRAP: Remote shell script pipe execution (line 43)
- **created**: 2026-11-03T20:32:17.442339

## Observation 158: Tool failure in orion:brain (Exit Code 1)
- **id**: 158
- **fingerprint**: ac8b27d94c6b
- **status**: open
- **kind**: violation
- **target**: orion:brain
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **count**: 3
- **evidence**: Args: {'args': ['inject_triplets', '.orion/scratch/triplets.json'], 'exit_code': 1} | Args: {'args': ['handoff', 'show', 'handoff_1793805051_1'], 'exit_code': 1}
- **created**: 2026-11-03T20:33:28.032051

## Observation 159: Verify gate failure: GHOST - Ghost skill reference: references/ai_llm_attacks.md
- **id**: 159
- **fingerprint**: 878f8a3ba470
- **status**: open
- **kind**: violation
- **target**: skills\ai-engineer\SKILL.md
- **rule_id**: VERIFY_GATE_GHOST
- **siblings_checked**: true
- **scope**: project
- **evidence**: Ghost skill reference: references/ai_llm_attacks.md
- **created**: 2026-11-03T21:34:20.318169

## Observation 160: Verify gate failure: GHOST - Ghost skill reference: references/skill_inspector.md
- **id**: 160
- **fingerprint**: 870fe6fe974a
- **status**: open
- **kind**: violation
- **target**: skills\ai-engineer\SKILL.md
- **rule_id**: VERIFY_GATE_GHOST
- **siblings_checked**: true
- **scope**: project
- **evidence**: Ghost skill reference: references/skill_inspector.md
- **created**: 2026-11-03T21:34:20.329677

## Observation 161: Verify gate failure: PROTOCOL - Exceeds Antigravity 24,000-byte per-file rule limit (24413 b
- **id**: 161
- **fingerprint**: 8adb57ba082a
- **status**: open
- **kind**: violation
- **target**: AGENTS.md
- **rule_id**: VERIFY_GATE_PROTOCOL
- **siblings_checked**: true
- **scope**: project
- **evidence**: Exceeds Antigravity 24,000-byte per-file rule limit (24413 bytes)
- **created**: 2026-11-03T22:12:59.188199

## Observation 162: Tool failure in orion:foundation (Exit Code 2)
- **id**: 162
- **fingerprint**: 7fe420bdfa99
- **status**: open
- **kind**: violation
- **target**: orion:foundation
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['deploy', '--all'], 'exit_code': 2}
- **created**: 2026-11-03T22:31:52.381997

## Observation 163: Tool failure in orion:decisions (Exit Code 2)
- **id**: 163
- **fingerprint**: 2b8a39441dd8
- **status**: open
- **kind**: violation
- **target**: orion:decisions
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: Args: {'args': ['record', 'C:/Users/USER/.gemini/antigravity/brain/d3b6bedd-fb3f-4079-811d-406912fc6bbb/implementation_plan.md'], 'exit_code': 2} | Args: {'args': ['help'], 'exit_code': 2}
- **created**: 2026-11-04T08:01:55.625135

## Observation 164: Verify gate failure: INDEX_DRIFT - Tier-3 reference file on disk is not registered in AGENTS_IN
- **id**: 164
- **fingerprint**: 4ab53035d4ce
- **status**: open
- **kind**: violation
- **target**: AGENTS_INDEX.md
- **rule_id**: VERIFY_GATE_INDEX_DRIFT
- **siblings_checked**: true
- **scope**: project
- **count**: 584
- **evidence**: Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/rule-empty-pattern-hang-in-cli/references/evidence-eb868b35.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/rule-empty-pattern-hang-in-cli/references/remediation.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/systematic-debugging/references/evidence-4c8cc76e.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/strict-tdd/references/evidence-b7874053.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/systematic-debugging/references/evidence-4ebac5e0.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/systematic-debugging/references/evidence-da2e06cc.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/systematic-debugging/references/evidence-e7dc8d72.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/systematic-debugging/references/evidence-9759f658.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/systematic-debugging/references/evidence-39ddf020.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/systematic-debugging/references/evidence-66a02255.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/systematic-debugging/references/evidence-5b6db56c.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/systematic-debugging/references/evidence-4f5d4096.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/systematic-debugging/references/evidence-0b9cced3.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/systematic-debugging/references/evidence-214770f9.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/strict-tdd/references/evidence-214770f9.md' | Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '.agents/skills/systematic-debugging/references/evidence-32e28aa1.md'
- **created**: 2026-11-04T08:45:09.286945

## Observation 165: Tool failure in orion:verify_agents (Exit Code 1)
- **id**: 165
- **fingerprint**: b123583fa637
- **status**: open
- **kind**: violation
- **target**: orion:verify_agents
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **count**: 11
- **evidence**: Args: {'args': [], 'exit_code': 1}
- **created**: 2026-11-04T08:45:09.336421

## Observation 166: Verify gate failure: HYGIENE - Hardcoded user machine path found in .agents/skills/systemat
- **id**: 166
- **fingerprint**: c118b79974ab
- **status**: open
- **kind**: violation
- **target**: .agents/skills/systematic-debugging/SKILL.md
- **rule_id**: VERIFY_GATE_HYGIENE
- **siblings_checked**: true
- **scope**: project
- **count**: 116
- **evidence**: Hardcoded user machine path found in .agents/skills/systematic-debugging/SKILL.md
- **created**: 2026-11-04T08:48:09.030690

## Observation 167: Verify gate failure: HYGIENE - Hardcoded user machine path found in .agents/skills/strict-t
- **id**: 167
- **fingerprint**: ebe6729700d8
- **status**: open
- **kind**: violation
- **target**: .agents/skills/strict-tdd/SKILL.md
- **rule_id**: VERIFY_GATE_HYGIENE
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: Hardcoded user machine path found in .agents/skills/strict-tdd/SKILL.md
- **created**: 2026-11-04T09:01:29.805224

## Observation 168: Tool failure in orion:setup (Exit Code 1)
- **id**: 168
- **fingerprint**: 0698eef57616
- **status**: open
- **kind**: violation
- **target**: orion:setup
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **evidence**: Args: {'args': ['setup', '--yes', '--target'], 'exit_code': 1}
- **created**: 2026-11-04T19:20:05.629753

## Observation 169: Verify gate failure: GHOST - Invalid orion CLI subcommand: 'debug'
- **id**: 169
- **fingerprint**: 0f8bb7e288e7
- **status**: open
- **kind**: violation
- **target**: skills\systematic-debugging\SKILL.md:2
- **rule_id**: VERIFY_GATE_GHOST
- **siblings_checked**: true
- **scope**: project
- **evidence**: Invalid orion CLI subcommand: 'debug'
- **created**: 2026-11-04T21:33:45.342711

## Observation 170: Verify gate failure: PROTOCOL - Exceeds Antigravity 24,000-byte per-file rule limit (24254 b
- **id**: 170
- **fingerprint**: 1d08a87edca3
- **status**: open
- **kind**: violation
- **target**: AGENTS.md
- **rule_id**: VERIFY_GATE_PROTOCOL
- **siblings_checked**: true
- **scope**: project
- **evidence**: Exceeds Antigravity 24,000-byte per-file rule limit (24254 bytes)
- **created**: 2026-11-05T02:32:34.367976

## Observation 171: Tool failure in orion:scan (Exit Code 1)
- **id**: 171
- **fingerprint**: 9c40799095d4
- **status**: open
- **kind**: violation
- **target**: orion:scan
- **rule_id**: TOOL_EXIT_NONZERO
- **siblings_checked**: true
- **scope**: project
- **count**: 2
- **evidence**: Args: {'args': ['security', '.'], 'exit_code': 1}
- **created**: 2026-11-05T02:33:54.270477
