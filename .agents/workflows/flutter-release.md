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

If any of these fail, ABORT the release and fix the errors first.

## 2. Build Commands

### Android (Google Play)
For Google Play, an App Bundle is required.
```bash
flutter build appbundle --release
```
*Output: `build/app/outputs/bundle/release/app-release.aab`*

If an APK is needed for direct distribution/testing:
```bash
flutter build apk --release
```
*Output: `build/app/outputs/flutter-apk/app-release.apk`*

### iOS (App Store)
*Note: Requires macOS and Xcode.*
```bash
flutter build ipa --release
```
*Output: `build/ios/ipa/` (Contains the .ipa file)*

### Web (Firebase Hosting / Vercel)
```bash
flutter build web --release --wasm
```
*Output: `build/web/`*

## 3. Post-Build Instructions
If the user asks what to do next:
- **Android**: Provide instructions to upload the `.aab` file to the Google Play Console -> Production / Closed Testing track.
- **iOS**: Provide instructions to open Transporter app and upload the `.ipa` file to App Store Connect.
- **Web**: Run `firebase deploy --only hosting` or drag-and-drop the `build/web/` folder to Vercel/Netlify.
