import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:khwarizmi_app/widgets/math_keyboard.dart';

void main() {
  testWidgets('MathKeyboard category switching and insertion test', (WidgetTester tester) async {
    final controller = TextEditingController(text: '');
    bool solved = false;
    bool changed = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: MathKeyboard(
            controller: controller,
            onSolve: () => solved = true,
            onChanged: () => changed = true,
          ),
        ),
      ),
    );

    // Initial basic tab: 7, 8, 9 should be visible
    expect(find.text('7'), findsOneWidget);
    expect(find.text('حل'), findsOneWidget);

    // Tap '7'
    await tester.tap(find.text('7'));
    await tester.pump();
    expect(controller.text, '7');
    expect(changed, isTrue);

    // Switch to Algebra tab: 'جبر وقوى'
    await tester.tap(find.text('جبر وقوى'));
    await tester.pump();
    expect(find.text('a/b'), findsOneWidget);
    expect(find.text('ⁿ√x'), findsOneWidget);

    // Tap '√x'
    await tester.tap(find.text('√x'));
    await tester.pump();
    // It should insert \sqrt{} and cursor should be inside {}
    expect(controller.text, r'7\sqrt{}');
    expect(controller.selection.baseOffset, r'7\sqrt{}'.length - 1);

    // Switch to Calculus tab: 'تفاضل ودوال'
    await tester.tap(find.text('تفاضل ودوال'));
    await tester.pump();
    expect(find.text('d/dx'), findsOneWidget);
    expect(find.text('∫'), findsOneWidget);

    // Switch to Symbols tab: 'رموز وهندسة'
    await tester.tap(find.text('رموز وهندسة'));
    await tester.pump();
    expect(find.text('°'), findsOneWidget);
    expect(find.text('∈'), findsOneWidget);
    expect(find.text('⇒'), findsOneWidget);

    // Tap 'حل'
    await tester.tap(find.text('حل'));
    await tester.pump();
    expect(solved, isTrue);
  });
}
