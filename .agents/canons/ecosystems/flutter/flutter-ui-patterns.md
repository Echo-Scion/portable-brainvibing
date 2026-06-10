# Flutter Premium UI Patterns

## 💎 The Liquid Glass Stack (Performance-Safe)
```dart
// Core stack for premium surfaces - USE SPARINGLY
// CRITICAL: Max 2 BackdropFilters per screen to maintain 60FPS.
Stack(
  children: [
    ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1),
            border: Border.all(color: Colors.white.withOpacity(0.2)),
            borderRadius: BorderRadius.circular(20),
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
