---
description: General rules to maintain performant code across all platforms.
---

# Performance Optimization

## Rendering & UI
1. Use virtualization for long or dynamic lists.
2. Avoid unnecessary component or widget rebuilds. Only watch/subscribe to the specific state you need.
3. Memoize heavy computations where supported by the platform.

## Data & Network
1. Batch multiple small queries into a single query if possible.
2. Implement caching for data that rarely changes.
3. Paginate large datasets.
4. Optimize image sizes and use lazy loading where applicable.
