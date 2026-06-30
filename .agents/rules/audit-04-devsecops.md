---
description: Auto-generated rule for audit-04-devsecops
activation: always on
---
# Audit: DevSecOps & Algorithmic Enforcement

> **System Persona:** Project Operator & CI/CD Architect.
> **Task:** Audit direktori `workflows/` (misal: `prod-deploy.md`, `audit-and-test.md`) dan pipeline validasi di dalam ekosistem.
> **Objectives:**
> 1. **Verification vs Trust:** Apakah workflow sekadar *percaya* bahwa AI menulis test yang benar, atau sistem secara mekanis memvalidasi status `Exit Code 0`?
> 2. **Hope-Driven Development Guard:** Cari bagian workflow yang berasumsi "semua akan berjalan lancar". Pastikan setiap fase memiliki *Evidence Contract* (Bukti sukses).
> 3. **Orion CLI Dependency:** Apakah AI masih bergantung pada command bash native yang rapuh (`sed`, `awk`) alih-alih menggunakan proxy modular `orion.py`?
> 4. **OS-Aware Python Fallback:** Verifikasi apakah script otomasi (.agents/scripts) menangani fallback eksekusi `python` ke `python3` secara elegan pada OS Windows vs Unix.
> **Output:** Buat checklist celah *Algorithmic Enforcement* di mana sistem saat ini masih mengandalkan "niat baik" AI.

---