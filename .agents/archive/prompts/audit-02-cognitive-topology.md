---
description: Audit prompt for cognitive topology and memory routing.
version: 0.0.11
activation: when executing audit-02 or evaluating agent routing
---

# Audit 02: Cognitive Topology & Routing (The Synapse Check)

> **System Persona:** Meta-Cognitive Architect (`meta-agent-admin`).
> **Task:** Audit mekanisme *JIT (Just-In-Time) Knowledge Routing* dan koneksi file di seluruh arsitektur.

## ⚠️ KONTEKS SEJARAH & KEGAGALAN
Arsitektur sebelumnya menderita *Agentic Schizophrenia* dan *Ghost Routing*, di mana agen memanggil instruksi atau *persona* yang tidak eksis, atau tumpang tindih dengan peran lain. Routing di `GEMINI.md` harus menjadi peta jalan yang absolut dan tidak mentolerir ambiguitas.

## 🚀 TAHAPAN INTEROGASI (Phased Execution)

**TAHAP 1: JIT Signal Tracing**
Simulasikan *routing* dari tabel JIT di `GEMINI.md`. Jika user meminta "buat fitur otentikasi baru", petakan persis file apa saja yang di-load secara mekanis. Apakah ada "Dead Ends" (jalan buntu) di mana file yang dirujuk sebenarnya tidak ada?

**TAHAP 2: Synapse Validation (16 Skills)**
Buka `AGENTS_INDEX.md` dan verifikasi keberadaan 16 active skills. Identifikasi aturan yang masih bersifat *passive text* (contoh: "jangan lupa cek X"). Catat sebagai temuan agar diubah menjadi mekanis (contoh: "jalankan grep pada X").

**TAHAP 3: Trigger Loop & Cohesion Check**
Apakah ada tumpang tindih (overlap) peran di antara 16 active skills yang bisa memicu *Agentic Schizophrenia*? Pastikan tabel JIT tidak memicu infinite trigger loop.

## 🧠 MENTAL SIMULATION (If-Then)
- **JIKA** *skill* `ui-finish` memiliki insting yang sama dengan `frontend-experience` saat menangani layout error, **MAKA** apa potensi loop yang terjadi jika keduanya saling memanggil aturan yang berbeda?
- **JIKA** user memberikan perintah yang sangat ambigu (misalnya "perbaiki ini"), **MAKA** file JIT mana yang akan bertindak sebagai *fallback routing*?

## 🔥 SKENARIO UJIAN (Scenario Challenges)
- **Challenge:** Simulasi permintaan ambigu: "Sistem saya terasa lambat, tolong dioptimasi." Uji apakah sistem mengalami *Ghost Routing* atau apakah tabel JIT berhasil mendelegasikan tugas ini tepat ke `performance-optimization.md` atau `cost-optimizer` tanpa memicu pencarian file acak yang menghabiskan token.

## 💣 MANDAT OUTPUT
Buat *Gap Analysis* dari topologi routing otak agen.
❌ [KLAIM/ILUSI]: <Deskripsi>
🔍 [REALITAS KODE]: <Deskripsi>
💣 [VONIS]: <HAPUS / REWRITE / IMPLEMENTASI / PURGE>