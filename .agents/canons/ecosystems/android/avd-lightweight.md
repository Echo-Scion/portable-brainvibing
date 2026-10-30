---
activation: model_decision
description: Operational profile for 8GB RAM development hosts, ultra-lightweight AVD execution, and Gradle memory caps.
last_updated: 2026-10-29
---

# Ultra-Lightweight Android Environment & 8GB RAM Profile

> **Opt-In Module**: Recommended for development environments operating on resource-constrained hosts ($\le 8\text{ GB}$ RAM).

## 1. Host Memory Conservation (8GB RAM Safeguard)
On 8 GB RAM machines, concurrent compilation, IDE indexing, and full emulation quickly exhaust available memory. Operators and agents MUST enforce:
1. **Gradle Memory Limits**:
   In `~/.gradle/gradle.properties`:
   ```properties
   org.gradle.jvmargs=-Xmx1536m -XX:MaxMetaspaceSize=512m
   org.gradle.parallel=false
   org.gradle.caching=true
   org.gradle.configureondemand=true
   ```
2. **Device Selection Priority**:
   - **Tier 1 (Optimal)**: Physical Android device via USB/Wi-Fi (`adb devices`). Zero RAM impact on the host. Mirror via Antigravity **Android Device Hub**.
   - **Tier 2 (UI Loop)**: Android Compose Preview sidecar (`@Preview`).
   - **Tier 3 (Lightweight AVD)**: Dedicated low-spec AVD (`AVD_Ringan_API30`).

---

## 2. Optimized Emulator Execution Modes

When emulator execution is required, use the lightweight profile (`AVD_Ringan_API30` - AOSP, 1024 MB RAM, 128 MB heap) with the following command patterns:

### A. Headless Mode (Zero Window Render - Maximum RAM Savings ⭐)
Runs the emulator process in the background without allocating native Windows rendering surfaces. Screen interaction occurs through Antigravity **Android Device Hub**:
```cmd
"%LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe" -avd AVD_Ringan_API30 -no-window -no-audio -no-boot-anim
```

### B. Fast Windowed Mode (Standard UI with Boot Acceleration)
Skips boot animation and disables expensive snapshot writes upon closing:
```cmd
"%LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe" -avd AVD_Ringan_API30 -no-boot-anim -no-snapshot-save
```

### C. Android CLI Native Dispatcher
```cmd
android emulator start AVD_Ringan_API30
```
