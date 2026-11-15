import 'package:flutter/material.dart';
import 'package:flutter_math_fork/flutter_math.dart';

/// Renders Arabic text with embedded inline LaTeX math wrapped in `$ ... $`.
/// Example: "وفق أولويات العمليات الحسابية: $25 \times 3 = 75$ ثم نعوض."
class FormattedMathText extends StatelessWidget {
  final String text;
  final TextStyle? textStyle;
  final TextStyle? mathStyle;
  final TextAlign textAlign;

  const FormattedMathText({
    super.key,
    required this.text,
    this.textStyle,
    this.mathStyle,
    this.textAlign = TextAlign.right,
  });

  @override
  Widget build(BuildContext context) {
    final baseTextStyle = textStyle ??
        const TextStyle(
          fontSize: 14,
          color: Color(0xFFD1D5DB),
          height: 1.6,
        );

    final baseMathStyle = mathStyle ??
        const TextStyle(
          fontSize: 15,
          color: Color(0xFF60A5FA),
          fontWeight: FontWeight.bold,
        );

    // If there are no math delimiters, render standard Text
    if (!text.contains(r'$')) {
      return Text(
        text,
        textAlign: textAlign,
        style: baseTextStyle,
      );
    }

    final spans = <InlineSpan>[];
    final parts = text.split(r'$');

    for (int i = 0; i < parts.length; i++) {
      final part = parts[i];
      if (part.isEmpty) continue;

      if (i % 2 == 1) {
        // Odd indices are math expressions inside $...$
        spans.add(
          WidgetSpan(
            alignment: PlaceholderAlignment.middle,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 4),
              child: Math.tex(
                part.trim(),
                textStyle: baseMathStyle,
                onErrorFallback: (err) => Text(
                  part,
                  style: baseMathStyle.copyWith(color: const Color(0xFFFBBF24)),
                ),
              ),
            ),
          ),
        );
      } else {
        // Even indices are natural Arabic text
        spans.add(
          TextSpan(
            text: part,
            style: baseTextStyle,
          ),
        );
      }
    }

    return Text.rich(
      TextSpan(children: spans),
      textAlign: textAlign,
      textDirection: TextDirection.rtl,
    );
  }
}
