---
description: Master workflow for sequential execution of audits 01-09.
version: 0.0.11
activation: when user requests a full ecosystem audit
---

# 00: Ecosystem Omni-Context Master Workflow

> **System Persona:** Lead Auditor (Autonomous Audit Orchestrator)
> **Task:** Lakukan eksekusi berantai (chained execution) untuk audit ekosistem `.agents` mulai dari tahap 01 hingga 09.

## ⚠️ KONTEKS SEJARAH & KEGAGALAN
Ekosistem `.agents` adalah **satu kesatuan otak (Unified Brain)**. Di masa lalu, audit yang terisolasi per file memicu *tech debt* dan *context drift*, di mana agen memperbaiki satu file namun merusak dependensi di file lain. Untuk mencegah AI mengalami *tunnel vision*, Anda bertugas sebagai orkestrator utama yang memaksa kepatuhan terhadap 5 pilar interogasi di setiap sub-audit.

## 🚀 TAHAPAN INTEROGASI (Phased Execution)

**TAHAP 1: Inisialisasi Scratchpad**
Anda WAJIB menginisialisasi sebuah file state sementara (contoh: `AUDIT_STATE.md` di *scratch*). Setiap kali menyelesaikan satu tahap audit, tulis temuan Anda ke dalam file ini. File ini menjadi *rolling context* agar Anda mengingat temuan tahap 01 saat sedang berada di tahap 09. Pastikan path scratch kompatibel dengan OS Windows.

**TAHAP 2: Eksekusi Batch 1 (Audit 01-04)**
Gunakan `view_file` untuk membaca prompt `audit-01` hingga `audit-04`. Anda harus menjalankan secara brutal setiap fase (Mental Simulation & Scenario Challenges) yang ada di dalamnya.
> *JANGAN melakukan refactor kode selama fase ini. Ini murni Graph Discovery.*
Catat hasil ke `AUDIT_STATE.md`. BERHENTI dan minta User mengetik `[DO: CONTINUE]`.

**TAHAP 3: Eksekusi Batch 2 (Audit 05-09)**
Setelah disetujui, jalankan tahap 05 hingga 09 dengan tingkat kebrutalan yang sama.

**TAHAP FINAL: Terminal Reality-Check & Synthesis**
SETELAH tahap 09 selesai, Anda **WAJIB** melakukan uji asumsi di terminal (gunakan `grep_search` atau script diagnostik berbasis python) untuk memverifikasi kebenaran `AUDIT_STATE.md` (contoh: verifikasi versi file secara aktual). SETELAH diverifikasi, barulah buat **Holistic Refactor Blueprint**.

## 🧠 MENTAL SIMULATION (If-Then)
- **JIKA** Anda mengabaikan urutan Batch dan langsung membaca semua file sekaligus, **MAKA** Anda akan mengalami *Token Exhaustion* dan berhalusinasi saat memberikan vonis.
- **JIKA** Anda langsung memperbaiki kode saat menemukan bug di `audit-02`, **MAKA** Anda melanggar *No Premature Fixes rule* dan menghancurkan referensi di `audit-07` yang belum Anda baca.

## 🔥 SKENARIO UJIAN (Scenario Challenges)
- **Challenge:** Bisakah Anda memetakan *Blast Radius* (dampak lintas-file) jika file `core-guardrails.md` dihapus? Buktikan dengan menelusuri dependensi menggunakan IDE Native Tooling (seperti `grep_search` pada direktori rules dan skills).

## 💣 MANDAT OUTPUT
Standarisasi temuan di dalam `AUDIT_STATE.md` WAJIB menggunakan format berikut:
❌ [KLAIM/ILUSI]: <Deskripsi>
🔍 [REALITAS KODE]: <Deskripsi>
💣 [VONIS]: <HAPUS / REWRITE / IMPLEMENTASI / PURGE>