import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:khwarizmi_app/widgets/formatted_math_text.dart';

void main() {
  testWidgets('FormattedMathText renders plain and math text without error', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: FormattedMathText(
            text: r'وفق أولويات العمليات الحسابية: $25 \times 3 = 75$ ثم نعوض بالناتج.',
          ),
        ),
      ),
    );

    expect(find.byType(FormattedMathText), findsOneWidget);
  });
}
