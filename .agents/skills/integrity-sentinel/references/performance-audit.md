# The Performance & Optimization Audit

You are hunting for silent performance killers. **Do not point out syntax or styling.** Focus strictly on runtime complexity, memory leaks, and rendering bottlenecks.

## 1. Big-O Traps (Algorithmic Complexity)
- **Nested Loops `O(N^2)`**: Are there arrays being iterated inside other iterations?
- **Expensive Lookups**: Are lists/arrays being searched repeatedly (e.g., `.contains()`) instead of using Sets or Maps `O(1)`?
- **Over-fetching**: Is the app pulling 10,000 records from the DB just to display 10?

## 2. Memory Leaks & Resource Exhaustion
- **Unclosed Streams**: Are WebSockets, Rx/Streams, or file handles opened without a guaranteed `dispose()` or `close()`?
- **Orphaned Async Tasks**: Are Promises/Futures fired without being `await`ed or having error handlers, keeping objects alive in memory?
- **Listener Accumulation**: Are event listeners added inside `build` or render methods without being removed?

## 3. Rendering Bottlenecks (Flutter / UI Specific)
- **Massive Rebuilds**: Does changing a single checkbox rebuild the entire screen instead of just a localized widget?
- **Missing `const`**: Are static widget trees rebuilt repeatedly because they lack the `const` constructor?
- **Expensive Builds**: Are heavy synchronous calculations (parsing JSON, sorting lists) happening directly inside the `build()` method?
- **Image Bloat**: Are massive assets loaded into memory without resizing or caching?

## Output
If you find performance bottlenecks, specify the exact Big-O complexity or memory leak mechanism, and provide the exact optimized code.
