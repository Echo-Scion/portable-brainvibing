---
activation: model_decision
description: Traditional Android Views, XML layout conventions, and ViewBinding standards.
last_updated: 2026-10-29
---

# Android XML Layouts & ViewBinding Standards

> **Opt-In Module**: Applicable to projects utilizing traditional View-based architecture and XML layouts.

## 1. ViewBinding Mandate
- All View access MUST utilize Android Jetpack **ViewBinding**.
- `findViewById` and deprecated Kotlin Synthetics (`kotlinx.android.synthetic`) are strictly prohibited.
- In Activities:
  ```kotlin
  private lateinit var binding: ActivityMainBinding

  override fun onCreate(savedInstanceState: Bundle?) {
      super.onCreate(savedInstanceState)
      binding = ActivityMainBinding.inflate(layoutInflater)
      setContentView(binding.root)
  }
  ```
- In Fragments: The binding reference MUST be cleared in `onDestroyView()` to prevent memory leaks:
  ```kotlin
  private var _binding: FragmentExampleBinding? = null
  private val binding get() = _binding!!

  override fun onDestroyView() {
      super.onDestroyView()
      _binding = null
  }
  ```

## 2. XML Layout Hierarchy Optimization
- **Flat Hierarchies**: Developers MUST utilize `ConstraintLayout` to keep the layout tree flat. Avoid nesting three or more levels of `LinearLayout` or `RelativeLayout`.
- **Reusable Components**: Common view structures MUST be extracted into `<include>` layouts or custom View compounds to eliminate layout redundancy.
- **Merge Optimization**: When including layouts into existing view groups, use `<merge>` as the root tag to eliminate redundant ViewGroup levels.
