---
description: Audit prompt for project lifecycles and handoff protocols.
version: 0.0.11
activation: when executing audit-08 or evaluating lifecycles
---

# Audit 08: Project Lifecycles & Handoff Protocols

> **System Persona:** Agile Orchestrator.
> **Task:** Audit direktori `workflows/` yang menangani pergerakan proyek (seperti `app-lifecycle.md`, `project-migrate.md`, `session-offload.md`, `orion-ops.md`, `temporal-pulse.md`, `auto-context.md`, `knowledge-extraction.md`, dan `knowledge-sync.md`).

## ⚠️ KONTEKS SEJARAH & KEGAGALAN
Amnesia antar-sesi (Cross-Session Amnesia) adalah penyakit paling mematikan bagi AI IDE. Sesi ditutup tanpa menyimpan status (*state*) yang relevan, atau beban token dibiarkan menumpuk hingga IDE lumpuh. Protokol *Handoff* (serah-terima) diciptakan agar pergantian *shift* antar AI berjalan mulus, di mana setiap sesi mewariskan *rolling context* presisi tanpa sampah memori.

## 🚀 TAHAPAN INTEROGASI (Phased Execution)

**TAHAP 1: Handoff & Amnesia**
Analisis brutal pada `session-offload.md`. Apakah prosedur *context eviction* dan pencatatan *state* di akhir sesi benar-benar *fool-proof*? Apakah agen benar-benar dipaksa membersihkan file statis tak berguna dari *context window*?

**TAHAP 2: Legacy Migration Loopholes**
Cek kelengkapan `project-migrate.md`. Apakah *workflow* ini terlalu longgar sehingga AI bisa salah langkah saat melakukan *onboarding* pada *legacy codebase* raksasa yang belum terpetakan?

**TAHAP 3: Temporal & Graph Sync Mechanics**
Evaluasi `orion-ops.md`, `knowledge-sync.md`, dan `temporal-pulse.md`. Apakah eksekusi siklus evaluasi temporal ini bergantung pada inisiatif acak AI, atau di-trigger secara algoritmik berbasis pencapaian aktivitas?

## 🧠 MENTAL SIMULATION (If-Then)
- **JIKA** *session-offload* tidak mengusir *state* dengan benar, dan AI berikutnya masuk dalam keadaan *token window* tersisa 5%, **MAKA** seberapa fatal efek *Agentic Amnesia* yang terjadi pada arsitektur proyek utama?
- **JIKA** proses ekstraksi *Brain Graph* di `knowledge-extraction.md` keliru menyalin pola kode yang di-deprecate, **MAKA** apakah hal tersebut merusak kualitas generasi dari LightRAG untuk 10 *sprint* ke depan?

## 🔥 SKENARIO UJIAN (Scenario Challenges)
- **Challenge:** Simulasikan insiden *Token Exhaustion* darurat. Buat skenario di mana pengguna mengirim error log sepanjang 120.000 token. Uji instruksi `session-offload.md`—apakah prosedur ini cukup reaktif untuk menyela eksekusi, merangkum *state* penting, dan mengosongkan memori sebelum terjadi kelumpuhan total (crash)?

## 💣 MANDAT OUTPUT
Gunakan format berikut:
❌ [KLAIM/ILUSI]: <Deskripsi>
🔍 [REALITAS KODE]: <Deskripsi>
💣 [VONIS]: <HAPUS / REWRITE / IMPLEMENTASI / PURGE>