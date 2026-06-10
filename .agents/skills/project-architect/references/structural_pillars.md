# THE 8 PILLARS OF STRUCTURAL LOGIC

Before finalizing any architecture, grade it against these 8 pillars. Do not output a blueprint if it fails these rules:

1. **Single Source of Truth**: Data must never be duplicated or ambiguous. Ensure that there is one authoritative location for every piece of information.
2. **Immutability First**: State changes must be predictable and traceable. Use immutable data structures and unidirectional data flow.
3. **Dependency Inversion**: High-level logic must not depend on low-level detail. Abstractions should not depend on details; details should depend on abstractions.
4. **Interface Segregation**: Clients should not be forced to depend on unused methods. Keep interfaces small and focused.
5. **Fail-Fast Mechanism**: Systems crash or report errors immediately upon logical breach. Do not allow the system to continue in an undefined state.
6. **Stateless Logic**: Pure functions are preferred; side effects must be isolated and managed.
7. **Data Sovereignty**: Local data is primary; cloud is backup/sync. The user should own and control their data locally.
8. **Atomic Operations**: Transactions are all-or-nothing. Ensure that complex state changes either succeed completely or fail gracefully with no side effects.
