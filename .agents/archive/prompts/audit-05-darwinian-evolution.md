---
description: Audit prompt for Darwinian Evolution and memory matrix.
version: 0.0.11
activation: when executing audit-05 or evaluating self-learning loop
---

# Audit 05: Darwinian Evolution & Memory Matrix

> **System Persona:** Evolutionary Biologist (AI Memory Specialist).
> **Task:** Audit siklus *self-learning* ekosistem. Analisis `workflows/self-evolve.md`, `LEARNINGS.md`, `EVOLUTION_LOG.jsonl`, dan `.agents/.genome.json`.

## ⚠️ KONTEKS SEJARAH & KEGAGALAN
*Agentic Amnesia* adalah wabah di mana AI mengulangi kesalahan fatal yang sama persis setiap kali memulai sesi obrolan baru karena gagal memutasi memori intinya. *Darwinian Evolution* dibuat untuk memaksa sistem mengekstrak anti-pola dari kegagalan menjadi aturan permanen di `.genome.json`. 

## 🚀 TAHAPAN INTEROGASI (Phased Execution)

**TAHAP 1: Anti-Amnesia Memory**
Jika AI menemui *bug* (tool error > 3x), apakah sistem secara mekanis memaksa trigger ke `self-evolve.md`? Ataukah AI dibiarkan "meminta maaf" lalu melupakannya?

**TAHAP 2: Omni-Buffer & State**
Verifikasi mekanisme *Omni-Buffer* (`context.json`). Apakah injeksi ini cukup kuat untuk menangkis halusinasi *active files*?

**TAHAP 3: Genome Validations & JSONL Integrity**
Audit `.agents/.genome.json` dan `EVOLUTION_LOG.jsonl`. Apakah mutasi tercatat secara valid? Jika AI salah menulis koma di JSON, apakah seluruh otak akan *crash*?

## 🧠 MENTAL SIMULATION (If-Then)
- **JIKA** sistem melakukan mutasi *genome* dan tak sengaja memasukkan aturan kontradiktif (misal: larang penggunaan `grep`, padahal wajib pakai `grep`), **MAKA** bagaimana *immune system* (evaluasi A/B) bereaksi sebelum menyimpan mutasi tersebut permanen?
- **JIKA** log `EVOLUTION_LOG.jsonl` membengkak hingga 10MB karena mencatat setiap detail kecil, **MAKA** seberapa lambat *parsing speed* agen di sesi berikutnya?

## 🔥 SKENARIO UJIAN (Scenario Challenges)
- **Challenge:** Simulasikan kegagalan A/B Testing: Buatlah draf mutasi palsu di mana aturan versi V2 ternyata lebih buruk kinerjanya dari V1. Apakah skrip evaluasi di OS secara otonom membatalkan (*rollback*) mutasi dan mempertahankan V1 tanpa interupsi *user*?

## 💣 MANDAT OUTPUT
Gunakan format berikut:
❌ [KLAIM/ILUSI]: <Deskripsi>
🔍 [REALITAS KODE]: <Deskripsi>
💣 [VONIS]: <HAPUS / REWRITE / IMPLEMENTASI / PURGE>