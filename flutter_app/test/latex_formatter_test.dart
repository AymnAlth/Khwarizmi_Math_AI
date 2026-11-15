import 'package:flutter_test/flutter_test.dart';
import 'package:khwarizmi_app/core/latex_formatter.dart';

void main() {
  group('LatexFormatter Tests', () {
    test('formats empty string to dots', () {
      expect(LatexFormatter.formatForPreview(''), r'\dots');
      expect(LatexFormatter.formatForPreview('   '), r'\dots');
    });

    test('strips trailing dangling backslashes', () {
      expect(LatexFormatter.formatForPreview(r'\sqrt{x}\'), r'\sqrt{x}');
      expect(LatexFormatter.formatForPreview(r'\\'), r'\dots');
    });

    test('auto-closes incomplete braces in typing', () {
      expect(LatexFormatter.formatForPreview(r'\sqrt{x'), r'\sqrt{x}');
      expect(LatexFormatter.formatForPreview(r'\frac{a}{b'), r'\frac{a}{b}');
      expect(LatexFormatter.formatForPreview(r'^{2'), '^{2}');
    });

    test('converts ASCII math keywords', () {
      expect(LatexFormatter.formatForPreview('sqrt(16)'), r'\sqrt{16}');
      expect(LatexFormatter.formatForPreview('cbrt(27)'), r'\sqrt[3]{27}');
      expect(LatexFormatter.formatForPreview('sin(x)'), r'\sin(x)');
      expect(LatexFormatter.formatForPreview('pi + theta'), r'\pi + \theta');
    });

    test('converts relational operators and asterisks', () {
      expect(LatexFormatter.formatForPreview('x != 5'), r'x  \ne  5');
      expect(LatexFormatter.formatForPreview('x <= 10'), r'x  \le  10');
      expect(LatexFormatter.formatForPreview('25 * 3'), r'25 \times 3');
    });
  });
}
