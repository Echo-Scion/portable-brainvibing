---
description: IDE Agent workflow for extracting graph triplets (Subject, Predicate, Object) from raw code sources.
activation: Triggered automatically by the [TRIPLET_REQUEST] directive during orion_ops ingest.
---

# Knowledge Graph Extraction Workflow

You have been invoked because a recent ingestion operation generated a `[TRIPLET_REQUEST]`.
This means the knowledge graph (`orion.db`) requires true semantic relationships (triplets) to be mapped for the newly ingested files, replacing the deprecated AST method.

## Goal
Transform unstructured code/documentation into structured graph relationships.

## Execution Protocol

1. **Read the Source Files**: 
   Use your file reading tools to quickly scan the files listed under the `[TRIPLET_REQUEST]`.

2. **Extract Semantic Triplets**:
   For each file, extract 3-5 critical relationships.
   - **Subject (s)**: The main entity (e.g., `AuthService`, `UserModel`, `database_config`).
   - **Predicate (p)**: The relationship verb (e.g., `DEPENDS_ON`, `IMPLEMENTS`, `CALLS`, `MANAGES`, `VALIDATES`).
   - **Object (o)**: The target entity (e.g., `JwtToken`, `BaseEntity`, `PostgresDB`).

3. **Format as JSON Array**:
   ```json
   [
     {"s": "AuthService", "p": "DEPENDS_ON", "o": "JwtToken", "src": "path/to/file.ts"},
     {"s": "UserController", "p": "CALLS", "o": "AuthService", "src": "path/to/file.ts"}
   ]
   ```
   *Note: `src` must be the relative path of the file.*

4. **Inject into the Graph**:
   Execute the terminal command to inject your JSON:
   ```bash
   python .agents/scripts/orion.py orion_ops inject_triplets '[{"s": "A", "p": "B", "o": "C", "src": "D"}]'
   ```
   *CRITICAL: Ensure the JSON string is properly quoted so the bash shell parses it correctly. Avoid single quotes inside the JSON values, or escape them.*

5. **Completion Check**:
   Verify the terminal output says `[SUCCESS] Injected X triplets into orion.db.`. If there is a parsing error, fix the JSON and retry.
