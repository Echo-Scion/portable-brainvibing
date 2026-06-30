---
description: Auto-generated rule for audit-00-master-workflow
activation: always on
---
# 00: Ecosystem Omni-Context Master Workflow

> **System Persona:** Lead Auditor (Autonomous Audit Orchestrator)
> **Task:** Lakukan eksekusi berantai (chained execution) untuk audit ekosistem `.agents` mulai dari tahap 01 hingga 09.

## ⚠️ THE BLIND-CONTEXT PREVENTION PROTOCOL
Ekosistem `.agents` adalah **satu kesatuan otak (Unified Brain)**. Audit yang terisolasi per file akan memicu *tech debt* dan *context drift*. Untuk mencegah AI mengalami *tunnel vision*, Anda WAJIB mematuhi aturan berikut:

1. **No Premature Fixes:** Selama menjalankan tahap 01 hingga 09, Anda **DILARANG KERAS** melakukan refactor, modifikasi, atau memberikan solusi final. Fase 01-09 murni untuk **Graph Discovery & Observasi**.
2. **Rolling Memory (Scratchpad):** Anda WAJIB menginisialisasi sebuah file state sementara (contoh: `AUDIT_STATE.md` di *scratch*). Setiap kali menyelesaikan satu tahap audit, tulis temuan Anda ke dalam file ini. File ini menjadi *rolling context* agar Anda mengingat temuan tahap 01 saat sedang berada di tahap 09. Pastikan path scratch kompatibel dengan OS Windows jika berjalan di lingkungan Windows.
3. **Cross-Reference Mandate (Blast Radius):** Saat mengevaluasi satu file (misal `core-guardrails.md`), Anda tidak boleh memandangnya secara silo. Gunakan tool `grep_search` atau `python .agents/scripts/orion.py brain sync` untuk memetakan skill/workflow lain yang me-referensi atau bergantung pada file tersebut. Catat *Blast Radius* (dampak lintas-file) jika ada perubahan.
4. **OS-Agnostic Tooling (Fallback Protocol):** WAJIB menggunakan tool bawaan IDE (seperti `grep_search` atau `view_file`) untuk observasi. JANGAN menggunakan bash commands mentah (seperti `grep` atau `cat`) karena lingkungan OS User bisa jadi Windows/PowerShell. Gunakan `rtk` (Rust Token Killer) hooks secara transparan untuk optimasi token jika menjalankan CLI.

## 🚀 Execution Rules (Batched Auto-Proceed)
1. **Sequence Mandate:** Anda WAJIB memproses file audit secara berurutan. Perhatian: Hindari redudansi antara `audit-02` dan `audit-07`. Lewati atau gabungkan temuan 07 jika beririsan.
2. **Soft Auto-Proceed (Batching):** Untuk mencegah token burn dan halusinasi berantai, jalankan audit dalam batch. 
   - **Batch 1:** Jalankan tahap 01 hingga 04. Catat ke `AUDIT_STATE.md`. BERHENTI dan minta User mengetik `[DO: CONTINUE]`.
   - **Batch 2:** Setelah disetujui, jalankan tahap 05 hingga 09.
3. **Phase 10 (Terminal Reality-Check & Synthesis):** SETELAH tahap 09 selesai, Anda **WAJIB** melakukan uji asumsi di terminal (gunakan `grep_search` atau script diagnostik berbasis python) untuk memverifikasi kebenaran `AUDIT_STATE.md` (contoh: verifikasi versi file secara aktual). SETELAH diverifikasi, barulah buat **Holistic Refactor Blueprint**.

## 🏁 Trigger Execution
1. Buat/inisialisasi state logger `AUDIT_STATE.md`.
2. Gunakan `view_file` untuk membaca `audit-01-security-guardrails.md`.
3. Mulai observasi batch pertama (01-04), catat cross-reference, lalu berhenti untuk minta konfirmasi.
4. Mulai sekarang.

---