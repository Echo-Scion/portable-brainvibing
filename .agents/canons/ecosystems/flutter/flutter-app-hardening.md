---
activation: on-demand
description: Opt-in security hardening canon for production Flutter releases. Covers AOT binary obfuscation, symbol splitting, keystore security, certificate pinning, and platform integrity attestation.
ecosystem: flutter
---

# Flutter App Hardening & Anti-Reverse Engineering (Opt-In Canon)

This canon defines production security standards for high-stakes, commercial Flutter applications. 

While complete client-side binary protection is theoretically impossible against dedicated reverse engineers, these standards maximize economic cost, defeating 99.9% of vibe-coding cloners, automated APK unpackers, and API sniffers.

---

## 1. Mandatory AOT Compilation & Symbol Stripping

Standard Flutter release builds retain method names, routing strings, and class definitions in machine code. Production builds MUST strip and obfuscate Dart symbols:

### Android Commands
```bash
# Production Google Play AppBundle
flutter build appbundle --release --obfuscate --split-debug-info=build/symbols

# Standalone Production APK
flutter build apk --release --obfuscate --split-debug-info=build/symbols
```

### iOS / macOS Commands
```bash
flutter build ipa --release --obfuscate --split-debug-info=build/symbols
```

### Symbol Archive Quarantine Rule
- The `build/symbols/` directory contains mapping files required to de-obfuscate production stack traces.
- **NEVER** package `build/symbols/` into distribution APK/AAB files.
- **NEVER** commit `build/symbols/` into version control. Store symbols in secure, private release vaults.

---

## 2. Hardware Keystore & Secure Storage

Sensitive secrets, BYOK tokens, and session identifiers MUST be stored inside platform hardware enclaves:

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const secureVault = FlutterSecureStorage(
  aOptions: AndroidOptions(
    encryptedSharedPreferences: true,
    keyCipherAlgorithm: KeyCipherAlgorithm.RSA_ECB_OAEPwithSHA_256andMGF1Padding,
    storageCipherAlgorithm: StorageCipherAlgorithm.AES_GCM_NoPadding,
  ),
  iOptions: IOSOptions(
    accessibility: KeychainAccessibility.first_unlock,
    synchronizable: false,
  ),
);
```

---

## 3. Zero-Trust Network Layer (Certificate Pinning)

To prevent traffic interception via tools like Charles Proxy or mitmproxy, pin backend public keys or root CA certificates using Dart's native `SecurityContext`:

```dart
import 'dart:io';

HttpClient createPinnedHttpClient(List<int> trustedCertificateBytes) {
  final context = SecurityContext(withTrustedRoots: false);
  context.setTrustedCertificatesBytes(trustedCertificateBytes);

  final client = HttpClient(context: context);
  client.badCertificateCallback = (X509Certificate cert, String host, int port) {
    // Strictly fail-closed: reject any certificate not in the explicit trusted bundle
    return false;
  };
  return client;
}
```

---

## 4. Hardware Integrity Attestation (Google Play Integrity & Apple DeviceCheck)

Commercial applications handling sensitive transactions or proprietary API quotas MUST verify binary integrity before granting access:

1. **Client Request**: The app requests an ephemeral hardware attestation token from the OS (Google Play Integrity on Android / Apple App Attest on iOS).
2. **Server Exchange**: The client sends the hardware token alongside the payload.
3. **Verification**: The server validates the token against Google/Apple verification APIs. 
4. **Rejection**: If the APK has been repacked, cloned, tampered with, or run in an unauthorized emulator, the attestation fails and the server terminates the session.

---

## 5. String Obfuscation & Sensitive Constant Protection

Avoid embedding raw API endpoints, proprietary salts, or sensitive strings as plain string literals. 

- Use compile-time environment variables (`--dart-define` or `--dart-define-from-file`).
- Encrypt sensitive internal constants into byte arrays (`Uint8List`) and decode them at runtime with dynamic XOR or AES key derivation.
