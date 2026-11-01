---
description: Concrete steps to build and release a Flutter application to production (Android/iOS/Web).
---

# Workflow: Flutter Release (`/flutter-release`)

Follow these concrete steps when the user asks to build or release the application.

## 1. Pre-Flight Checks
Execute these commands to ensure the codebase is clean:

```bash
dart format --set-exit-if-changed .
flutter analyze --fatal-infos --fatal-warnings
flutter test
```

If any of these fail, STOP the release and fix the errors first.

## 2. Hardened Production Build Commands

> [!IMPORTANT]
> **OBFUSCATION MANDATE**: Production binaries MUST be built with Dart AOT obfuscation and symbol splitting to strip class, method, and variable names from the compiled binary. Never ship unobfuscated release builds to app stores. See [`flutter-app-hardening.md`](flutter-app-hardening.md) for full security controls.

### Android (Google Play)
For Google Play, an App Bundle with symbol splitting is required:
```bash
flutter build appbundle --release --obfuscate --split-debug-info=build/symbols
```
*Output: `build/app/outputs/bundle/release/app-release.aab`*  
*Symbols: `build/symbols/` (Quarantine immediately — do NOT commit to git or publish)*

If an APK is needed for direct distribution/testing:
```bash
flutter build apk --release --obfuscate --split-debug-info=build/symbols
```
*Output: `build/app/outputs/flutter-apk/app-release.apk`*

### iOS (App Store)
*Note: Requires macOS and Xcode.*
```bash
flutter build ipa --release --obfuscate --split-debug-info=build/symbols
```
*Output: `build/ios/ipa/` (Contains the .ipa file)*  
*Symbols: `build/symbols/` (Archive with release tag for dSYM crash de-obfuscation)*

### Web (Firebase Hosting / Vercel)
```bash
flutter build web --release --wasm
```
*Output: `build/web/`*

## 3. Pre-Release Hardening Checklist
Before distributing binaries, verify against [`flutter-app-hardening.md`](flutter-app-hardening.md):
- [ ] **Symbols Quarantined**: `build/symbols` archived to secure offline storage and omitted from distribution artifacts.
- [ ] **No Hardcoded Secrets**: Zero API keys or cloud credentials in Dart source (all keys loaded via hardware Keystore or environment).
- [ ] **Certificate Pinning**: Sensitive network endpoints protected via custom `SecurityContext`.
- [ ] **Integrity Attestation**: Play Integrity API / DeviceCheck active on sensitive backend endpoints.

## 4. Post-Build Instructions
If the user asks what to do next:
- **Android**: Provide instructions to upload the `.aab` file to the Google Play Console -> Production / Closed Testing track.
- **iOS**: Provide instructions to open Transporter app and upload the `.ipa` file to App Store Connect.
- **Web**: Run `firebase deploy --only hosting` or drag-and-drop the `build/web/` folder to Vercel/Netlify.
