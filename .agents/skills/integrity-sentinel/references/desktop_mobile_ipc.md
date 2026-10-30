# 📱 Desktop, Mobile & Local IPC Privilege Isolation Runbook

> **Scope**: Applied during security audits whenever a codebase targets desktop apps (Electron, Qt, Flutter Desktop), mobile apps (Android, iOS), local daemon helpers, deep-link handlers, or local IPC mechanisms (Named Pipes, Unix Sockets, D-Bus, XPC, Binder).
> **Complements**: [`audit_vectors.md`](audit_vectors.md) Vector 12 and [`security.md`](security.md).

---

## 1. Attacker Model & Local Boundaries

In desktop and mobile environments, attackers can reside on the same operating system:
1. **Malicious Local Processes**: Lower-privileged or untrusted applications running under the same or different OS user accounts.
2. **Untrusted Web Content via Deep-Links**: Web browsers or external links launching registered URL schemes (`custom-app://action`).
3. **Compromised WebViews**: Web content loaded into embedded application webviews attempting to invoke native capabilities.
4. **Sandboxed Child Processes**: Untrusted renderers or worker processes escaping confinement via IPC channels.

---

## 2. Core Attack Classes & Audit Checklists

### A. Rejection of Fake Peer Authentication (`ORION-IPC-01`)
- [ ] **No Self-Reported Identity**: Remind auditors: process names, executable paths, bundle IDs, and sender headers are **trivially spoofable**.
- [ ] **Mandatory OS-Enforced Credentials**:
  - **Linux / POSIX**: Verify Unix domain sockets use kernel peer credentials via `getsockopt(fd, SOL_SOCKET, SO_PEERCRED, ...)`.
  - **Windows**: Verify Named Pipes validate client process tokens via `GetNamedPipeHandleState` and impersonate using `ImpersonateNamedPipeClient`.
  - **Android**: Verify IPC services check calling identity via `Binder.getCallingUid()` and validate against expected package signatures with `PackageManager.checkSignatures()`.
  - **macOS / iOS**: Verify XPC connections audit code-signing requirements via `xpc_connection_set_target_queue` and `SecCodeCopyGuestWithProcessIdentifier`.

### B. Deep-Link & Custom Scheme Ambiguity (`ORION-IPC-02`)
- [ ] **Unauthenticated State Mutation**: Audit all custom scheme handlers (`myapp://...`) and Android deep-link intents. Reject deep links that execute state changes (changing password, deleting items, completing purchases) without an active, verified user confirmation or one-time token.
- [ ] **OAuth Redirect Interception**: Confirm OAuth redirect URIs use platform-verified app links (Android App Links with `assetlinks.json`, iOS Universal Links with `apple-app-site-association`) rather than generic custom schemes that any installed app can hijack.

### C. Local Transport Permissions & ACLs (`ORION-IPC-03`)
- [ ] **Insecure Named Pipe DACLs (Windows)**: Audit Named Pipe creation (`CreateNamedPipe`). Confirm `SECURITY_ATTRIBUTES` explicitly restricts access to authorized user SIDs. Reject world-writable pipes (`NULL` DACL).
- [ ] **Unix Socket Permissions (POSIX)**: Ensure Unix domain socket files are created with restrictive file permissions (`umask 0077` or explicit `chmod 0600`) inside protected parent directories (`/run/user/<uid>/`).
- [ ] **Exported Android Components**: In `AndroidManifest.xml`, check all `<activity>`, `<service>`, `<receiver>`, and `<provider>` declarations. Ensure components without intended external consumers specify `android:exported="false"`.

### D. WebView Bridge Privilege Isolation (`ORION-IPC-04`)
- [ ] **Overprivileged JavaScript Interfaces**: On Android, inspect `@JavascriptInterface` bindings. Verify exported Java methods do not expose raw file access, arbitrary intent launches, or shell execution.
- [ ] **Missing Origin Validation**: In WebView message handlers (`onMessage`, `postMessage`), verify the event origin (`event.origin`) is strictly validated against an allowlist of trusted HTTPS domains before acting on the message.
- [ ] **Mixed Content & Navigation Traps**: Ensure webviews restrict navigation to trusted domains (`shouldOverrideUrlLoading`) and disable access to local content schemes (`file://`, `content://`).

### E. Account & Session State Confusion (`ORION-IPC-05`)
- [ ] **Cross-Account Cache Isolation**: Verify that user logout or account switching immediately purges local caches, cached API responses, and encrypted secure storage keys.
- [ ] **Biometric & Notification Action Binding**: Ensure biometric prompts or notification actions re-validate the active session context and cannot be replayed out-of-band.

---

## 3. Verdict & Remediation Patterns

| Finding Category | Minimal Proof Required for `confirmed` | Immediate Remediation Pattern |
| :--- | :--- | :--- |
| **Fake Peer Auth** | Code inspection showing peer identity checked via process name | Replace with `SO_PEERCRED` / `Binder.getCallingUid()`. |
| **Deep-Link CSRF** | PoC URL showing unauthorized state change without prompt | Require user confirmation prompt or cryptographic session nonce. |
| **World-Writable Pipe** | Inspection showing `NULL` DACL in `CreateNamedPipe` | Build explicit security descriptor restricting access to `GENERIC_READ | GENERIC_WRITE` for target SID. |
| **WebView Origin Leak** | Code inspection showing `postMessage` handler without origin check | Add `if (!trustedOrigins.includes(event.origin)) return;`. |
