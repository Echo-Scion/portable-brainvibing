# Flutter Premium UI Patterns

> **Surface Mandate**: Primary surfaces default to restrained solid and tactile backgrounds per `ui-finish/SKILL.md`. The Liquid Glass Stack is an optional accent reserved strictly for floating headers, bottom sheets, or modal overlays (maximum 2 BackdropFilters per screen).

## 💎 The Liquid Glass Stack (Performance-Safe Accent)
```dart
// Core stack for premium surfaces - USE SPARINGLY
// CRITICAL: Max 2 BackdropFilters per screen to maintain 60FPS.
Stack(
  children: [
    ClipRRect(
      borderRadius: BorderRadius.circular(10), // Restrained 8-12px standard
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 8, sigmaY: 8),
        child: Container(
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface.withValues(alpha: 0.15),
            border: Border.all(
              color: Theme.of(context).colorScheme.outlineVariant.withValues(alpha: 0.25),
              width: 1.0,
            ),
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      ),
    ),
    // Content here
  ]
)
```

## 🪄 Micro-Animation & Tactile Delight
```dart
GestureDetector(
  onTapDown: (_) => HapticFeedback.lightImpact(), // Tactile Feedback
  onTap: () => ...,
  child: AnimatedScale(
    scale: isTapped ? 0.95 : 1.0,
    duration: const Duration(milliseconds: 100),
    curve: Curves.elasticOut,
    child: MyGlassButton(...),
  ),
)
```

## 🛡️ Permission Gate & Educational Dialog Pattern
When a system permission or accessibility service is required, present a clear rationale before redirecting:
```dart
class PermissionGateDialog extends StatelessWidget {
  final String title;
  final String rationale;
  final VoidCallback onOpenSettings;

  const PermissionGateDialog({
    super.key,
    required this.title,
    required this.rationale,
    required this.onOpenSettings,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(title),
      content: Text(rationale),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: () {
            Navigator.of(context).pop();
            onOpenSettings();
          },
          child: const Text('Open Settings'),
        ),
      ],
    );
  }
}
```

## 📐 ConstraintLayout to Idiomatic Flutter Translation Heuristics
When translating Android XML layouts (`ConstraintLayout`) into Flutter widgets:
1. **Horizontal Chains (`constraintStart_toEndOf`, `constraintEnd_toStartOf`)**:
   - Map to **`Row`** with `Expanded` widgets for elements with `layout_width="0dp"`.
   - If children follow `[Icon, Column(Title, Subtitle), Action/Switch]`, map directly to **`ListTile`** or **`SwitchListTile`**.
2. **Vertical Chains (`constraintTop_toBottomOf`, `constraintBottom_toTopOf`)**:
   - Map to **`Column`** with `CrossAxisAlignment.start` and spacing tokens.
3. **True Spatial Overlap**:
   - Reserve **`Stack`** strictly for overlays, badges, floating controls, or progress spinners centered over lists. Never flatten an entire screen layout into a single root `Stack`.
4. **Dimension & Padding Tokens**:
   - Map `paddingHorizontal="@dimen/..."` and `paddingVertical="@dimen/..."` to `EdgeInsets.symmetric(horizontal: ..., vertical: ...)`. Always resolve `@dimen/` tokens against the project's design token scale.

---
## 🚀 Performance Guardrails (60 FPS Mandate)
- **Raster Cache**: For static complex glass layers, wrap in `RepaintBoundary` to cache pixels and avoid GPU re-blurring.
- **Scroll Optimization**: NEVER use `BackdropFilter` inside a `ListView.builder` without a global background blur strategy.
- **Opacity**: Use `Opacity` widget only as a last resort; prefer `color: withOpacity()` for better performance.
