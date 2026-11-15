import 'package:flutter_test/flutter_test.dart';
import 'package:khwarizmi_app/main.dart';

void main() {
  testWidgets('KhwarizmiApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const KhwarizmiApp());
    expect(find.text('خوارزمي'), findsOneWidget);
  });
}
