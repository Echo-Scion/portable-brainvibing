# Liquid Glass Widget Recipes

When tasked with "ui-finish" or "Liquid Glass design", use these specific component templates to achieve depth, blur, and premium aesthetics. Do NOT use flat, opaque colors if a frosted glass effect would look better.

## 1. Frosted Glass Container (BackdropFilter)
Use this for Cards, Bottom Sheets, or floating elements over images/gradients.

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
    this.borderRadius = 16.0,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10.0, sigmaY: 10.0),
        child: Container(
          width: width,
          height: height,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1), // Adjust opacity for dark/light mode
            borderRadius: BorderRadius.circular(borderRadius),
            border: Border.all(
              color: Colors.white.withOpacity(0.2), // Subtle glass border
              width: 1.5,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 10,
                spreadRadius: -5,
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
Buttons should feel tactile. Use `GestureDetector` with an `AnimationController` or `AnimatedScale`.

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
    return GestureDetector(
      onTapDown: (_) => setState(() => _isPressed = true),
      onTapUp: (_) {
        setState(() => _isPressed = false);
        widget.onTap();
      },
      onTapCancel: () => setState(() => _isPressed = false),
      child: AnimatedScale(
        scale: _isPressed ? 0.95 : 1.0,
        duration: const Duration(milliseconds: 100),
        curve: Curves.easeInOut,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.blueAccent, Colors.purpleAccent],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(30),
            boxShadow: [
              BoxShadow(
                color: Colors.blueAccent.withOpacity(0.4),
                blurRadius: 12,
                offset: const Offset(0, 4),
              )
            ],
          ),
          child: DefaultTextStyle(
            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
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
