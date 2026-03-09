# Micro-Canon: Supabase (≤50 lines — Budget Model Cheat Sheet)

## AUTH
- DO: `supabase.auth.signInWithPassword(email: e, password: p)` — email/pass
- DO: `supabase.auth.signInWithOAuth(OAuthProvider.google)` — OAuth
- DO: `supabase.auth.currentUser` — synchronous, null if not logged in
- DONT: `supabase.auth.user()` — DEPRECATED in v2, use `currentUser`
- DONT: Store JWT in SharedPreferences — SDK handles session auto-refresh

## ROW-LEVEL SECURITY (RLS) — ALWAYS ENABLE
- DO: Enable RLS on ALL tables: `ALTER TABLE public.table ENABLE ROW LEVEL SECURITY;`
- DO: Default-deny: if no policy matches, row is invisible
- SYNTAX for user-scoped read: `CREATE POLICY "read_own" ON public.table FOR SELECT USING (auth.uid() = user_id);`
- SYNTAX for insert own: `CREATE POLICY "insert_own" ON public.table FOR INSERT WITH CHECK (auth.uid() = user_id);`
- DONT: `USING (true)` — grants ALL users ALL rows (public data only)

## QUERIES (JS/TS Client v2)
- DO: `.select('id, name, created_at')` — explicit columns, never `*` in production
- DO: `.eq('user_id', userId).single()` — use `.single()` when expecting 1 row
- DO: `.order('created_at', ascending: false).limit(20)` — always paginate
- DONT: `.select()` without columns — over-fetches and breaks RLS intent
- DONT: Ignore error: always destructure `{ data, error }` and check error first

## EDGE FUNCTIONS
- DO: Validate `Authorization: Bearer <JWT>` header — `supabase.auth.getUser(token)`
- DO: Return `new Response(JSON.stringify(payload), { headers: { 'Content-Type': 'application/json' } })`
- DONT: Use `SUPABASE_SERVICE_ROLE_KEY` in client-side code — server only
- DONT: Call edge function without CORS headers if called from browser

## REALTIME
- DO: `supabase.channel('room').on('postgres_changes', { event: '*', schema: 'public', table: 'messages' }, callback).subscribe()`
- DO: Unsubscribe on widget dispose: `supabase.removeChannel(channel)`
- DONT: Subscribe in StatelessWidget — causes memory leaks

## STORAGE
- DO: Use signed URLs for private files: `storage.from('bucket').createSignedUrl(path, 3600)`
- DO: Use `upsert: true` to avoid conflicts on upload
- DONT: Public bucket for user-sensitive files (invoices, profile data)
