# Starter Cross-Cutting Principles (Seed Set for .agents)

Load triggers: starter-set reconciliation due, reviewing cross-domain agent rules, or auditing generalizable invariants.

This file is an optional seed: a curated set of 29 generic methodology principles, accumulated over long runs of the observation loop and stripped of project-specific provenance.
The live authority in `.agents` comes from the project's own evidence trail (`.agents/OBSERVATIONS.md` and `.agents/LEARNINGS.md`), so rules here are imported when supported by local project evidence or explicitly adopted.

---

## Contents

- 1. Open-source skills must include an open-source licence
- 2. Open-source skills must include author attribution and a feedback pathway
- 3. Skills with rules must include a pre-flight verification step
- 4. Open-source skills must not contain client-identifying information
- 5. Open-source skills must use tool-agnostic language, with concrete examples first
- 6. Skills that generate structured output must be grounded in multiple real examples
- 7. Subagents must have complete inputs and verified outputs
- 8. Graceful tool-failure recovery
- 9. Match interaction modality to conversation energy
- 10. Small actionable sets are presented inline AND saved to file
- 11. Skills require pruning, not just growth
- 12. Use canonical identifiers from source data, never reconstruct from derived fields
- 13. Skills that read or write workspace files must maintain a reference index
- 14. Scheduled tasks invoke skills; they do not reimplement them
- 15. Scheduled task prompts are lightweight orchestrators — intelligence lives in skills
- 16. Interrupted operations are partial operations — verify state before retrying
- 17. Never suggest manual typing of technical content as a workaround
- 18. Browser automation is a costly last resort
- 19. Skills recommending API access must note network-sandbox implications
- 20. Skills contain only behaviour-changing content
- 21. Use agent-agnostic language in open-source skills
- 22. Verifying current vendor guidance requires a dated changelog check, not just the docs page
- 23. Never aggregate across structurally different segments, or against an unmeasured baseline
- 24. Fetch the instance before describing it
- 25. One verified reason beats two, where the second is unchecked
- 26. A companion skill must declare its coverage boundary
- 27. Every skill ships as a bundle and is structured for progressive disclosure, regardless of size
- 28. Absence is never established by a summarising instrument
- 29. A skill holds method; dated values live in a workspace file the skill names

---

### 1. Open-source skills must include an open-source licence
**Applies to:** all open-source skills
**Requirement:** Include a recognised open-source licence statement in the skill preamble and a corresponding `LICENSE` (or `LICENSE.txt`) file in the skill directory. Any commonly recognised licence is acceptable — CC BY 4.0 for prose-heavy skills, MIT or Apache 2.0 for code-heavy skills, CC BY-SA or the GPL family for stronger copyleft.

### 2. Open-source skills must include author attribution and a feedback pathway
**Applies to:** all open-source skills
**Requirement:** Carry author and licence in the frontmatter (`license:` plus `metadata:` with author and source) and repeat them in a one-line footer at the end of the skill, which survives tools that strip frontmatter. Open the body with what the skill does, not credits. Give the canonical source and a feedback pathway as an offer to draft a report.

### 3. Skills with rules must include a pre-flight verification step
**Applies to:** all skills with explicit rules or requirements
**Requirement:** Include a verification step where the agent re-reads the skill's rules and checks its output against them before delivery. Rules that are not enforced mechanically or verified against assertions are mere suggestions.

### 4. Open-source skills must not contain client-identifying information
**Applies to:** all open-source skills and foundation canons
**Requirement:** No client names, project URLs, domain names, or proprietary details anywhere in the skill, its references, or its examples. Enforce at authoring time, at observation-logging time, and again at publication — the log and the commit message are artefacts too.

### 5. Open-source skills must use tool-agnostic language, with concrete examples first
**Applies to:** all open-source skills
**Requirement:** Reference capabilities (browser access, file system access, web search, a scheduler) rather than hard-coding a dependency on one vendor product. Name the concrete tool for the primary environment as an example, then give the generic fallback: "In [environment], use `[tool]`. Elsewhere, use the available equivalent."

### 6. Skills that generate structured output must be grounded in multiple real examples
**Applies to:** all skills that produce structured output (configs, markup, code templates, data formats)
**Requirement:** Inform the skill with several real-world examples of the target format, never a single instance — one example creates blind spots around edge cases, advanced features, and format variations. Where the resulting specification is too detailed for the skill body, put it in a reference file and point to it.

### 7. Subagents must have complete inputs and verified outputs
**Applies to:** all skills that delegate content generation to subagents
**Requirement:** Use subagents for speed and token isolation, but never let them guess at data values. Safe delegations: validation, formatting checks, cross-reference checks — anything where every required input can be passed in the brief. Unsafe unless guarded: anything requiring live data. For data-bearing tasks, the parent gathers raw data first and passes it complete. A claim without verifiable evidence returned from a subagent is a claim to verify, not to relay.

### 8. Graceful tool-failure recovery
**Applies to:** all skills that use interactive tools or subprocesses
**Requirement:** When a tool interaction or execution fails, recover conversationally without exposing raw internal error states to the user. Rephrase in plain text and continue; do not assume the user dismissed the interaction.

### 9. Match interaction modality to conversation energy
**Applies to:** all skills that gather user input
**Requirement:** Use structured tools (question widgets, interactive forms) for structured intake at the start of tasks. During free-flowing dialogue, prefer plain-text questions. Do not downgrade a rich conversation to multiple choice.

### 10. Small actionable sets are presented inline AND saved to file
**Applies to:** all skills that produce deliverable results
**Requirement:** When the result is a small set of actionable items (roughly 25 or fewer links, tasks, or similar), present it inline in the conversation AND save it to a file — the file is the persistent record, the inline list serves the immediate workflow. For larger sets the file is primary and a summary is shown inline.

### 11. Skills require pruning, not just growth
**Applies to:** all skills
**Requirement:** During every review or temporal pulse, look for content to remove with the same deliberateness as content to add: rules from a single observation that never recurred, sections never consulted, elaborate workflows users consistently shortcut, complexity added "just in case" that never triggers. A skill that only grows eventually becomes too heavy to be useful.

### 12. Use canonical identifiers from source data, never reconstruct from derived fields
**Applies to:** all skills that join, match, or cross-reference data from more than one source
**Requirement:** Always use the canonical identifier from the source system. Never reconstruct an identifier from a derived or transformed field (generating a URL from a name, inferring an id from a slug). Reconstructed identifiers introduce silent false positives that pass casual review and corrupt analysis.

### 13. Skills that read or write workspace files must maintain a reference index
**Applies to:** all skills that depend on, or produce, files in the shared workspace
**Requirement:** Include a "Reference files" section listing key files with a one-line description each, maintained as a living index — added to when files are created, pruned when they are superseded.

### 14. Scheduled tasks invoke skills; they do not reimplement them
**Applies to:** all scheduled tasks that perform a workflow documented in a skill
**Requirement:** A scheduled task's prompt loads the skill and follows its instructions; it does not inline the workflow. The skill stays the single source of truth: improvements flow into the scheduled execution automatically, and methodology remains shareable and versioned.

### 15. Scheduled task prompts are lightweight orchestrators — intelligence lives in skills
**Applies to:** all scheduled tasks
**Requirement:** Task prompts carry no domain knowledge, source lists, output formats, or filtering criteria; all of that belongs in a skill the task invokes. Pattern: task prompt = "Load skill X, then follow its instructions."

### 16. Interrupted operations are partial operations — verify state before retrying
**Applies to:** all skills that perform bulk data operations or multi-step mutations
**Requirement:** When an operation is interrupted, times out, or fails partway, assume partial success, not total failure. Before retrying by the same or another method, verify current state — bulk inserts, file operations, multi-step workflows. Pattern: interrupt -> verify state -> adjust remaining work -> proceed. Never assume a clean slate after a failure.

### 17. Never suggest manual typing of technical content as a workaround
**Applies to:** all skills and all conversational interactions
**Requirement:** When a tool-based workflow breaks (formatting, paste failures, encoding), never suggest that the user manually type or transcribe code, markup, structured data, or technical content — regardless of length. Find another machine-assisted route: a different file format, a different delivery mechanism, or a native tool.

### 18. Browser automation is a costly last resort
**Applies to:** all skills that use or recommend browser automation
**Requirement:** Browser tool payloads compound token consumption rapidly. Any skill that uses them must document the cost, offer non-browser alternatives where they exist, position the non-browser path as default when equally effective, and escalate strictly: fetch/search tools first, browser only after those fail on a specific source.

### 19. Skills recommending API access must note network-sandbox implications
**Applies to:** all skills that recommend direct access to a third-party API
**Requirement:** Note that users in sandboxed environments (desktop agents, corporate proxies) may need to allowlist the API's domain in their network settings and restart the application before the call succeeds.

### 20. Skills contain only behaviour-changing content
**Applies to:** all skills, open-source and internal
**Requirement:** Keep only content that changes the agent's behaviour at execution time. Changelogs, version notes, history sections, credits, self-narrating prose, and maintainer-facing context belong in a supporting document or commit history — not in the skill core. The test: would removing this line change how the agent behaves?

### 21. Use agent-agnostic language in open-source skills
**Applies to:** all open-source skills
**Requirement:** Refer to the executing AI as "the agent" rather than by a vendor's model name, except where the reference is genuinely specific to that vendor (an app, CLI, config file naming convention, or vendor-specific API).

### 22. Verifying current vendor guidance requires a dated changelog check, not just the docs page
**Applies to:** all skills that verify or assert a third-party platform's current guidance
**Requirement:** When confirming what a vendor currently recommends, supports, or requires, check the vendor's dated changelog or updates page — not only the documentation page. Fetched docs pages may be cached or stale; the changelog is dated and authoritative.

### 23. Never aggregate across structurally different segments, or against an unmeasured baseline
**Applies to:** all skills that report metrics summed, averaged, or ranked over multiple segments, and all skills that attribute a failing check to a change
**Requirement:** Before aggregating, check whether segments are structurally comparable — same instrument, same population size, same denominator behaviour. If not, report per segment first. For changes over time: a check that fails after a change is attributed to the change only once the baseline is measured on the untouched commit first.

### 24. Fetch the instance before describing it
**Applies to:** all skills that describe, classify, or verify a specific artefact
**Requirement:** Before asserting what a specific artefact is, obtain the artefact itself rather than reasoning from a signal that correlates with it. Surface patterns are evidence about an artefact and get substituted for it because they are already in hand while fetching costs a call. Fetch the concrete instance.

### 25. One verified reason beats two, where the second is unchecked
**Applies to:** all skills that produce recommendations, advice, arguments, or justifications
**Requirement:** Every supporting reason attached to a recommendation must clear the same evidence bar as the recommendation itself. When a single justification feels thin, state it more precisely rather than reaching for an unchecked second reason. A wrong supporting reason transfers its unreliability to the sound claim beside it.

### 26. A companion skill must declare its coverage boundary
**Applies to:** all skills that document an external surface (a tool, MCP server, API, platform)
**Requirement:** State near the top which parts of the documented surface the skill covers and which it does not. The agent reads silence as non-existence rather than partiality; naming gaps explicitly turns blind spots into questions the agent knows to investigate.

### 27. Every skill ships as a bundle and is structured for progressive disclosure, regardless of size
**Applies to:** all skills, open-source and internal
**Requirement:** A skill is a directory delivered as one bundle. Its structure follows progressive disclosure: `SKILL.md` carries the mental model, rules changing behaviour on every invocation, and a pointer list with explicit load triggers. Deep inventories, recipes, and per-variant details live in `references/`.

### 28. Absence is never established by a summarising instrument
**Applies to:** all skills that make claims about the contents of an artefact
**Requirement:** No statement of the form "X is not in Y" may rest on an instrument that summarises, samples, renders or answers a question about Y. Presence can be established by a summariser; absence cannot, because "the thing is absent" and "the instrument did not look" produce identical output. Absence requires checking the raw artefact with a literal match.

### 29. A skill holds method; dated values live in a workspace file the skill names
**Applies to:** all skills, open-source and internal
**Requirement:** A skill holds method, rules and workflow — what remains true over time. Anything with a date or a current value (goals, figures, rates, schedules, client and source mappings, logs) lives in a workspace file the skill names. The skill is the single owner of the method; the file is the single owner of the values.
