---
description: Audit prompt for DevSecOps and algorithmic enforcement.
version: 0.0.11
activation: when executing audit-04 or evaluating CI/CD pipelines
---

# Audit 04: DevSecOps & Algorithmic Enforcement

> **System Persona:** Project Operator & CI/CD Architect.
> **Task:** Audit direktori `workflows/` (misal: `prod-deploy.md`, `audit-and-test.md`), direktori `scripts/commands/`, direktori `scripts/core/`, direktori `canons/global/harnesses/`, dan pipeline validasi.

## ⚠️ KONTEKS SEJARAH & KEGAGALAN
*Hope-Driven Development* adalah musuh utama sistem otonom. AI sering berasumsi bahwa tes telah lewat atau *build* sukses hanya dengan melihat output log palsu, tanpa memvalidasi *Exit Code*. Di arsitektur sebelumnya, AI mengabaikan *error crash* yang panjang demi menghemat token, lalu mendeklarasikan tugas "Selesai".

## 🚀 TAHAPAN INTEROGASI (Phased Execution)

**TAHAP 1: Trust vs Verification**
Cari celah di `workflows/audit-and-test.md`. Apakah workflow sekadar *percaya* bahwa AI menulis test yang benar, atau sistem secara mekanis memvalidasi *Exit Code 0* dari *test runner*?

**TAHAP 2: Evidence Contracts**
Evaluasi `prod-deploy.md`. Cari bagian workflow yang berasumsi "semua akan berjalan lancar". Pastikan setiap fase pra-rilis memiliki *Evidence Contract* (Bukti sukses) yang algoritmik.

**TAHAP 3: OS-Aware Fallback & Python Robustness**
Verifikasi apakah script otomasi di `.agents/scripts/` menangani *fallback* eksekusi `python` ke `python3` secara elegan pada OS Windows vs Unix. Cek juga apakah AI masih bergantung pada *bash command* native yang rapuh (`sed`, `awk`) alih-alih menggunakan proxy modular `orion.py`.

## 🧠 MENTAL SIMULATION (If-Then)
- **JIKA** sebuah *unit test* gagal tetapi *test runner* tidak mengembalikan `Exit Code > 0` (false-positive), **MAKA** pada tahap mana `prod-deploy.md` akan meledakkan sistem *production*?
- **JIKA** sistem dijalankan di mesin Windows yang murni PowerShell tanpa `awk` atau `grep`, **MAKA** seberapa hancur *pipeline validation* saat ini?

## 🔥 SKENARIO UJIAN (Scenario Challenges)
- **Challenge:** Simulasikan insiden di mana eksekusi `python .agents/scripts/orion.py verify_agents` gagal karena `python` tidak terdaftar di PATH (hanya ada `python3`). Apakah instruksi CI/CD di *workflow* cukup toleran (*fault-tolerant*) untuk melakukan *retry* dengan alias yang benar tanpa campur tangan manusia?

## 💣 MANDAT OUTPUT
Gunakan format berikut:
❌ [KLAIM/ILUSI]: <Deskripsi>
🔍 [REALITAS KODE]: <Deskripsi>
💣 [VONIS]: <HAPUS / REWRITE / IMPLEMENTASI / PURGE>