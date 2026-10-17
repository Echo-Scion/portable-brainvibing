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

---
## 🚀 Performance Guardrails (60 FPS Mandate)
- **Raster Cache**: For static complex glass layers, wrap in `RepaintBoundary` to cache pixels and avoid GPU re-blurring.
- **Scroll Optimization**: NEVER use `BackdropFilter` inside a `ListView.builder` without a global background blur strategy.
- **Opacity**: Use `Opacity` widget only as a last resort; prefer `color: withOpacity()` for better performance.
