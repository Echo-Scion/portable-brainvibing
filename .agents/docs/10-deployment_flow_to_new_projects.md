# VOLUME X: DEPLOYMENT FLOW TO NEW PROJECTS

---

## Chapter 22: Complete Deployment Procedure

### 22.1. Step 1: Identify Target & Stack
The AI must ask for framework (`react`, `flutter`, `nextjs`, `python`) and language (`typescript`, `dart`, `python`) if `.project_manifest.json` does not exist yet.

### 22.2. Step 2: Gitignore Pre-Flight
The AI must ensure `.gitignore` exists and includes `node_modules`, `build`, `.env*`, etc. This prevents RAG ingest from indexing binary garbage.

### 22.3. Step 3: Execution
```bash
# Deploy to a single IDE (Gemini default)
python .agents/scripts/orion.py foundation deploy --target /path/to/project --framework flutter --language dart

# Deploy to multiple IDEs
python .agents/scripts/orion.py foundation deploy --target /path/to/project --framework react --language typescript --ai cursor,copilot

# Deploy to all 6 IDEs
python .agents/scripts/orion.py foundation deploy --target /path/to/project --framework react --language typescript --ai all
```

### 22.4. Step 4: Safe Auto-Ingest
```bash
python .agents/scripts/orion.py orion_ops ingest .agents/rules .agents/skills .agents/canons .agents/workflows context/
```
**STRICTLY FORBIDDEN**: `ingest .` or ingest without arguments. This can freeze the system or corrupt the SQLite database.

### 22.5. Step 5: Periodic Sync
```bash
# Sync after Foundation is updated
python .agents/scripts/orion.py foundation sync-ai --target /path/to/project

# Push project improvements back to master Foundation
python .agents/scripts/orion.py foundation push-upstream --source /path/to/project
```

---

