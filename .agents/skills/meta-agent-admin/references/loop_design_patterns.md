# Agent Loop Design Patterns

## 🤖 State Machine Definition
- **Planning**: Breaking down the objective.
- **Researching**: Using search/read tools.
- **Drafting**: Generating code or content.
- **Reviewing**: QA/Verification phase.
- **Exit Conditions**: Define exactly when a state transitions or ends.

## 🛠️ Execution Loop (ReAct)
1. **Input**: User objective.
2. **Thought**: Agent reasoning.
3. **Action**: Tool call selection.
4. **Observation**: Tool output processing.
5. **Repeat**: Until goal is achieved or `max_iterations` reached.

## 🛡️ Guardrails & Memory
- **Memory Management**: Offload massive history to RAG or summarization.
- **Hard Caps**: ALWAYS implement `max_iterations` to prevent infinite loops.
- **Human-in-the-loop**: Mandatory for destructive actions (`DROP`, `DELETE`).

---
*Preserved from Portable Brainvibing Infrastructure*
