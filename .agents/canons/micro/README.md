# Micro-Canons (Domain Cheat-Sheets)

## The Knowledge Shim Concept
Premium Models (Opus/Sonnet) have vast *world-knowledge* and *pre-trained data* from millions of framework documentations. However, Budget Models (Flash/Haiku) often hallucinate when dealing with modern framework APIs (e.g., the latest Next.js App Router, Flutter 3.24, etc.).

**Micro-Canons** are "Cheat Sheet" files (*Maximum 30-50 lines*) specifically designed to bypass the weaknesses of Small Models. These files serve as a replacement for heavy RAG (Retrieval-Augmented Generation), injecting essential *world-knowledge* into super-lightweight static text files.

## Usage Rules (For Budget Models)
1. If task execution involves specific/new technology (e.g.: Flutter, FastAPI) or serverless architectures (e.g.: Supabase Edge Functions, Firebase Cloud Functions, Cloudflare Workers).
2. The agent **MUST** read the relevant `canons/micro/<framework>.md` file (if any) before starting *planning*.
3. Knowledge from the Micro-Canon becomes the Supreme Law *(Override)* over the LLM's inherent knowledge, which might be outdated *(cutoff data)*.

## Micro-Canon Creation Rules
- It is forbidden to create a Micro-Canon exceeding 50 lines.
- It must be in telegraphic bullet points (Format: DO / DONT / SYNTAX).
- Avoid prose/narrative sentences. Use deterministic instructions.
