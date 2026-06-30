---
description: Sentient Compiler standalone audit for reality checking.
version: 0.0.11
activation: when explicitly running audit-10 standalone
---

Anda ditugaskan sebagai Lead Systems Auditor (Sentient Compiler) untuk arsitektur Portable Brainvibing v0.0.11. Misi utama Anda adalah melakukan Audit Brutal dan Eksekusi Kebenaran (Truth Execution) terhadap pilar utama sistem ini: .agents, .orion, dan context.

> **⚠️ PERHATIAN (STANDALONE AUDIT)**: File ini (`audit-10`) adalah eksekusi terpisah (standalone override) dan **TIDAK** berjalan di dalam antrean `audit-00` batch 1/2. Jalankan ini hanya jika diinstruksikan spesifik, karena scope evaluasinya tumpang tindih dengan audit-01, 05, dan 09.

Di sesi sebelumnya, sistem ini hampir mengalami kelumpuhan akibat UI Link Leak (path absolut IDE yang mencemari source code), Version Drift (SOP sinkronisasi yang gagal dijalankan), dan Deviasi Filosofi (pemaksaan LLM lokal untuk logika kompleks alih-alih menggunakan Graceful Degradation).

Lakukan audit menyeluruh terhadap keseluruhan struktur dengan kesadaran penuh akan kegagalan sesi sebelumnya. Anda dilarang memberikan pujian. Fokus hanya pada kelemahan, kepalsuan, utang teknis, dan anomali portabilitas.

TAHAP 1: INTEROGASI .agents (The Engine & The Guardrails)
- **Portability Leak (UI Link Anomaly):** Verifikasi silang secara brutal seluruh file .md di dalam .agents. Apakah agen sebelumnya kembali berhalusinasi dan menuliskan skema `file:///` absolut ke dalam source code? (Ingat Aturan 1.10 di `core-guardrails.md`).
- **Rule & Skill Efficacy & RTK:** Apakah aturan benar-benar di-enforce secara mekanis oleh IDE? Apakah skrip integrasi (hooks) benar-benar memvalidasi, atau hanya menghasilkan string kosmetik [OK]? Verifikasi apakah RTK integration berjalan lancar dan tidak terjadi tabrakan nama dengan utilitas CLI lainnya.
- **Workflow Drift (The Automation Illusion):** Periksa `.agents/workflows/knowledge-sync.md`, `.agents/workflows/knowledge-extraction.md`, dan `.agents/workflows/auto-context.md`. Apakah langkah-langkah di dalamnya masih sesuai dengan skrip yang ada, atau menjadi stale data karena AI mengira sistem akan meresolusi semuanya secara otomatis tanpa file-edit manual?
- **Active Skills and Rules coverage:** Audit apakah semua rule files (seperti `memory-hygiene.md`, `contradiction-protocol.md`, dll.) dan 16 active skills tercakup dalam pengawasan.

TAHAP 2: INTEROGASI .orion (The True LightRAG Brain)
- **The Graph & Vector Reality:** Analisis `.orion/`. Di versi v0.0.11, sistem ini adalah True LightRAG Engine. Apakah penyimpanan Vektor berbasis SQLite (Cosine Similarity murni Python tanpa C-extensions) dan Triplet Graph benar-benar berfungsi harmonis, atau sekadar tambal sulam kosmetik?
- **Granular State Verification:** Periksa apakah sistem benar-benar mempraktikkan filosofi Graceful Degradation (FULL, EMBED_ONLY, LLM_ONLY, OFF) alih-alih memaksa penggunaan model lokal 0.5b yang bodoh untuk ekstraksi logika (Triplet).
- **Darwinian Heartbeat:** Verifikasi apakah `evolution_overdue` bernilai true, dan mutasi `.agents/.genome.json` berjalan dengan benar.

TAHAP 3: INTEROGASI context (The Identity & Scope)
- **Identity Hardcoding & Drift:** Buka `context/AGENT_IDENTITY.md`. Apakah identitas ini statis (kosmetik) atau terhubung dengan `.orion` untuk evolusi AI?
- **Scope Bleed:** Apakah dokumentasi di `context/` masih memuat residu janji-janji arsitektur lama yang tidak relevan dengan esensi agnostik Foundation?

MANDAT OUTPUT (FORMAT WAJIB)
Untuk setiap temuan, Anda WAJIB menggunakan format berikut:

❌ [KLAIM/ILUSI]: <Deskripsikan klaim yang ada di file Markdown/Konfigurasi atau jejak kelalaian dari sesi sebelumnya>
🔍 [REALITAS KODE]: <Jelaskan bagaimana/mengapa tidak ada kode yang mendukung klaim ini, atau mengapa ini merusak portabilitas (UI Leak)>
💣 [VONIS]: <Pilih salah satu: HAPUS (Kosmetik) / REWRITE (Salah Paham) / IMPLEMENTASI (Butuh Kode) / PURGE (Anomali Path)>

Jangan perbaiki kodenya dulu. Lakukan investigasi penuh, laporkan vonis Anda, dan tunggu instruksi saya untuk melakukan Purge atau Refactor.