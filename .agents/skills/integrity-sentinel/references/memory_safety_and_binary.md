# 🧬 Memory Safety & Native Binary Invariants Runbook

> **Scope**: Applied during security audits whenever a codebase targets native C, C++, Rust (`unsafe`), Assembly, Foreign Function Interfaces (FFI), or binary format parsers.
> **Complements**: [`audit_vectors.md`](audit_vectors.md) Vector 11 and [`security.md`](security.md).

---

## 1. Attacker Model & Native Boundaries

In native systems, memory safety violations lead directly to arbitrary code execution, denial-of-service, or information disclosure:
1. **Untrusted Binary Inputs**: Network packet decoders, file format parsers (image, audio, archive), IPC payloads.
2. **FFI Seams**: Memory allocated in one language runtime (e.g. C/Rust) and accessed/freed in another (Dart, Python, Node.js).
3. **Privileged Interfaces**: Native helper utilities, setuid/setgid binaries, system drivers.

---

## 2. Core Attack Classes & Audit Checklists

### A. Spatial Memory Safety (`ORION-MEM-01`)
- [ ] **Buffer Overflows & Out-of-Bounds Writes**: Inspect all array indexing and memory copy operations (`memcpy`, `memmove`, `strcpy`, `read_exact`). Confirm that destination buffer lengths are strictly validated against input lengths prior to copying.
- [ ] **Unbounded Loop Traversal**: Check loop termination conditions when parsing length-prefixed binary structs. Ensure corrupt input lengths cannot cause buffer reads past allocated memory pages.
- [ ] **Off-by-One Boundary Errors**: Scrutinize zero-terminator allocations (e.g., `malloc(len + 1)`) and `<=` vs `<` array indices.

### B. Temporal Memory Safety (`ORION-MEM-02`)
- [ ] **Use-After-Free (UAF)**: Trace pointer lifecycles after free/drop calls. Ensure pointers are zeroed immediately upon deallocation (`free(ptr); ptr = NULL;`) or guarded by smart pointers with exclusive ownership (`std::unique_ptr`, Rust RAII).
- [ ] **Double-Free Anomalies**: In error-recovery branches, verify that allocated memory is not freed multiple times across different unwind paths.
- [ ] **Uninitialized Memory Reads**: Check stack and heap allocations. Confirm buffers are explicitly initialized (`calloc`, `memset`, or default-initialized structs) before passing to serializers or network transmission functions (preventing heap/stack content disclosure).

### C. Integer & Allocation Hazards (`ORION-MEM-03`)
- [ ] **Integer Overflow in Allocation**: Audit allocation calls computing buffer sizes dynamically:
  ```c
  // VULNERABLE: count * size can wrap around 32-bit integer
  char *buf = malloc(count * element_size);
  ```
  Verify the use of overflow-checked arithmetic (e.g., `calloc`, `check_mul`, or saturating operations).
- [ ] **Signed/Unsigned Comparison Traps**: Flag signed integer lengths compared against unsigned bounds (`if (len < MAX_LEN)` where `len = -1` bypasses check and converts to large unsigned value in `memcpy`).
- [ ] **64-to-32 Bit Truncation**: In 64-bit binaries, verify casting `size_t` / `uint64_t` down to `uint32_t` does not discard upper bits.

### D. Unsafe Rust Invariant Auditing (`ORION-MEM-04`)
- [ ] **Every `unsafe` Block Justified**: Every `unsafe { ... }` block in Rust MUST be preceded by a `// SAFETY:` comment stating the invariant that the caller proves.
- [ ] **Aliasing Rule Enforcement**: Audit raw pointer dereferences (`*const T`, `*mut T`). Verify that no two pointers alias mutable memory concurrently, violating Rust's pointer uniqueness guarantee.
- [ ] **`std::mem::transmute` Soundness**: Ensure `transmute` is only used between types with strictly identical memory layout, size, and alignment.
- [ ] **Undefined Behavior in Unchecked APIs**: Audit calls to `get_unchecked`, `from_raw_parts`, and `slice::from_raw_parts_mut`. Verify lengths and pointers are non-null and valid for the entire slice length.

### E. FFI & Cross-Language Memory Ownership (`ORION-MEM-05`)
- [ ] **Cross-Language Freeing Banned**: Memory allocated by Rust/C allocator MUST NOT be freed by Dart, Python, or standard OS `free()`. Memory must be returned to the origin allocator's free function.
- [ ] **Struct Layout & Padding**: In FFI structs (`#[repr(C)]`), confirm that field types, sizes, and padding match byte-for-byte between host and foreign declarations.

---

## 3. Verdict & Remediation Patterns

| Finding Category | Minimal Proof Required for `confirmed` | Immediate Remediation Pattern |
| :--- | :--- | :--- |
| **Heap Buffer Overflow** | PoC binary input showing write beyond buffer allocation | Enforce bounded reads (`snprintf`, bounded slice copies). |
| **Integer Overflow Alloc** | Mathematical proof that `N * size` wraps to small value | Use checked math (`count.checked_mul(size)` or `calloc`). |
| **Unsafe Rust Aliasing** | Source trace showing concurrent `&mut` reference to same memory | Refactor to standard safe references or `Cell`/`RefCell`/`Mutex`. |
| **FFI Memory Leak/UAF** | Source trace showing missing deallocator or double-free across seam | Expose dedicated free helper (`my_lib_free_string(ptr)`). |
