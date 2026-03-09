---
description: Standards for human-facing documentation and elimination of predictable AI writing patterns.
activation: when drafting documentation, copy, or reviewing prose for authenticity
---

# 🖋️ Prose Authenticity: Anti-Slop Writing & AI Tell Elimination


This standard governs all human-facing documentation, README files, commit messages, PR descriptions, and architectural copy. It ensures writing sounds like an experienced, thoughtful engineer—not an eager, formulaic chatbot.

---

## 1. The 54 Pattern Categories (Taxonomy of AI Tells)

Current language models default to predictable structural habits. Every entry below represents a default tell that must be eliminated:

### A. AI Vocabulary & Lexical Inflation
1. **Tier 1 (Instant Tells)**: *delve, tapestry, testament, pivotal, beacon, undeniably, unwavering, paramount, cornerstone, foster, harness, holistic, paradigm, synergy, streamline*.
2. **Tier 2 (Word Clusters)**: *navigating the complexities, double-edged sword, at the intersection of, play a vital role, testament to the power of*.
3. **Tier 3 (Overused Technical Fillers)**: *robust, comprehensive, seamless, ecosystem, leverage, facilitate, underpin* (when used decoratively rather than strictly technical).
4. **Significance Inflation**: Framing routine mechanics as historic milestones (*"a major milestone in the evolution of", "pivotal turning point", "redefines the landscape"*).
5. **Novelty Inflation**: Claiming ordinary workflows are revolutionary breakthroughs.
6. **"Real/Actual" Inflation**: Unnecessary intensifiers (*"the real power of", "the actual reason why", "what actually happens"*).
7. **Hollow Intensifiers**: *literally, truly, deeply, profoundly, fundamentally, genuinely*.

### B. Structural Telling & Staging Clichés
8. **Binary Contrasts (Not-X-but-Y Formulas)**: Formulaic reversals and reversals designed to create artificial drama (see Section 2).
9. **Negative Listing**: Describing what something is *not* before stating what it *is* (*"Not a tool... Not a script... A revolution"*). State the fact directly.
10. **Dramatic Fragmentation**: Staccato one-line sentence fragments for artificial profundity (*"That's it. That's the real win.", "Full stop.", "Let that sink in."*).
11. **Throat-Clearing Openers**: Preambles that announce the point instead of making it (*"Here's the thing:", "Here's why that matters:", "The uncomfortable truth is"*, *"Let me be clear"*).
12. **Forced Triads**: Grouping adjectives, nouns, or bullet points in rigid sets of three (*"fast, secure, and scalable"*).
13. **Rhetorical Posturing**: Socratic rhetorical questions (*"What if everything you knew was wrong?", "Think about it:", "Can we talk about X?"*).
14. **Launch Clichés**: Startup marketing hooks (*"Meet X, your new favorite...", "Think X meets Y", "Say hello to X"*).
15. **Dramatized Crowd Contrast**: Contrived superiority against an imaginary crowd (*"While everyone else was writing think-pieces, we shipped", "While competitors play catch-up"*).
16. **Fake Casual Props**: Chatbot stage directions and forced informalities (*"*checks notes*", "*shrugs*", "chef's kiss", "(yes, really)", "(and that's okay)"*).
17. **Generic Future Narratives**: Formulaic optimism closers (*"As we look ahead, the future of X is brighter than ever", "Only time will tell, but one thing is certain" *).
18. **Chatbot Leftovers**: *as of my last update, I hope this helps, in summary, to wrap up, let's dive in*.
19. **Em-Dash Overuse**: Forbid overused em-dash characters (`—`) as universal clause connectors. Use standard punctuation (comma, period, colon, parentheses).

---

## 2. Binary Contrast Reversal Formulas (Drop the Setup)

Binary reversals announce insight rather than delivering it. Eliminate the negation and state the assertion directly:

| Formulaic Contrast | Problem | Proper Replacement |
| :--- | :--- | :--- |
| `"Not because X, but because Y."` | Telegraphed reversal | State Y directly: `"Because Y."` |
| `"[X] isn't the problem. [Y] is."` | Formulaic reframe | `"The problem is Y."` |
| `"The answer isn't X. It's Y."` | Predictable pivot | `"The answer is Y."` |
| `"It feels like X. It's actually Y."` | Setup/reveal cliché | `"It is Y."` |
| `"The question isn't X. It's Y."` | Rhetorical misdirection | `"The question is Y."` |
| `"stops being X and starts being Y"` | False transformation arc | `"Becomes Y."` |
| `"isn't just about X, it's about Y"` | Negation crutch | `"It is about Y."` |
| `"not only X, but also Y"` | Additive hedge | State both concisely: `"X and Y."` |

---

## 3. False Agency & Corporate Jargon Translation

### False Agency Prohibition
Inanimate concepts, code, architectures, and algorithms cannot perform human actions:
- **Bad**: *"The schema decided to reject the mutation."*
- **Good**: *"The database rejected the mutation because the schema failed validation."*
- **Bad**: *"The bug quietly emerged over time."*
- **Good**: *"The race condition occurred when concurrent workers executed."*

### Corporate Jargon Translation Dictionary
| Avoid | Plain English Replacement |
| :--- | :--- |
| *Navigate (challenges)* | Handle, resolve, address |
| *Unpack (concepts)* | Explain, analyze, examine |
| *Lean into* | Adopt, embrace, accept |
| *Landscape (context)* | Situation, market, field |
| *Game-changer* | Significant, decisive, major |
| *Double down* | Commit further, increase investment |
| *Deep dive* | Detailed examination, analysis |
| *Circle back* | Revisit, return to |
| *Move the needle* | Improve results, make measurable progress |
| *Table the discussion* | Postpone, defer |

### Metric & Domain Honesty
- **Evidence Over Metric Claims**: Quantitative assertions (e.g., "99.9% uptime", "10k+ users", "300% faster") must reflect verified database records or telemetry logs; otherwise omit entirely. Never invent metrics.
- **Zero Fictitious Badges**: Forbid displaying uncertified compliance badges ("SOC 2 Type II", "ISO 27001", "Enterprise Ready") without verified proof in workspace.
- **Concrete Domain Names**: Ban placeholder entity names (*Acme Corp, John Smith, Jane Doe, Nexus, Pulse, Unleash*). Use realistic, domain-specific naming.

---

## 4. Voice-Preserving 4-Step Rewrite Protocol

When editing existing prose to remove AI tells:

1. **Mark the Tells**: Scan the text once, identifying structural reversals, throat-clearing, and buzzwords.
2. **Draft the Direct Statement**: Keep every supported fact, benchmark, number, and citation. State points directly without introductory fanfare.
3. **Source Fidelity Check (Zero Invention)**:
   - NEVER invent facts, metrics, or citations to make prose sound "punchy."
   - If a detail is missing, write a simpler sentence or ask the user.
4. **Protected Content Invariants (100% Immutable)**:
   - Code blocks (` ``` `) and inline code (`` `symbol` ``) are **STRICTLY IMMUTABLE**.
   - YAML frontmatter headers (`--- ... ---`) are **STRICTLY IMMUTABLE**.
   - Table formatting, URLs, direct quotes, and file paths MUST NOT be modified or rephrased.
   - Limit prose editing to a maximum of **2 passes** to prevent semantic drift.
