# Liquid Glass Widget Recipes

When tasked with subtle depth and elevation in Flutter, use these specific component templates to achieve restrained translucency and tactile responsiveness. Always derive colors from `Theme.of(context).colorScheme` rather than hardcoding colors.

## 1. Subtle Translucent Surface (BackdropFilter)
Use this sparingly for AppBars, BottomNavBars, or focal elevated sheets. CRITICAL: Max 2 BackdropFilters per screen to maintain 60FPS.

```dart
import 'dart:ui';
import 'package:flutter/material.dart';

class GlassContainer extends StatelessWidget {
  final Widget child;
  final double width;
  final double height;
  final double borderRadius;

  const GlassContainer({
    super.key,
    required this.child,
    this.width = double.infinity,
    this.height = double.infinity,
    this.borderRadius = 10.0, // Standard restrained radius (8-12px)
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 8.0, sigmaY: 8.0),
        child: Container(
          width: width,
          height: height,
          decoration: BoxDecoration(
            color: (isDark ? theme.colorScheme.surface : theme.colorScheme.surfaceContainerHighest)
                .withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(borderRadius),
            border: Border.all(
              color: theme.colorScheme.outlineVariant.withValues(alpha: 0.25),
              width: 1.0,
            ),
            boxShadow: [
              BoxShadow(
                color: theme.shadowColor.withValues(alpha: 0.05),
                blurRadius: 8,
                offset: const Offset(0, 2),
              )
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}
```

## 2. Micro-Interaction Button (Scale on Tap)
Buttons should feel tactile and responsive. Use `GestureDetector` with `AnimatedScale` and theme semantic color tokens.

```dart
class LiquidButton extends StatefulWidget {
  final VoidCallback onTap;
  final Widget child;

  const LiquidButton({super.key, required this.onTap, required this.child});

  @override
  State<LiquidButton> createState() => _LiquidButtonState();
}

class _LiquidButtonState extends State<LiquidButton> {
  bool _isPressed = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return GestureDetector(
      onTapDown: (_) => setState(() => _isPressed = true),
      onTapUp: (_) {
        setState(() => _isPressed = false);
        widget.onTap();
      },
      onTapCancel: () => setState(() => _isPressed = false),
      child: AnimatedScale(
        scale: _isPressed ? 0.98 : 1.0,
        duration: const Duration(milliseconds: 100),
        curve: Curves.easeInOut,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          decoration: BoxDecoration(
            color: colorScheme.primary,
            borderRadius: BorderRadius.circular(10), // Restrained 8-12px standard
            border: Border.all(
              color: colorScheme.outlineVariant.withValues(alpha: 0.2),
              width: 1.0,
            ),
            boxShadow: [
              BoxShadow(
                color: colorScheme.primary.withValues(alpha: 0.15),
                blurRadius: 8,
                offset: const Offset(0, 2),
              )
            ],
          ),
          child: DefaultTextStyle(
            style: TextStyle(
              color: colorScheme.onPrimary,
              fontWeight: FontWeight.w600,
            ),
            child: widget.child,
          ),
        ),
      ),
    );
  }
}
```

## Performance Warning
Do not nest `BackdropFilter` inside large `ListView.builder` items, as this will destroy the 60FPS target. Use them for AppBars, BottomNavBars, and focal hero elements.
