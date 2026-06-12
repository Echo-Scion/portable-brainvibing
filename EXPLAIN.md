# Otak AI: Ensiklopedia Utama Ekosistem `.agents` & `.orion`
# (Portable Brainvibing Infrastructure v0.0.1)

> **Dokumen ini adalah Ensiklopedia Lengkap — bukan ringkasan, bukan panduan cepat.** Setiap file, setiap konsep, setiap mekanisme didokumentasikan secara eksplisit beserta contoh kode dan rasional arsitektural. Dibuat agar bisa dibaca dari awal sampai akhir sebagai referensi absolut.

---

# VOLUME I: FONDASI TEORITIS — Mengapa Sistem Ini Ada?

---

## Bab 1: Tiga Kelemahan Fatal Large Language Models (LLM)

Sistem `.agents` ada karena LLM — betapapun canggihnya — memiliki tiga kerentanan struktural yang tidak bisa diatasi dengan prompt biasa. Infrastruktur ini bukan sekadar "koleksi aturan"; ia adalah **mesin koreksi deterministik** yang mengubah chatbot probabilistik menjadi instrumen rekayasa.

### 1.1. Penurunan Atensi (Context Degradation / "Lost in the Middle")
Ketika LLM disuapi konteks besar (>50.000 token), kemampuannya mengingat instruksi di bagian tengah menurun drastis. Fenomena ini disebut "Lost in the Middle" dan telah dibuktikan secara empiris oleh Liu et al. (2023).

**Skenario Nyata:**
Anda memasukkan panduan arsitektur setebal 100 halaman ke konteks AI. Di halaman 3, ada Aturan #12: *"Jangan gunakan `setState`. Selalu gunakan `Riverpod`."* Anda lalu meminta AI membangun layar Login. AI menulis 200+ baris kode UI, dan karena perhatiannya sudah berpusat pada tugas langsung, aturan di halaman 3 "menguap." AI menggunakan `setState`, dan arsitektur proyek langsung terpolusi. Anda baru menyadarinya 3 hari kemudian setelah 15 layar lain sudah dibangun.

**Solusi Arsitektural: Perutean Just-In-Time (JIT)**
Kerangka kerja `.agents` secara fisik mencegah pemuatan semua aturan sekaligus. Ia menggunakan tabel routing dinamis (didefinisikan di `GEMINI.md` §4). Jika pengguna bertanya tentang "database", hanya aturan `backend-orchestrator` dan `data-logic` yang dimuat. Jika tentang "UI", hanya `ui-finish` dan `palette`. Ini menjamin bahwa konteks AI selalu bersih, terfokus, dan terisi hanya oleh informasi yang relevan.

### 1.2. Fragmentasi IDE (Vendor Lock-In Vulnerability)
Setiap IDE (Cursor, Windsurf, Copilot, Antigravity) memiliki mesin AI dan alat interaktif yang berbeda-beda:
- **Cursor**: `Composer Ask`, `Agent Mode`, `Ctrl+K`.
- **Antigravity/Gemini**: `/grill-me`, `/goal`, `/schedule`.
- **Copilot**: `/fix`, `/tests`, variabel Chat.
- **Windsurf**: `Cascade`, alat aliran bawaan.

Jika aturan ditulis secara hardcoded *"Gunakan `/grill-me` saat bingung"*, maka saat proyek dibuka di Cursor, aturan tersebut menjadi instruksi mati. AI akan bingung dan mungkin error.

**Solusi: Arahan Perkakas Agnostik-IDE**
Aturan ditulis dalam bahasa abstrak: *"Trigger your native interactive questionnaire tool."* AI yang sadar-diri terhadap host IDE-nya akan menerjemahkan ini secara otomatis — menjadi `/grill-me` di Antigravity, `Composer Ask` di Cursor, dst. Ini didefinisikan di `core-guardrails.md` §1.8 dan menjamin portabilitas penuh.

### 1.3. "Pajak Kesopanan" (Token Inefficiency / Politeness Tax)
Respons AI standar membuang banyak token untuk basa-basi.

| Gaya | Contoh | ~Token |
|:--|:--|:--|
| Standar | "I apologize for the oversight! You are absolutely right. Let's go ahead and fix the null pointer exception by adding a safety check to the Auth module." | ~35 |
| Caveman | "Auth crash. User null. Adding check." | ~7 |

Selisih 5x lipat. Jika AI merespon 50 kali sehari selama sebulan: Standar = 35.000 token terbuang sia-sia vs Caveman = 7.000 token. Token yang dihemat = ruang konteks ekstra untuk kode yang sesungguhnya.

**Solusi: Caveman Protocol** (`skills/caveman/SKILL.md`)
Protokol komunikasi yang secara struktural melarang kata sandang (a, an, the), pembukaan sopan, dan narasi panjang. Mendukung 6 level intensitas: `lite`, `full`, `ultra`, `wenyan-lite`, `wenyan-full`, `wenyan-ultra`.

---

# VOLUME II: ARSITEKTUR SISTEM — Anatomi Lengkap `.agents`

---

## Bab 2: Router Aktif — Master BIOS (`GEMINI.md`)

File `GEMINI.md` (atau `CLAUDE.md`, tergantung IDE) di root proyek bertindak sebagai **Active Router** dan **Master BIOS** — ia adalah hal pertama yang dibaca oleh setiap agen AI saat memulai sesi.

### 2.1. Sequential Tool Ban (Hard Gate — §1.0)
```
CRITICAL: Anda DILARANG menggunakan alat modifikasi (write_to_file, replace_file_content,
run_command, dll.) SEBELUM Anda menjalankan view_file pada .agents/rules/core-guardrails.md.
```
Ini adalah blokir mekanis absolut. AI wajib membaca "hukum utama" sebelum diizinkan menyentuh file apa pun. Tujuannya: mencegah Tunnel Vision dan Agentic Amnesia di awal sesi.

### 2.2. Integrity Flag (§1.1)
Setiap rencana implementasi (`implementation_plan.md`) wajib menyertakan kutipan langsung dari `core-guardrails.md` di header. Ini membuktikan bahwa konteks AI benar-benar dimuat, bukan halusinasi.

### 2.3. Auto-Pilot Injector (§1.5)
Sebelum memulai tugas APA PUN, agen wajib menjalankan:
```bash
python .agents/scripts/orion.py brain sync "<kata_kunci_tugas>"
```
Ini menyuntikkan standar dinamis yang relevan ke dalam konteks, memastikan agen tidak bekerja "dalam gelap."

### 2.4. Darwinian Heartbeat (§1.7)
Jika `context.json` mengandung `"evolution_overdue": true`, agen WAJIB menjalankan:
```bash
python .agents/scripts/orion.py evolve mine-friction
```
Ini memaksa sistem untuk berevolusi dari kesalahan sebelum mengerjakan tugas baru.

### 2.5. JIT Knowledge Routing Table (§4)
Tabel routing lengkap yang memetakan 20+ kategori prompt pengguna ke file target spesifik. Contoh:

| Jika Prompt Pengguna Berkaitan Dengan... | Langsung Muat File... |
|:--|:--|
| Proyek Baru, Inisialisasi | `canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-init.md` |
| Strategi Bisnis, Pertumbuhan | `skills/saas-strategist/SKILL.md` |
| Arsitektur Sistem, Skema DB | `skills/project-architect/SKILL.md` |
| Frontend UI, Animasi | `skills/ui-finish/SKILL.md` |
| Keamanan, QA, Testing | `skills/integrity-sentinel/SKILL.md` |
| Debugging, Error Runtime | `skills/frontend-experience/SKILL.md` |
| Deployment, CI/CD | `skills/project-operator/SKILL.md` |
| Orion, Knowledge Base | `skills/brain-graph/SKILL.md` |
| Token, Biaya LLM | `skills/cost-optimizer/SKILL.md` |
| Akhir Sesi, Handoff | `workflows/session-offload.md` |

### 2.6. Unified Response Footer (§5)
Setiap respons teknis WAJIB diakhiri dengan blok navigasi:
```
🚦 CHECKPOINT: [Apa yang baru saja terjadi]
📋 EVIDENCE: [Exit Code atau status output]
🧠 EVALUATION: [Analisis akar masalah jika error]
🔮 NEXT TASK: [Langkah selanjutnya]
⚡ RECOMMENDED TIER: BUDGET|STANDARD|PREMIUM
```

---

## Bab 3: Omni-Buffer — Sinkronisasi Konteks IDE (`.orion/working/context.json`)

### 3.1. Masalah yang Dipecahkan
AI tidak tahu file apa yang sedang dilihat pengguna. Jika pengguna berkata "Perbaiki file ini", AI bisa saja mengedit file yang salah. Ini disebut "halusinasi spasial."

### 3.2. Mekanisme Kerja
Skrip hook `hooks/pre-agent-wake.py` dipanggil oleh IDE (atau daemon latar belakang) sebelum AI memulai giliran. Skrip ini menulis state IDE ke JSON:
```json
{
  "timestamp_ms": 1718104500000,
  "active_file": "src/auth/middleware.ts",
  "terminal_error": "TypeError: Cannot read properties of undefined (reading 'token')",
  "user_intent": "",
  "ide_source": "antigravity",
  "evolution_overdue": false,
  "unprocessed_learnings": 0
}
```

### 3.3. Stale Data Guard
Jika `timestamp_ms` lebih tua dari 5 menit dibanding waktu sistem saat ini, AI wajib membuang data tersebut dan bertanya langsung ke pengguna. Ini mencegah tindakan berdasarkan konteks kadaluarsa.

### 3.4. Autonomic Evolution Hook
Di dalam `pre-agent-wake.py` baris 44-70, terdapat logika otomatis: jika jumlah tag `[Darwinian Hook]` di `LEARNINGS.md` >= 3, skrip akan:
1. Menandai `evolution_overdue = True`.
2. Secara otomatis men-spawn `subprocess.Popen` yang menjalankan `orion.py evolve mine-friction` di background.
Artinya: evolusi tidak perlu menunggu perintah manual — ia terjadi secara otonom.

---

## Bab 4: Pemfilteran Terminal — RTK (Rust Token Killer)

### 4.1. Masalah
Perintah terminal seperti `npm install` bisa menghasilkan 5.000+ baris output (progress bar, download log, info). Jika AI membaca semua ini, konteks window-nya langsung meledak.

### 4.2. Solusi
RTK adalah binary Rust yang mem-proxy perintah terminal. `rtk npm install` mencegat output, menghapus progress bar dan log `INFO`, hanya meneruskan `WARN` dan `ERROR`. Penghematan: 60-90% token.

### 4.3. Decision Tree (Wajib — dari `antigravity-rtk-rules.md`)
```
Q1. Apakah perintah menghasilkan output teks besar? (git log, find, grep, docker ps)
    ├── YA → Gunakan rtk <cmd>
    └── TIDAK → Lanjut Q2
Q2. Apakah perintah interaktif atau memerlukan output JSON mentah?
    ├── YA → Gunakan perintah RAW (tanpa rtk)
    └── TIDAK → Gunakan rtk <cmd> sebagai default
```

### 4.4. Meta Commands
```bash
rtk gain              # Lihat penghematan token
rtk gain --history    # Riwayat perintah + penghematan
rtk proxy <cmd>       # Jalankan mentah tanpa filter (untuk debugging)
```

### 4.5. Fallback (dari `prerequisites.md`)
Jika `rtk` tidak tersedia (`command not found`), agen wajib degradasi ke `grep_search` native IDE atau `view_file` dengan parameter `StartLine`/`EndLine` yang sempit. Tidak boleh memblokir tugas.

---

# VOLUME III: OTAK RAG LOKAL — Anatomi `.orion/`

---

## Bab 5: Struktur Direktori `.orion/`

```
.orion/
├── _manifest.json        # Metadata seluruh indeks (36KB, auto-generated)
├── index.md              # Peta indeks manusia-bisa-baca dari seluruh aset (135 entri)
├── log.md                # Log episodik lintas-sesi
├── orion.db              # Database SQLite utama (225KB) — inti otak
├── episodic/             # Ringkasan sesi masa lalu (episodic memory)
├── matrix/               # Matriks YAML terkompresi dari aturan
├── sources/              # 118 file .yml/.md — salinan terproses dari seluruh aset
└── working/
    └── context.json      # Omni-Buffer (state IDE real-time)
```

### 5.1. `orion.db` — Database SQLite Utama
Menggunakan tabel virtual **FTS5** (Full Text Search 5) untuk pencarian leksikal instan:
```sql
CREATE VIRTUAL TABLE memories USING fts5(
    id UNINDEXED,
    title,
    content,
    tags
);
```
Setiap file `.agents` di-hash dengan SHA-256 sebelum di-upsert, mencegah duplikasi. Kueri pencarian instan tanpa biaya cloud:
```sql
SELECT * FROM memories WHERE memories MATCH 'auth OR jwt OR session';
```

### 5.2. `sources/` — 118 File Refleksi
Ketika `orion_ops ingest` dijalankan, setiap file di `.agents/rules/`, `.agents/skills/`, `.agents/canons/`, dan `.agents/workflows/` diproses dan disimpan ke folder `sources/` sebagai file `.yml` atau `.md` yang distrukturisasi ulang. Folder ini adalah "cermin terindeks" dari seluruh ekosistem.

### 5.3. `matrix/` — Matriks Aturan YAML
Versi YAML dari setiap file aturan. Dihasilkan oleh `compile_rules.py`. Tujuannya: agar NanoBrain dan skrip Python bisa mem-parse aturan tanpa harus mem-parse Markdown secara manual.

### 5.4. `index.md` — Peta Navigasi Manusia
File 135-baris yang mendaftar setiap aset dalam ekosistem, dikelompokkan per layer:
- **Infrastructure Layer**: Kanon, aturan, skill, workflow.
- **Context Layer**: File strategi bisnis, arsitektur, roadmap.
- **Project Docs Layer**: LEARNINGS.md.
- **Raw/Source Layer**: Skrip Python mentah (harness, compress, dll).

### 5.5. `_manifest.json` — Metadata Mesin
File JSON besar (36KB) yang menyimpan metadata hash, tanggal terakhir diproses, dan tipe klasifikasi untuk setiap file. Digunakan oleh `orion_ops.py` untuk mengetahui apakah file sudah berubah sejak ingest terakhir.

---

## Bab 6: Relational Triplet Graph (Pencegah Bug Kompilasi)

### 6.1. Konsep Inti
Kode sumber bukan hanya teks; ia memiliki relasi struktural antar-entitas. Sistem mengekstrak **Triplet Semantik** (Subject - Predicate - Object) dari setiap file:
```json
{
  "subject": "UserController",
  "predicate": "depends_on",
  "object": "AuthService",
  "context": "UserController requires AuthService to validate JWT tokens on line 45."
}
```

### 6.2. Dampak Praktis
Jika AI diminta refaktor `AuthService`, Graph Triplet langsung mengeluarkan peringatan:
*"UserController depends on AuthService. Anda WAJIB memperbarui keduanya."*
Ini menghilangkan bug kompilasi akibat refaktor buta (blind refactoring).

### 6.3. Injeksi Triplet
Workflow `knowledge-extraction.md` menginstruksikan AI untuk:
1. Membaca file sumber tertentu.
2. Mengekstrak 3-5 Triplet Semantik.
3. Menjalankan `orion_ops inject_triplets` yang mengeksekusi SQL `INSERT` ke tabel edge.

---

## Bab 7: Universal AST Parser (Peringkas Kode)

### 7.1. Masalah
Memasukkan 2000 baris kode ke konteks AI sangat mahal secara token. Sebagian besar baris adalah komentar, whitespace, dan blok logika berulang yang tidak relevan untuk pemahaman arsitektural.

### 7.2. Mekanisme
File `scripts/utils/ast_parser.py` memproses kode sumber dan menghasilkan "rangka tulang" (skeleton):

**Kode Asli (50 baris):**
```python
class AuthService:
    # This function logs the user in
    def login(self, user_id: str):
        print("Logging in...")
        db.connect()
        if not user:
            raise Exception("User not found")
        return True
```

**Footprint AST (2 baris):**
```python
class AuthService:
    def login(self, user_id: str) -> bool: pass
```

Reduksi: **~90%** ukuran, dengan retensi sempurna terhadap nama kelas, nama metode, dan tipe parameter. AI tahu arsitektur tanpa membaca implementasi.

---

## Bab 8: NanoBrain Intelligence (`qwen2.5:0.5b`)

### 8.1. Deskripsi
Model LLM kuantisasi super-kecil (<500MB) yang berjalan secara lokal via Ollama. Bukan pengganti model besar; ini adalah **asisten pra-proses** yang murah.

### 8.2. Active Mode (`brain sync`)
Ketika pengguna mengetik "fix the login", NanoBrain:
1. **Semantic Query Expansion**: Memperluas "login" → `["auth", "jwt", "session", "oauth"]`.
2. **FTS5 Search**: Menjalankan kueri di `orion.db` dengan istilah yang diperluas. Hasilnya: ~20 dokumen.
3. **Dynamic Rule Filtering**: Membaca 20 dokumen, memberi skor YES/NO berdasarkan konteks saat ini. Hanya dokumen YES (~3 dokumen) yang dikirim ke IDE AI.

Ini menjamin: AI model mahal (Claude, Gemini) hanya menerima konteks terfokus-laser, bukan 20 dokumen acak.

### 8.3. Sleep Mode (`nano`)
Saat IDE ditutup:
1. NanoBrain membaca transkrip percakapan harian (`transcript.jsonl`).
2. Merangkum apa yang dibangun hari itu menjadi ~500 token.
3. Mengekstrak relasi Triplet baru dan menyimpannya ke `orion.db`.
4. Ringkasan disimpan di `episodic/` sebagai memori episodik permanen.

---

# VOLUME IV: PERPUSTAKAAN ATURAN (`rules/`) — 10 File Hukum

---

## Bab 9: Daftar Lengkap File Aturan

### 9.1. `core-guardrails.md` (142 baris | 11KB)
**Hukum Tertinggi.** Berisi 10 seksi:
1. **Unified Response Protocol**: Wajib footer CHECKPOINT/EVIDENCE/EVALUATION/NEXT di setiap respons.
2. **Environment Boundary Check (§1.5)**: Melarang penerapan kebijakan "82-File Mandate" di dalam repo `_foundation`.
3. **Native Orion Execution (§1.6)**: Wajib menggunakan `orion.py`, bukan binary eksternal.
4. **Omni-Buffer Context Protocol (§1.7)**: Wajib membaca `context.json` di awal sesi.
5. **IDE-Agnostic Tooling (§1.8)**: Terjemahan perintah ke alat bawaan masing-masing IDE.
6. **Reasoning Standards (§2)**: Plan Protocol, Anti-Laziness Mandate, 5-Why Script, Evidence Mandate.
7. **Edge-Case Tax (§2)**: Wajib Matriks Edge-Case untuk tugas STANDARD/PREMIUM.
8. **Circuit Breaker (§4)**: 3x gagal berturut-turut = ABORT dan minta bantuan manusia.
9. **Rule Precedence (§5)**: Urutan prioritas: Security > Core > Tier > Domain > Skills.
10. **Token Efficiency (§9)**: AST Hollowing, Sleep-State Delegation, Anti-Full-Read.

### 9.2. `security-guardrails.md` (168 baris | 9.3KB)
**Hukum Keamanan & Audit Ofensif.** Berisi:
- **Pre-Commit Secrets Scan**: Perintah `grep` wajib sebelum setiap `git commit` untuk mendeteksi kunci OpenAI (`sk-*`), `SUPABASE_SERVICE_ROLE_KEY`, private key PEM.
- **Prompt Injection Defense**: Algoritma deterministik yang mendeteksi dan menolak instruksi jahat ("Ignore previous instructions").
- **Least Privilege**: Wajib justifikasi setiap permission. Default = READ-ONLY.
- **Destructive Command Gate**: `rm -rf`, `DROP TABLE`, `DELETE FROM` tanpa WHERE wajib konfirmasi `[DO: YES]`.
- **Offensive Audit Protocol**: AI dipaksa menjadi "Lead Quant Security Auditor" yang:
  - Menjalankan mutation testing (sengaja masukkan bug, pastikan test menangkapnya).
  - Memeriksa setiap `catch`/`except` — jika ada silent fail, langsung CRITICAL VULNERABILITY.
  - Audit vertical slice (Route → Controller → Service → Repo), bukan layer-by-layer.

### 9.3. `tier-execution-protocol.md` (172 baris | 11KB)
**Mesin Alokasi Sumber Daya.** Membagi tugas ke dalam 3 tier:

| Tier | Kapabilitas | Profil Model |
|:--|:--|:--|
| **BUDGET** | Fix 1 file, indexing, batch | Flash/Haiku |
| **STANDARD** | UI, code gen, testing | Sonnet/Pro |
| **PREMIUM** | Arsitektur, debugging kompleks | Opus/Thinking |

**Bento-Box Law**: Model BUDGET dilarang multitasking. Hanya boleh 1 file per iterasi.
**Auto-Abort (Downgrade Guard)**: Jika model aktif LEBIH LEMAH dari tier target, agen WAJIB `[ABORT: TIER MISMATCH]`.
**Token Economy**: BUDGET = max 1 file read; STANDARD = 3-5 surgical reads; PREMIUM = unlimited (justified).
**Adversarial Twin Protocol**: Tulis skrip exploit → jalankan → log hasilnya dalam XML `<adversarial_attack>`.

### 9.4. `development-operations.md` (155 baris | 9.3KB)
**Operasi Pengembangan.** Berisi 3 sub-sistem:
- **Git Workflow**: Konvensi commit (`<type>(<scope>): <subject>`), branching (`feat/*`, `fix/*`), Save Point Protocol (commit setelah setiap sub-langkah sukses).
- **AutoHarness Protocol**: AI wajib menulis skrip validasi otomatis (Harness) untuk operasi destruktif. Tipe: Action-Verifier, Action-Filter, Policy. Output wajib: `action_id`, `is_legal`, `violated_rule`, `fix_hint`.
- **Context Management**: Hierarki konteks 3-layer (Global → Project → App), Skeleton-First Law (BUDGET dilarang full-read), 82-File Mandate (hanya untuk proyek SaaS target).

### 9.5. `performance-optimization.md` (94 baris | 3.6KB)
**Bolt Protocol.** Sebelum optimasi apapun, wajib lulus 3 gerbang:
1. Measurable? (Bisa diukur?) → Jika TIDAK, batalkan.
2. Readable? (Bisa dibaca?) → Jika TIDAK, batalkan.
3. Scope < 50 baris? → Jika TIDAK, batalkan.

**500-Line Decision Tree**: File > 500 baris = WAJIB refaktor.
**Keyword Surgical Loading**: Map (AST) → Search (grep) → Surgical Read (view_file dengan line range).

### 9.6. `web-api-standards.md` (131 baris | 3.9KB)
**Standar Web & API.** Berisi:
- **CSP (Content Security Policy)**: Wajib meta tag atau header.
- **4-State Map**: Setiap komponen UI yang fetching data WAJIB menangani: Loading, Error, Empty, Success.
- **Zod Schema Mandate**: JANGAN PERNAH trust `req.body`. Wajib validasi Zod.
- **API Response Contract**: Format standar `{ success: true/false, data/error: {...} }`.
- **Idempotency Pattern**: Operasi kritis wajib `Idempotency-Key` header.

### 9.7. `context-standards.md` (19 baris | 1.2KB)
Penegakan batas konteks. Melarang penerapan 82-File Mandate di repo `_foundation`. Memaksakan **AST Hollowing** (larangan `view_file` pada file > 100 baris tanpa `rtk read`).

### 9.8. `prerequisites.md` (34 baris | 2.3KB)
**Graceful Fallback Matrix.** Mendefinisikan 4 prasyarat dan fallback-nya:

| Prasyarat | Fallback |
|:--|:--|
| RTK (Rust) | `grep_search` atau `view_file` dengan line range |
| Orion (Python) | `grep_search` manual pada `.orion/` |
| QMD/Ollama | `grep_search` dan traversal manual |
| Subagent Orchestration | Handle di main thread dengan `grep_search` agresif |

### 9.9. `antigravity-rtk-rules.md` (54 baris | 1.6KB)
Aturan spesifik untuk integrasi RTK di Antigravity IDE. Decision tree dan contoh perintah.

### 9.10. `RULES_INDEX.md` (1.4KB)
Indeks terkompilasi dari semua aturan. Diparsing oleh NanoBrain untuk filtering cepat selama JIT routing.

### 9.11. `rules/local/` (Sub-direktori)
Tempat untuk aturan spesifik-proyek yang meng-override aturan global. Kosong di `_foundation`.

---

# VOLUME V: SKILL / PERSONA (`skills/`) — 16 Spesialisasi

---

## Bab 10: Konsep Skill
Setiap skill adalah sebuah "topi" (hat) yang dikenakan AI. Saat dimuat, skill membatasi fokus AI ke domain tertentu dan memaksakan pola pikir spesifik. Setiap folder skill berisi `SKILL.md` (instruksi wajib) dan opsional `references/` (dokumen pendukung mendalam).

### 10.1. `ai-engineer`
**Domain:** Mitigasi sifat probabilistik LLM.
**Konten:** Matriks asersi, Confidence Gates, anti-halusinasi. Digunakan saat agen memodifikasi folder `.agents` itu sendiri.

### 10.2. `api-contract`
**Domain:** Kontrak antarmuka klien/server.
**Konten:** Spesifikasi OpenAPI, validasi Zod, pola keamanan API.
**Referensi:** `references/api_safety_patterns.md`.

### 10.3. `backend-orchestrator`
**Domain:** Arsitek backend master.
**Konten:** Manajemen kebocoran memori Node.js, connection pooling, optimasi SQL, indeks database.
**Referensi:** 6 sub-dokumen — `backend-architect.md`, `backend-optimizer.md`, `cache-optimizer.md`, `db-expert.md`, `enterprise_patterns.md`, `node_performance_tuning.md`, `postgres_patterns.md`.

### 10.4. `brain-graph`
**Domain:** Operator `orion.db` dan RAG lokal.
**Konten:** Cara query FTS5, injeksi triplet, pemeliharaan SQLite.

### 10.5. `caveman`
**Domain:** Kompresi komunikasi ultra-terse.
**Konten:** 6 level intensitas. Mendukung `wenyan` (varian bahasa Mandarin klasik).

### 10.6. `caveman-compress`
**Domain:** Kompresi file `.md`.
**Konten:** Membaca file markdown dan menggantinya dengan versi terse melalui regex. Menyimpan backup `.original.md`.
**Skrip pendukung:** `scripts/__init__.py`, `scripts/compress.py`, `scripts/detect.py`, `scripts/validate.py`, `scripts/benchmark.py`, `scripts/cli.py`.

### 10.7. `cost-optimizer`
**Domain:** Manajemen anggaran token dan cloud.
**Konten:** Routing model murah (Haiku) untuk tugas sederhana, model mahal (Opus) untuk tugas kompleks.

### 10.8. `data-logic`
**Domain:** Kekekalan data (immutability).
**Konten:** Melarang global state, Redux/Zustand patterns, fungsi murni, DTO tidak boleh dimutasi.

### 10.9. `frontend-experience`
**Domain:** Debugging UI/UX.
**Konten:** Perbaikan re-render berlebih, infinite loop DOM, sinkronisasi state React/Flutter.
**Referensi:** `references/ux-designer.md`.

### 10.10. `integrity-sentinel`
**Domain:** Red Team & QA Otomatis.
**Konten:** Audit arsitektur, audit bloat, audit duplikat, audit fail-fast, audit logika, audit performa, audit retry, uji beban.
**Referensi:** 11 sub-dokumen: `architecture-audit.md`, `bloat-audit.md`, `duplicate-audit.md`, `fail-fast-audit.md`, `flutter_testing_patterns.md`, `load_testing_tactics.md`, `logic-audit.md`, `master-audit.md`, `performance-audit.md`, `plan-checklist.md`, `retry-audit.md`, `telemetry-gate.md`.

### 10.11. `meta-agent-admin`
**Domain:** Arsitek sistem `.agents` itu sendiri.
**Konten:** Evolusi ekosistem, pembuatan aturan, integritas routing.
**Referensi:** `agent-architect.md`, `agent-evolution.md`, `context-manager.md`, `knowledge.md`, `loop_design_patterns.md`, `system-admin.md`, `tech-writer.md`.

### 10.12. `palette`
**Domain:** Estetika mikro & aksesibilitas.
**Konten:** CSS token, animasi halus, ARIA label, glassmorphism, harmoni warna, keyboard navigation.

### 10.13. `project-architect`
**Domain:** PRD & Blueprint skala tinggi.
**Konten:** Menerjemahkan ide pengguna menjadi dokumen teknis sebelum kode ditulis.
**Referensi:** `architectural_standards.md`, `startup_growth.md`, `strategic_rigor.md`, `structural_pillars.md`.

### 10.14. `project-operator`
**Domain:** DevOps & resiliensi.
**Konten:** Dockerfile, CI/CD pipeline, Nginx, chaos engineering.
**Referensi:** `chaos-engineer.md`, `release-manager.md`.

### 10.15. `saas-strategist`
**Domain:** Strategi bisnis SaaS.
**Konten:** Analisis viabilitas, monetisasi, pertumbuhan, konten viral.
**Referensi:** `saas-growth.md`, `saas-viability.md`, `technical_content.md`, `viral_growth.md`.

### 10.16. `ui-finish`
**Domain:** Polesan akhir UI premium.
**Konten:** Empty states, loading spinner, error boundaries, Liquid Glass widgets.
**Referensi:** `visual_engineering.md`.

---

# VOLUME VI: WORKFLOW / SOP — 10 Prosedur Operasi Standar

---

## Bab 11: Daftar Lengkap Workflow

### 11.1. `app-lifecycle.md` (11.9KB)
**Mega-workflow E2E.** 10 langkah:
1. Requirements Intake (Interview).
2. Blueprint Generation.
3. Scaffold Database.
4. API Layer.
5. UI Layer.
6. Integration.
7. Testing.
8. Polish.
9. Pre-Deploy.
10. Launch.

### 11.2. `audit-and-test.md` (6.8KB)
**Strict TDD Loop** (Red → Green → Refactor) + PR Code Review Checklist.

### 11.3. `auto-context.md` (2.4KB)
**Ekstraksi Organik.** Jika pengguna berulang kali mengoreksi AI ("Bukan, maksud saya X"), sistem otomatis mengekstrak aturan X, memformalisasikannya, dan menyimpannya ke `orion.db`.

### 11.4. `knowledge-extraction.md` (2KB)
Menginstruksikan AI untuk membaca file kode, mengekstrak 3-5 Triplet Semantik, dan menjalankan `orion_ops inject_triplets`.

### 11.5. `knowledge-sync.md` (2.5KB)
DevOps internal: bump versi, verifikasi integritas, commit ke Git.

### 11.6. `orion-ops.md` (1.8KB)
SOP untuk membangun ulang database FTS5, query graph, dan memperbaiki state SQLite yang rusak.

### 11.7. `prod-deploy.md` (1.7KB)
Checklist pra-produksi: variabel environment, minifikasi, security headers.

### 11.8. `project-migrate.md` (3.9KB)
Panduan migrasi proyek warisan/brownfield ke arsitektur `.agents` tanpa merusak yang sudah berjalan.

### 11.9. `self-evolve.md` (3.5KB)
**Loop Refleksi Deterministik.** 4 fase:
1. **Error Extraction**: Ekstrak trace error ke XML.
2. **Memory Write**: Tulis ke `LEARNINGS.md`.
3. **Darwinian A/B Evolution**: Fork aturan → Benchmark V1 vs V2 → Promosikan pemenang.
4. **Pattern Recognition**: Scan `LEARNINGS.md` untuk pola berulang → Sintesis aturan/skill/workflow baru.

### 11.10. `session-offload.md` (4.7KB)
**Shutdown Sequence.** 5 langkah:
1. **Scratchpad Eviction**: Hapus file temp.
2. **Gated Auto-Commit**: Logic Gate → Security Gate → History Gate sebelum commit.
3. **Memory Compression**: `compress_memory` + `nano_compressor` untuk mengecilkan log.
4. **Handoff State**: Tulis `handoff.md` dengan Resume Point, Technical State, Anti-Goals.
5. **RTK Metrics**: Laporkan penghematan token sesi ini.

---

# VOLUME VII: SKRIP PYTHON (`scripts/`) — Mesin Eksekusi

---

## Bab 12: Arsitektur Skrip

### 12.1. Entry Point: `orion.py` (4.2KB)
Satu-satunya skrip yang dipanggil langsung. Semua perintah diarahkan melalui CLI modular ini.

### 12.2. Tabel Perintah Lengkap

| Perintah | Target Skrip | Fungsi |
|:--|:--|:--|
| `verify` | `commands/verify_agents.py` (23KB) | Kompilator Markdown — scan semua link, pastikan tidak ada referensi hantu |
| `context-lint` | `commands/context_naming_lint.py` (5.6KB) | Validasi penamaan file konteks terhadap registri 82-file |
| `deploy` | `commands/foundation.py` (29KB) | Deploy/sync Foundation ke proyek baru via symlink |
| `push-upstream` | `commands/foundation.py` | Sync evolusi proyek kembali ke Foundation master |
| `budget` | `commands/track_budget.py` (2.3KB) | Lacak anggaran dan telemetri tier |
| `scan tokens` | `core/scanner.py` (10KB) | Ghost Token Auditor — deteksi bloat memori |
| `scan map` | `core/scanner.py` | Structural Code Mapper — buat skeleton ringan |
| `scan targets` | `core/scanner.py` | Identifikasi target untuk Offensive Audit |
| `preflight` | `commands/preflight_check.py` (6.7KB) | Diagnostik pra-terbang (Self-Healing Routing) |
| `compress` | `commands/compress_memory.py` (6.3KB) | Kompresi memori episodik ke format Caveman |
| `orion_ops init` | `commands/orion_ops.py` (35KB) | Inisialisasi infrastruktur `.orion/` |
| `orion_ops ingest` | `commands/orion_ops.py` | Ingest aturan dan konfigurasi ke graph |
| `amnesia` | `commands/rule_eviction.py` (2.2KB) | Mekanisme eviksi aturan (garbage collection) |
| `swarm` | `commands/auto_delegate.py` (4.6KB) | Multi-Thread Micro-Fix (paralel) |
| `rtk` | `core/rtk_proxy.py` (1.7KB) | Proxy RTK |
| `evolve bench` | `commands/evolve.py` (9.6KB) | Benchmark mutasi aturan A/B |
| `evolve mine-friction` | `commands/evolve.py` | Tambang pola friksi dari learnings |

### 12.3. Utilitas Pendukung

| File | Fungsi |
|:--|:--|
| `utils/ast_parser.py` (4.4KB) | Parser AST universal — ekstrak skeleton kode |
| `utils/evolution_ledger.py` (2.3KB) | Tulis ke `EVOLUTION_LOG.jsonl` |
| `commands/brain.py` (19.5KB) | Mesin RAG: ekspansi query, FTS5 search, Ollama filtering |
| `commands/compile_rules.py` (2.8KB) | Kompilasi aturan Markdown → YAML untuk matrix/ |
| `commands/nano_compressor.py` (2.8KB) | Koneksi Ollama untuk kompresi NanoBrain |
| `commands/scaffold_saas.py` (3.6KB) | Generator scaffold proyek SaaS |

---

# VOLUME VIII: KANON, TEMPLAT, HOOK, EVAL, DAN ARSIP

---

## Bab 13: Kanon Ekosistem (`canons/`)

### 13.1. Struktur 4-Layer
```
canons/
├── ecosystems/         # Framework-specific
│   ├── flutter/        # 16 file kanon (init, debug, release, state-map, ui-patterns, tests, dll.)
│   ├── react/          # 2 file kanon (init, standards)
│   └── python/         # 2 file kanon (init, standards)
├── global/             # Cross-framework
│   ├── core-architecture.md  # Hukum Tata Negara semua proyek
│   ├── ai_brands.json        # Registry IDE yang didukung
│   └── harnesses/            # Skrip verifikasi reusable (action verifier, migration verifier, secrets scan)
├── local/              # Project-specific (kosong di _foundation)
└── micro/              # Cheat-sheet BUDGET models
    ├── pubspec.md      # Ringkasan pubspec.yaml Flutter
    └── supabase.md     # Ringkasan pola Supabase
```

### 13.2. `global/core-architecture.md` — 6 Prinsip Inti
1. **Agent-First Design**: Kode harus mudah diparsing oleh AI.
2. **Predictable Modularity**: Modul terisolasi > monolith.
3. **Distributed Context**: Konteks di root DAN di app-level.
4. **Code-As-Harness**: Offload validasi ke skrip verifier.
5. **Unidirectional Data Flow**: State immutable, mutasi via actions/events.
6. **Strict Verification**: Tidak ada fitur selesai tanpa verifikasi mekanis.

## Bab 14: Templat (`templates/`)

### 14.1. 11 File Template

| Template | Target | Tujuan |
|:--|:--|:--|
| `AGENTS.template.md` (12KB) | Root project (`GEMINI.md`/`CLAUDE.md`) | Generator instruksi multi-AI (sumber DRY) |
| `PROJECT_SCAFFOLD.template.md` (10KB) | Arsitektur & Blueprint | Master prompt untuk scaffold proyek baru + 82-file mapping |
| `MEMORY.template.md` (3.6KB) | State tracking | Pelacakan state SaaS & handoff sesi |
| `TASK_PLANNING.template.md` (3.9KB) | Checklists | Eksekusi, roadmap, atomic tasks |
| `STYLE_GUIDE.template.md` | UI/UX tokens | Panduan gaya visual |
| `ORION_SCHEMA.template.md` (1KB) | Konfigurasi `.orion/` | Skema graph |
| `custom-agent.template.md` (5.4KB) | Agen baru | Scaffold agen AI khusus |
| `custom-rule.template.md` (3.4KB) | Aturan baru | Scaffold behavioral rule |
| `github-native-structure.md` (4.6KB) | GitHub | Panduan struktur folder GitHub kanonik |
| `startup_knowledge_base.md` (2.3KB) | Knowledge | Instruksi auto-populasi domain SaaS |

## Bab 15: Hooks (`hooks/`)

### 15.1. `pre-agent-wake.py` (91 baris | 4KB)
**Omni-Buffer Hook.** Dipanggil oleh IDE sebelum AI memulai giliran. Fungsi:
1. Menerima argumen `--active-file`, `--terminal-error`, `--ide-source`, `--user-intent`.
2. Menulis state ke `context.json` secara atomic (temp file → `os.replace`).
3. Mengecek `LEARNINGS.md` untuk tag `[Darwinian Hook]`. Jika >= 3, set `evolution_overdue = True`.
4. Secara otomatis spawn `orion.py evolve mine-friction` di background.

## Bab 16: Evaluator (`evals/`)

### 16.1. `audit_aesthetics.py` (89 baris | 4.3KB)
**CI/CD Gatekeeper untuk Estetika.** Memindai file `.dart`, `.tsx`, `.jsx`, `.css`:
- **Check 1**: Deteksi warna generik (`Colors.red`, `Colors.blue`). Error: wajib pakai design tokens.
- **Check 2**: Deteksi inline style dengan warna generik. Error.
- **Check 3**: Jika > 5 raw hex codes, warning: ekstrak ke semantic tokens.
- **Check 4**: Jika file adalah komponen UI tapi TIDAK ada primitif animasi (`AnimatedContainer`, `framer-motion`, `transition-all`), warning: tambahkan micro-interactions.

Exit Code 1 = gagal → agen dilarang melanjutkan tanpa perbaikan.

### 16.2. `evals.json` (9.9KB)
Konfigurasi benchmark/evaluasi untuk testing model AI.

## Bab 17: Dokumentasi (`docs/`)

### 17.1. `versioning-changelog-guide.md` (280 baris | 6.8KB)
Pipeline versioning otomatis: Semantic Versioning (`MAJOR.MINOR.PATCH`), CHANGELOG otomatis, sanitasi file sensitif sebelum distribusi, blacklist file yang tidak boleh disinkronkan.

### 17.2. `workflows_guide.md` (1.2KB)
Panduan ringkas tentang cara menggunakan workflows.

### 17.3. `MULTI_AI_DEPLOYMENT.md` (181 bytes)
Catatan tentang deployment ke multiple IDE secara bersamaan.

## Bab 18: Metrics (`metrics/`)
Berisi `README.md` dan `eval_workspace/` — workspace untuk menjalankan evaluasi performa model.

## Bab 19: Archive (`archive/`)
Berisi `README.md` dan `orion_mcp.py` (10.3KB) — implementasi MCP server untuk Orion (legacy/eksperimental).

## Bab 20: File Root `.agents`

### 20.1. `AGENTS_INDEX.md` (4.7KB)
Peta master yang mendaftar semua Rules, Skills, Workflows, dan Canons dengan path relatif.

### 20.2. `DEPLOY_ME.md` (4.3KB)
Instruksi plug-and-play untuk mendeploy Foundation ke proyek baru. Mencakup:
- Q&A wajib (framework, language).
- Gitignore pre-flight.
- Perintah eksekusi: `python .agents/scripts/orion.py foundation deploy --target ... --framework ... --language ...`
- Safe Auto-Ingest (dilarang keras ingest root directory).

### 20.3. `LEARNINGS.md` (3.7KB)
**Memori kolektif.** Format YAML per entry: `date`, `task_id`, `tier`, `severity`, `issue`, `root_cause`, `solution`, `debt_warning`. Berisi post-mortem nyata (VRAM OOM, workflow violation, smart ingest architecture).

### 20.4. `EVOLUTION_LOG.jsonl`
Buku besar genom append-only. Setiap mutasi, bug fix, dan pola terekstrak ditulis sebagai baris JSON:
```json
{
  "timestamp": "2026-06-12T14:30:00Z",
  "mutation": "Banned usage of generic 'any' type in TS DTOs.",
  "friction_source": "Runtime crash on malformed JSON payload.",
  "fitness_delta": "+15%",
  "genome_hash": "a1b2c3d4e5"
}
```

### 20.5. `.genome.json` (139 bytes)
Fingerprint genom yang bisa diimpor ke proyek baru agar AI langsung mewarisi pelajaran masa lalu.

### 20.6. `.project_manifest.json` (70 bytes)
Metadata proyek: framework, language, nama proyek.

### 20.7. `.deployed_ais` (414 bytes)
Registry IDE yang sudah menerima deployment Foundation.

### 20.8. `.foundation_path` (47 bytes)
Path absolut ke repo `_foundation`. Digunakan oleh skrip deployment.

---

# VOLUME IX: SIKLUS HIDUP EVOLUSI DARWINIAN

---

## Bab 21: Penambangan Friksi (Friction Mining)

### 21.1. Mekanisme
1. AI membuat error → terminal mengembalikan Exit Code > 0.
2. Error ditulis ke `LEARNINGS.md` dengan tag `[Darwinian Hook]`.
3. `pre-agent-wake.py` menghitung jumlah tag. Jika >= 3: `evolution_overdue = True`.
4. Di giliran berikutnya, BIOS (`GEMINI.md` §1.7) memaksa agen menjalankan `evolve mine-friction`.
5. Agen menganalisis pola kesalahan, menulis post-mortem, dan mengajukan aturan pencegahan.

### 21.2. Canary Deployment & Fitness Scoring
Aturan baru tidak langsung diterapkan. Melalui `orion.py evolve bench`:
1. **Fork**: `cp SKILL.md SKILL-v2.md`
2. **Benchmark V1**: Uji AI dengan aturan lama pada tugas dummy.
3. **Benchmark V2**: Uji AI dengan aturan baru pada tugas yang sama.
4. **Fitness Score**: Bandingkan — token terpakai, kecepatan, Exit Code.
5. **Promosi**: Jika `score(V2) >= score(V1)`, gabungkan. Jika gagal, arsipkan (jangan hapus).

### 21.3. Buku Besar Genom
`EVOLUTION_LOG.jsonl` mencatat setiap mutasi secara permanen. Saat Foundation diterapkan ke proyek baru, buku besar ini diimpor → AI di proyek baru langsung mewarisi semua pelajaran.

---

# VOLUME X: ALUR DEPLOYMENT KE PROYEK BARU

---

## Bab 22: Prosedur Deployment Lengkap

### 22.1. Langkah 1: Identifikasi Target & Stack
AI wajib menanyakan framework (`react`, `flutter`, `nextjs`, `python`) dan bahasa (`typescript`, `dart`, `python`) jika `.project_manifest.json` belum ada.

### 22.2. Langkah 2: Gitignore Pre-Flight
AI wajib memastikan `.gitignore` ada dan mencakup `node_modules`, `build`, `.env*`, dsb. Ini mencegah ingest RAG mengindeks sampah biner.

### 22.3. Langkah 3: Eksekusi
```bash
# Deploy ke satu IDE (Gemini default)
python .agents/scripts/orion.py foundation deploy --target /path/to/project --framework flutter --language dart

# Deploy ke beberapa IDE
python .agents/scripts/orion.py foundation deploy --target /path/to/project --framework react --language typescript --ai cursor,copilot

# Deploy ke semua 6 IDE
python .agents/scripts/orion.py foundation deploy --target /path/to/project --framework react --language typescript --ai all
```

### 22.4. Langkah 4: Safe Auto-Ingest
```bash
python .agents/scripts/orion.py orion_ops ingest .agents/rules .agents/skills .agents/canons .agents/workflows context/
```
**DILARANG KERAS**: `ingest .` atau ingest tanpa argumen. Ini bisa membekukan sistem atau menghancurkan database SQLite.

### 22.5. Langkah 5: Sinkronisasi Berkala
```bash
# Sync setelah Foundation diperbarui
python .agents/scripts/orion.py foundation sync-ai --target /path/to/project

# Push perbaikan proyek kembali ke Foundation master
python .agents/scripts/orion.py foundation push-upstream --source /path/to/project
```

---

# VOLUME XI: GLOSARIUM LENGKAP

---

| Istilah | Definisi |
|:--|:--|
| **Agentic Amnesia** | Fenomena di mana AI melupakan instruksi karena konteks terlalu besar atau dimulai ulang |
| **AST Hollowing** | Teknik membaca hanya "rangka tulang" (skeleton) kode sumber, menghapus implementasi detail |
| **AutoHarness** | Pola di mana AI menulis skrip validasi otomatis untuk memverifikasi tindakannya sendiri |
| **Bento-Box Law** | Aturan bahwa model BUDGET hanya boleh mengerjakan 1 file per iterasi |
| **Canary Deployment** | Menguji aturan baru di sandbox sebelum menerapkannya ke produksi |
| **Caveman Protocol** | Mode komunikasi ultra-terse yang menghapus kata sandang dan basa-basi |
| **Context Poisoning** | Degradasi kemampuan AI akibat konteks yang terlalu besar/irrelevan |
| **Darwinian Heartbeat** | Mekanisme cron otomatis yang memicu evolusi saat error menumpuk |
| **Fitness Score** | Metrik benchmark yang membandingkan efisiensi aturan V1 vs V2 |
| **FTS5** | Full Text Search 5 — ekstensi SQLite untuk pencarian teks cepat |
| **Friction Mining** | Proses otomatis mengekstrak pola kesalahan dari log untuk menghasilkan aturan pencegahan |
| **Genome Ledger** | `EVOLUTION_LOG.jsonl` — catatan append-only dari setiap mutasi sistem |
| **Ghost Token** | File atau referensi yang ada di indeks tetapi tidak ada secara fisik |
| **Hard Gate** | Blokir mekanis yang tidak bisa di-bypass oleh AI (contoh: Sequential Tool Ban) |
| **JIT Routing** | Pemuatan aturan/skill secara dinamis berdasarkan kata kunci prompt |
| **Lost in the Middle** | Fenomena degradasi atensi AI pada konten di bagian tengah konteks |
| **NanoBrain** | LLM lokal super-kecil (qwen2.5:0.5b) untuk pra-proses dan kompresi |
| **Omni-Buffer** | `context.json` — file sinkronisasi state IDE real-time |
| **RTK** | Rust Token Killer — proxy terminal yang menghemat 60-90% token |
| **Skeleton-First Law** | Aturan yang melarang pembacaan penuh file >200 baris oleh model BUDGET |
| **Stale Data Guard** | Mekanisme yang membuang data `context.json` jika lebih tua dari 5 menit |
| **Triplet Semantik** | Relasi `Subject-Predicate-Object` yang diekstrak dari kode sumber |
| **Tier Mismatch** | Kondisi di mana model yang aktif lebih lemah dari tier yang dibutuhkan tugas |
| **82-File Mandate** | Kebijakan penamaan konteks berdasarkan 82 domain file SaaS standar |

---

# VOLUME XII: DIAGRAM ARSITEKTUR VISUAL

---

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           PORTABLE BRAINVIBING                               │
│                                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────────────────────┐ │
│  │  GEMINI.md   │───→│ JIT Routing  │───→│ Skill/Rule/Workflow Loading     │ │
│  │  (BIOS)      │    │ Table (§4)   │    │ (Dynamic, on-demand)            │ │
│  └──────┬───────┘    └──────────────┘    └──────────────────────────────────┘ │
│         │                                                                     │
│         ▼                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────────────┐ │
│  │ context.json │───→│ pre-agent-   │───→│ Darwinian Heartbeat             │ │
│  │ (Omni-Buffer)│    │ wake.py      │    │ (Auto-Evolution Trigger)         │ │
│  └──────────────┘    └──────────────┘    └──────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                        .agents/ (The Brain)                           │   │
│  │  ┌────────┐ ┌────────┐ ┌──────────┐ ┌───────┐ ┌─────────┐ ┌──────┐  │   │
│  │  │ rules/ │ │skills/ │ │workflows/│ │canons/│ │scripts/ │ │evals/│  │   │
│  │  │ (10)   │ │ (16)   │ │  (10)    │ │ (4)   │ │ (16+)   │ │ (2)  │  │   │
│  │  └────────┘ └────────┘ └──────────┘ └───────┘ └─────────┘ └──────┘  │   │
│  │  ┌─────────┐ ┌──────┐ ┌──────────┐ ┌────────────────────────────┐   │   │
│  │  │templates│ │hooks/│ │  docs/   │ │ LEARNINGS.md + EVOLUTION   │   │   │
│  │  │  (11)   │ │ (1)  │ │  (3)     │ │        _LOG.jsonl          │   │   │
│  │  └─────────┘ └──────┘ └──────────┘ └────────────────────────────┘   │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                       .orion/ (The Memory)                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌────────────┐  │   │
│  │  │ orion.db │ │ index.md │ │ sources/ │ │ matrix/ │ │  working/  │  │   │
│  │  │ (SQLite) │ │ (135 idx)│ │(118 docs)│ │ (YAML)  │ │context.json│  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └─────────┘ └────────────┘  │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────┐    ┌──────────────────────────┐                   │
│  │  RTK (Rust Binary)   │    │  NanoBrain (Ollama/0.5b) │                   │
│  │  Terminal Proxy       │    │  Query Expansion + Filter │                   │
│  │  Token Savings: 60-90%│    │  Episodic Memory Compress │                   │
│  └──────────────────────┘    └──────────────────────────┘                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

*Akhir Ensiklopedia Utama. Dokumen ini mencakup 12 Volume, 22 Bab, seluruh 10 file aturan, 16 skill, 10 workflow, 16+ skrip Python, 11 template, dan semua komponen pendukung ekosistem Portable Brainvibing. Framework ini mengubah LLM dari chatbot percakapan probabilistik menjadi instrumen rekayasa deterministik yang berevolusi sendiri secara mekanis.*
