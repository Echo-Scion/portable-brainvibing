# The Logic & Semantic Audit

You are hunting for deep, semantic bugs that compilers and basic linters miss. **Do not point out syntax, formatting, or line-count issues here.** You are looking for algorithmic flaws that will corrupt data or crash the app in production.

## 1. Broken Math & Precision
- **Division by Zero**: Are denominators ever unvalidated?
- **Precision Loss**: Are `double` or `float` types used for currency or precise measurements instead of `Decimal` or `Int`?
- **Off-by-One**: Are loop boundaries or array indices mathematically sound?
- **Type Coercion Traps**: Are strings being implicitly converted to numbers, causing NaN propagation?

## 2. Logic Flaws & State Mutation
- **Contradictory Branches**: Are there `if/else` paths that logically conflict or overlap, leading to unreachable code?
- **Unsafe Mutation**: Is shared state modified concurrently without locks or immutable copying?
- **Race Conditions**: Do async operations rely on a specific execution order that isn't guaranteed?
- **Orphaned State**: Are objects left in an invalid state if a `try/catch` block fails halfway through a mutation?

## 3. Data Anomalies & Drift
- **Stale Cache**: Does the app cache data but lack an invalidation mechanism when the source of truth changes?
- **Serialization Gaps**: Do DTO mappings drop fields, fail on unexpected nulls, or misinterpret enums?
- **State Drift**: Can the UI show state A while the backend has already moved to state B?

## 4. Tech Debt & Architectural Fragility
- **Magic Numbers**: Are raw strings or numbers hardcoded deep in business logic instead of centralized constants?
- **Hidden Coupling**: Does module A secretly rely on the internal implementation details of module B?
- **God Objects**: Is a single class or function acting as a dumping ground for unrelated logic?

## Output
If you find these deep semantic flaws, document the exact scenario that breaks the logic and provide the specific algorithmic fix.
