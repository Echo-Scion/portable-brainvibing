# Postgres & Supabase Performance Patterns

## 🚀 Snappy Data Delivery (Realtime-First)
- **Instant Sync**: Use `supabase.from('table').stream(primaryKey: ['id']).listen(...)` for dynamic feeds (Chat/Live Data) to eliminate polling lag.
- **Payload Management**: Only subscribe to the columns you need to reduce WebSocket traffic and CPU load on the mobile client.

## 🎯 Server-Side Filtering (No-Jitter Rule)
- **Database Heavy Lifting**: NEVER fetch a large dataset and filter it in Flutter memory. Use Supabase SDK filtering: `.eq()`, `.neq()`, `.gt()`, `.textSearch()`.
- **Pagination**: Mandatory `.range(from, to)` for any list expected to grow beyond 50 items.

## 🛡️ Supabase Row-Level Security (RLS)
```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only read own docs" 
ON documents FOR SELECT 
USING (auth.uid() = user_id);
```

---
## 🚀 Production Safe Indexing
- **Covering Indexes**: Include frequently selected columns in the index to avoid table lookups (`INCLUDE` clause).
- **Concurrency**: ALWAYS use `CREATE INDEX CONCURRENTLY` in production environments.
```sql
CREATE INDEX CONCURRENTLY idx_users_active_email 
ON users (email) 
WHERE deleted_at IS NULL;
```

## 🔄 The Safe Refactor Pattern
...
2. **Sync**: Application writes to both old and new.
3. **Backfill**: Migrate data in batches (COMMIT every 10k).
4. **Drop**: Remove old column after verification.

---
*Preserved from Portable Brainvibing Infrastructure*
