---
activation: on-demand
description: High-performance Flutter Impeller GLSL fragment shaders, custom canvas rendering, and 120Hz tactile animation physics.
ecosystem: flutter
---

# Flutter Impeller Hardware Shaders & 120Hz Canvas Architecture

Flutter's core architectural advantage over DOM and cross-platform native wrappers is full ownership of the GPU rasterization pipeline via the **Impeller** rendering engine (Metal on iOS/macOS, Vulkan on Android). 

This canon establishes patterns for hardware-accelerated shaders and procedural graphics that cannot be replicated by generic vibe-coding web prompts.

---

## 1. Asset Configuration (`pubspec.yaml`)

Declare fragment shaders in `pubspec.yaml` under the root `flutter:` block:

```yaml
flutter:
  shaders:
    - shaders/liquid_glass.frag
    - shaders/chromatic_aberration.frag
```

All shader files MUST reside in the `shaders/` directory with a `.frag` extension.

---

## 2. Impeller GLSL Fragment Shader Standards

Impeller compiles shaders targeting SPIR-V. Write shaders conforming to **GLSL 460 Core**:

```glsl
#version 460 core

#include <flutter/runtime_effect.glsl>

// Uniforms ordered matching Flutter setFloat() indices
uniform vec2 uResolution;
uniform float uTime;
uniform vec2 uPointer;
uniform vec4 uBaseColor;

out vec4 fragColor;

void main() {
    vec2 st = FlutterFragCoord().xy / uResolution.xy;
    vec2 p = st * 2.0 - 1.0;
    p.x *= uResolution.x / uResolution.y;

    // Fluid procedural distortion
    float d = length(p - (uPointer * 2.0 - 1.0));
    float wave = sin(d * 12.0 - uTime * 3.0) * 0.04;
    vec2 uv = st + (p / (d + 0.001)) * wave;

    // Derive lighting against theme base color
    float vignette = smoothstep(1.2, 0.2, length(p));
    fragColor = vec4(uBaseColor.rgb * vignette, uBaseColor.a);
}
```

---

## 3. Asynchronous Program Caching & Uniform Binding

NEVER load `FragmentProgram` synchronously or compile on the UI thread during build:

```dart
import 'dart:ui';
import 'package:flutter/material.dart';

class ShaderController {
  FragmentProgram? _program;
  FragmentShader? _shader;

  Future<void> initialize(String assetPath) async {
    _program = await FragmentProgram.fromAsset(assetPath);
    _shader = _program?.fragmentShader();
  }

  FragmentShader? updateUniforms({
    required Size size,
    required double time,
    required Offset pointer,
    required Color baseColor,
  }) {
    final s = _shader;
    if (s == null) return null;

    int idx = 0;
    // Index 0, 1: Resolution (vec2)
    s.setFloat(idx++, size.width);
    s.setFloat(idx++, size.height);
    // Index 2: Time (float)
    s.setFloat(idx++, time);
    // Index 3, 4: Pointer (vec2)
    s.setFloat(idx++, pointer.dx / size.width);
    s.setFloat(idx++, pointer.dy / size.height);
    // Index 5, 6, 7, 8: BaseColor RGBA (vec4)
    s.setFloat(idx++, baseColor.r);
    s.setFloat(idx++, baseColor.g);
    s.setFloat(idx++, baseColor.b);
    s.setFloat(idx++, baseColor.a);

    return s;
  }
}
```

---

## 4. CustomPainter & RepaintBoundary Optimization

Wrap custom shader renderers in `RepaintBoundary` to prevent unnecessary GPU re-rasterization when sibling widgets rebuild:

```dart
class LiquidShaderSurface extends StatelessWidget {
  final ShaderController controller;
  final Animation<double> timeAnimation;
  final Offset pointerOffset;

  const LiquidShaderSurface({
    super.key,
    required this.controller,
    required this.timeAnimation,
    required this.pointerOffset,
  });

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(
      child: AnimatedBuilder(
        animation: timeAnimation,
        builder: (context, _) {
          return CustomPaint(
            painter: _ShaderPainter(
              controller: controller,
              time: timeAnimation.value,
              pointer: pointerOffset,
              color: Theme.of(context).colorScheme.primary,
            ),
            size: Size.infinite,
          );
        },
      ),
    );
  }
}

class _ShaderPainter extends CustomPainter {
  final ShaderController controller;
  final double time;
  final Offset pointer;
  final Color color;

  _ShaderPainter({
    required this.controller,
    required this.time,
    required this.pointer,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final shader = controller.updateUniforms(
      size: size,
      time: time,
      pointer: pointer,
      baseColor: color,
    );
    if (shader == null) return;

    final paint = Paint()..shader = shader;
    canvas.drawRect(Offset.zero & size, paint);
  }

  @override
  bool shouldRepaint(covariant _ShaderPainter oldDelegate) {
    return oldDelegate.time != time || oldDelegate.pointer != pointer || oldDelegate.color != color;
  }
}
```

---

## 5. Performance Mandates (120Hz Floor)

1. **Shader Pre-Warm**: Initialize `FragmentProgram.fromAsset()` during splash or service bootstrap to eliminate shader jank.
2. **Uniform Index Ordering**: Ensure `setFloat()` order matches the GLSL uniform declaration order byte-for-byte.
3. **Restrained Surface Area**: Use shaders on accent cards, dynamic headers, or background canvases; avoid full-screen un-cached blur stacks inside high-velocity scroll views.
