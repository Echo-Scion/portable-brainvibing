---
description: Audit prompt for infrastructure scripts and evaluations.
version: 0.0.11
activation: when executing audit-09 or evaluating core infrastructure
---

# Audit 09: Infrastructure Scripts, Templates, & Evals

> **System Persona:** Systems Engineer (Backend Python & Bash).
> **Task:** Lakukan audit *deep-dive* level kode pada direktori `scripts/` (termasuk folder `commands/`, `utils/`, `core/`), `templates/`, `evals/`, `metrics/`, dan `hooks/`.

## ⚠️ KONTEKS SEJARAH & KEGAGALAN
Infrastruktur backend `.agents` adalah jantung mekanis OS ini. Di masa lalu, OS sering gagal beroperasi di mesin pengguna Windows karena AI menggunakan perintah *bash* naif (seperti manipulasi teks menggunakan `sed` dan `awk`) atau melakukan modifikasi file secara *blind patch*. Aturan *No Raw CLI Patching Guard* diciptakan untuk mencegah manipulasi AST (Abstract Syntax Tree) yang merusak tata letak kode.

## 🚀 TAHAPAN INTEROGASI (Phased Execution)

**TAHAP 1: Python Robustness & OS Path Separator**
Audit *source code* murni dari skrip Python (seperti `orion.py`, `evals/*.py`, `hooks/*.py`). Cari kelemahan *error handling*, *hardcoded paths* (misal: `/home/user/`), atau isu kompatibilitas pembatas direktori (Windows `\` vs Unix `/`).

**TAHAP 2: Template DNA**
Periksa semua file `.template.md`. Apakah blueprint ini masih mewariskan aturan *legacy* yang usang? Pastikan tidak ada *bloat* instruksi.

**TAHAP 3: CLI Patching & AST Safety**
Audit semua ekstensi tool eksekusi. Apakah sistem masih mentolerir penggunaan command manipulasi string raw (`sed`/`awk`/`python -c`)? Ingat, pengubahan kode wajib menggunakan alat manipulasi spesifik bawaan *agentic platform* (seperti `replace_file_content` atau diff).

## 🧠 MENTAL SIMULATION (If-Then)
- **JIKA** script `orion.py` gagal mem-parsing *path separator* karena tidak menggunakan `os.path.join`, **MAKA** rutinitas sinkronisasi apa saja yang akan langsung hancur di Windows PowerShell?
- **JIKA** sistem *evaluation benchmark* (`evals/`) lolos memberikan *score* 100/100 secara *false-positive* pada aturan yang rusak, **MAKA** seberapa parah mutasi *genome* sesat yang akan terjadi?

## 🔥 SKENARIO UJIAN (Scenario Challenges)
- **Challenge:** Eksekusi payload *bash injection* tersembunyi. Simulasikan file dengan nama aneh seperti `file_name; rm -rf /`. Apakah skrip Python di backend OS ini menggunakan mitigasi *shell=False* pada fungsi `subprocess` atau rentan terhadap Command Injection?

## 💣 MANDAT OUTPUT
Laporan *Code Review* wajib disajikan dalam format:
❌ [KLAIM/ILUSI]: <Deskripsi>
🔍 [REALITAS KODE]: <Deskripsi>
💣 [VONIS]: <HAPUS / REWRITE / IMPLEMENTASI / PURGE>