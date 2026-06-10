# Node.js Performance Tuning Tactics

## ⚡ V8 Optimization
- **Event Loop**: Avoid sync blocking (`JSON.parse` large strings, heavy Crypto).
- **Concurrency**: Use `Promise.all()` for independent I/O.
- **Worker Threads**: Offload CPU-bound tasks (Image processing, heavy math).

## 💾 Memory Management
- **Streaming**: Use `fs.createReadStream` and pipe responses to avoid heap bloat.
- **Pagination**: Mandate limit/offset at DB level.
- **OOM Prevention**: Monitor `--max-old-space-size` and heap profiles.

## 📊 Infrastructure
- **Connection Pooling**: Mandate PgBouncer or persistent HTTP connections.
- **Compression**: Enable GZIP/Brotli globally.

---
*Preserved from Portable Brainvibing Infrastructure*
