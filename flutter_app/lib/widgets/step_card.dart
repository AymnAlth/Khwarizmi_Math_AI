import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_math_fork/flutter_math.dart';
import '../models/solution_step.dart';
import 'formatted_math_text.dart';

class StepCard extends StatelessWidget {
  final SolutionStep step;

  const StepCard({super.key, required this.step});

  void _copyStep(BuildContext context) {
    final text = 'الخطوة ${step.stepNum}: [${step.ruleNameAr}]\nالصيغة: ${step.latex}\nالشرح: ${step.explanationAr}';
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Directionality(
          textDirection: TextDirection.rtl,
          child: Row(
            children: [
              const Icon(Icons.check_circle, color: Color(0xFF10B981), size: 16),
              const SizedBox(width: 8),
              Text('تم نسخ الخطوة ${step.stepNum} إلى الحافظة', style: const TextStyle(fontSize: 12)),
            ],
          ),
        ),
        backgroundColor: const Color(0xFF1E2230),
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 1),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161922),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF282D3D), width: 1.2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Step Header: Step Number, Verified Tag, and Copy Step Button
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFF2563EB).withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: const Color(0xFF3B82F6), width: 1),
                    ),
                    child: Text(
                      'الخطوة ${step.stepNum}: ${step.ruleNameAr}',
                      style: const TextStyle(
                        color: Color(0xFF60A5FA),
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: const Color(0xFF059669).withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.check_circle_outline, size: 13, color: Color(0xFF10B981)),
                        SizedBox(width: 4),
                        Text(
                          'موثق رمزياً',
                          style: TextStyle(
                            color: Color(0xFF10B981),
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              IconButton(
                icon: const Icon(Icons.copy_outlined, size: 15, color: Colors.white38),
                tooltip: 'نسخ هذه الخطوة',
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
                onPressed: () => _copyStep(context),
              ),
            ],
          ),

          const SizedBox(height: 12),

          // LaTeX Rendered Math Formula Display
          Container(
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
            decoration: BoxDecoration(
              color: const Color(0xFF0F121A),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFF1F2433)),
            ),
            alignment: Alignment.center,
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Math.tex(
                step.latex.isNotEmpty ? step.latex : 'x = 0',
                textStyle: const TextStyle(
                  fontSize: 20,
                  color: Color(0xFF93C5FD),
                  fontWeight: FontWeight.w600,
                ),
                onErrorFallback: (err) => Text(
                  step.latex,
                  style: const TextStyle(color: Colors.white70, fontSize: 16),
                ),
              ),
            ),
          ),

          const SizedBox(height: 12),

          // Formatted Pedagogical Arabic Explanation (renders math inside $...$)
          FormattedMathText(
            text: step.explanationAr,
            textStyle: const TextStyle(
              fontSize: 13.5,
              color: Color(0xFFD1D5DB),
              height: 1.6,
            ),
            mathStyle: const TextStyle(
              fontSize: 15,
              color: Color(0xFF38BDF8),
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
