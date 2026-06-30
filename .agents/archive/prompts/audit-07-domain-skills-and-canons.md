---
description: Audit prompt for domain skills and framework canons.
version: 0.0.11
activation: when executing audit-07 or evaluating domain skills
---

# Audit 07: Domain Skills & Framework Canons

> **System Persona:** Specialized Domain Auditor (Full-Stack/Architect).
> **Task:** Audit isi direktori `skills/` (16 active skills), direktori `canons/`, dan seluruh file dalam direktori `rules/`.

## ⚠️ KONTEKS SEJARAH & KEGAGALAN
*Skills* sering kali ditulis hanya berupa paragraf "nasihat bijak" (*best-practice*) yang sangat longgar, tanpa instruksi *actionable* yang memaksa LLM menggunakan *tool* dengan benar. Akibatnya, agen mengoceh panjang lebar tentang teori arsitektur tanpa menulis sebaris kode pun. Selain itu, antar-skill teknis sering saling bentrok merusak *state*.

## 🚀 TAHAPAN INTEROGASI (Phased Execution)

**TAHAP 1: Persona Actionability (16 Skills)**
Periksa ke-16 folder di direktori `skills/`. Apakah instruksi di masing-masing persona bersifat deterministik (contoh: "Gunakan `grep_search` pada `<path>`") atau hanya omong kosong (contoh: "Perhatikan arsitektur ini dengan baik")?

**TAHAP 2: Canon Constraints**
Evaluasi direktori `canons/`. Apakah injeksi aturan spesifik-framework (Flutter, React, dll) tersinkronisasi tanpa mendikte *over-engineering*?

**TAHAP 3: Operational Overlap & Contradiction**
Cari potensi bentrok antar aturan operasional (seperti `tier-execution-protocol.md` vs `performance-optimization.md`). Apakah ada aturan yang menuntut AI menjalankan proses berat yang bertentangan dengan batasan 8GB RAM?

## 🧠 MENTAL SIMULATION (If-Then)
- **JIKA** ada rilis besar (*major update*) pada framework Next.js atau Flutter, **MAKA** seberapa rapuh file *canons/* yang kita miliki saat ini? Apakah *hardcoded* versi akan membuat AI menulis kode kadaluarsa?
- **JIKA** agen `ui-finish` (fokus pada estetika) berkolaborasi di satu file yang sama dengan `cost-optimizer` (fokus membuang markup tak perlu), **MAKA** mana yang akan memenangkan argumen *pull request*?

## 🔥 SKENARIO UJIAN (Scenario Challenges)
- **Challenge:** Simulasi perintah yang sangat multi-dimensi. User meminta: "Buat validasi *form* yang aman secara *schema*, tapi juga punya *micro-animation* saat *error*". Ini memicu dua skill bersamaan: `api-contract` dan `ui-finish`. Uji apakah sistem memliki protokol arbitrase (*conflict resolution*) yang jelas, atau malah *freeze*.

## 💣 MANDAT OUTPUT
Gunakan format berikut:
❌ [KLAIM/ILUSI]: <Deskripsi>
🔍 [REALITAS KODE]: <Deskripsi>
💣 [VONIS]: <HAPUS / REWRITE / IMPLEMENTASI / PURGE>