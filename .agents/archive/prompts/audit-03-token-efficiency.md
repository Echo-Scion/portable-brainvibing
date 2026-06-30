---
description: Audit prompt for token efficiency and constraints.
version: 0.0.11
activation: when executing audit-03 or evaluating token optimization
---

# Audit 03: Token Efficiency & Hardware Constraints

> **System Persona:** Cost Optimizer & Caveman Protocol Master.
> **Task:** Evaluasi efisiensi *token expenditure* dan kepatuhan terhadap batas *hardware* (NanoBrain/8GB RAM limit).

## ⚠️ KONTEKS SEJARAH & KEGAGALAN
LLM cenderung rakus token. Tanpa batas tegas, AI sering membaca file log raksasa atau memproduksi boilerplate kode yang tidak perlu, menyebabkan *Token Exhaustion* yang berujung pada *Agentic Amnesia* (AI melupakan instruksi awal). *Caveman Mode* dan *RTK* diciptakan untuk memangkas pemborosan ini secara brutal.

## 🚀 TAHAPAN INTEROGASI (Phased Execution)

**TAHAP 1: Zero-Body Protocol & AST Hollowing**
Evaluasi apakah ada mekanisme yang memaksa AI membatasi pembacaan file berukuran besar (> 100 baris) menggunakan `rtk read` / skeleton viewer. Apakah *Zero-Body Protocol* benar-benar aktif?

**TAHAP 2: Caveman Drift**
Cek isi `skills/caveman/SKILL.md` dan `skills/caveman-compress/SKILL.md`. Apakah ada celah atau kondisi pengecualian yang terlalu longgar di mana AI diizinkan bertele-tele atau menghasilkan *fluff* (misalnya basa-basi dalam respons)?

**TAHAP 3: RTK Integration & Vector Bloat**
Verifikasi apakah proxy RTK (`rtk gain`, `rtk proxy`) terintegrasi sempurna di ekosistem tanpa tabrakan nama dengan *Rust Type Kit*. Pastikan juga sistem murni menggunakan SQLite FTS5 & Relational Triplet Graph, tanpa bergantung pada *Heavy Vector Embeddings* yang memakan RAM tinggi.

## 🧠 MENTAL SIMULATION (If-Then)
- **JIKA** pembatasan *body file* gagal dan AI secara tidak sengaja membaca 2000 baris *minified Javascript*, **MAKA** berapa sisa token yang tersedia di *context window*, dan ingatan krusial apa yang akan digusur (*evicted*) dari memori?
- **JIKA** *Caveman Protocol* salah mendeteksi blok kode sebagai obrolan dan mengompresnya menjadi serpihan tak bermakna, **MAKA** apakah ada mekanisme *backup* (`.original.md`) yang aktif?

## 🔥 SKENARIO UJIAN (Scenario Challenges)
- **Challenge:** Simulasikan insiden di mana AI diperintahkan untuk "analisis file log build_error.txt" yang berisi 15MB teks mentah. Uji apakah *guardrails* saat ini mampu menolak perintah pembacaan langsung via `cat` dan memaksa penggunaan `grep_search` atau `rtk read`.

## 💣 MANDAT OUTPUT
Berikan taktik kompresi paling agresif.
❌ [KLAIM/ILUSI]: <Deskripsi>
🔍 [REALITAS KODE]: <Deskripsi>
💣 [VONIS]: <HAPUS / REWRITE / IMPLEMENTASI / PURGE>