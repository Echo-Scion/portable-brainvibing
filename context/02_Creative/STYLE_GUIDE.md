# STYLE_GUIDE: Scionlog & Orion Foundation

> **Master Creative Atlas (Pillar: 02_Creative)**
> Defines Terminal UX, Telemetry Formatting, Telegram Templates, and Tone of Voice.

---

## 1. Visual & Communication Philosophy

- **Aesthetic Theme**: `Cyber-Glass / Minimalist Terminal`
- **Primary Design Principle**: High scannability, zero cognitive noise, deterministic status visibility.
- **Tone of Voice**: Terse, precise, objective, evidence-driven (Caveman brevity with high technical rigor).

---

## 2. CLI & Terminal Output Standards

All Python scripts and CLI utilities must adhere to these output rules:

### A. Unicode & Cross-Platform Encoding
- Always reconfigure standard streams at module initialization:
  ```python
  if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
      sys.stdout.reconfigure(encoding='utf-8')
      sys.stderr.reconfigure(encoding='utf-8')
  ```
- Use ASCII fallbacks or guarded Unicode characters so Windows `cp1252` and Linux `utf-8` render identically.

### B. Standardized Status Banners
```text
========================================
 🌌 ORION: The Unified Brain Engine CLI
========================================
[PASS] Component verified
[WARN] Non-blocking notice
[FAIL] Mechanical failure requiring remediation
```

---

## 3. Telegram Telemetry Templates

Notifications sent by `scionlog/src/core/notifications.py` must use structured HTML/Markdown parsing:

### Trade Signal Template
```markdown
🎯 **SNIPER SIGNAL TRIGGERED**
• **Pair**: BTC/USDT (Long)
• **Regime**: 12/12 Sniper Checklist Confirmed
• **Entry**: $64,250.00 | **SL**: $63,400.00 | **TP1**: $65,500.00
• **Position Size**: 2.5% Equity (Risk: 0.8%)
• **Execution**: Paper Mode
```

### Daily Performance Pulse Template
```markdown
📊 **SCIONLOG DAILY PULSE**
• **Closed Trades**: 8 (Win Rate: 75.0%)
• **Daily Net PnL**: +$342.50 (+1.42%)
• **Max Drawdown**: 0.45%
• **Darwinian Mutations**: 1 parameter adjusted (`atr_multiplier`: 1.8 -> 2.0)
```

---

## 4. Agent Tone & Response Formatting

- **Anti-Affirmation**: Treat proposals as flawed until verified against code AST and test outputs.
- **Unified Footer Mandate**: Every technical response concludes with the clean 3-line footer:
  ```text
  🚦 **CHECKPOINT**: [Brief summary]
  📋 **EVIDENCE**: [Exit Code X or verified state]
  🔮 **NEXT TASK**: [Next step or None]
  ```

---

## 5. Granular Detail References (JIT Child Mapping)
When deep UX or formatting design is needed, generate detail files using this official prefix:
- `Design_` — Interface specs, widget designs, and notification schemas (e.g., `Design_Design_System.md`, `Design_UX_Flows.md`).
