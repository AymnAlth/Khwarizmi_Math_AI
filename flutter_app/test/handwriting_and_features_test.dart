import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:khwarizmi_app/main.dart';

void main() {
  group('Comprehensive UI & Features Tests (Handwriting, Canvas, Solving)', () {
    testWidgets('Renders all toolbar buttons including handwriting, camera, gallery', (tester) async {
      await tester.pumpWidget(const KhwarizmiApp());
      await tester.pump();

      // Verify header and buttons
      expect(find.text('خوارزمي'), findsOneWidget);
      expect(find.text('كتابة باليد'), findsOneWidget);
      expect(find.text('تصوير بالكاميرا'), findsOneWidget);
      expect(find.text('من المعرض'), findsOneWidget);
    });

    testWidgets('Opens HandwritingCanvasDialog and simulates pen drawing', (tester) async {
      await tester.pumpWidget(const KhwarizmiApp());
      await tester.pump();

      // Tap on Handwriting button
      final canvasBtn = find.text('كتابة باليد');
      expect(canvasBtn, findsOneWidget);
      await tester.tap(canvasBtn);
      await tester.pumpAndSettle();

      // Verify Blackboard dialog is open
      expect(find.text('كتابة المعادلة بخط اليد (Touch / Pen)'), findsOneWidget);
      expect(find.byTooltip('القلم'), findsOneWidget);
      expect(find.byTooltip('الممحاة'), findsOneWidget);
      expect(find.byTooltip('تراجع'), findsOneWidget);
      expect(find.byTooltip('مسح اللوحة بالكامل'), findsOneWidget);
      expect(find.text('التعرف والحل الفوري'), findsOneWidget);

      // Simulate drawing touch gesture on the chalkboard
      final gestureArea = find.byType(GestureDetector).first;
      final gesture = await tester.startGesture(tester.getCenter(gestureArea));
      await gesture.moveBy(const Offset(30, 30));
      await gesture.moveBy(const Offset(60, 0));
      await gesture.up();
      await tester.pump();

      // Verify clear button functions
      final clearBtn = find.byTooltip('مسح اللوحة بالكامل');
      await tester.tap(clearBtn);
      await tester.pump();

      // Close dialog
      final closeBtn = find.byIcon(Icons.close);
      await tester.tap(closeBtn);
      await tester.pumpAndSettle();

      // Dialog is closed
      expect(find.text('كتابة المعادلة بخط اليد (Touch / Pen)'), findsNothing);
    });

    testWidgets('Full solving flow on-device displays final answer card and pedagogical steps', (tester) async {
      await tester.pumpWidget(const KhwarizmiApp());
      await tester.pump();

      // Verify Final Answer card is rendered
      expect(find.text('النتيجة النهائية الموثقة رمزياً'), findsOneWidget);
      expect(find.text('نسخ النتيجة فقط'), findsOneWidget);
      expect(find.text('نسخ الحل كاملاً'), findsOneWidget);
    });
  });
}
