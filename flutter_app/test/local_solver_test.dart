import 'package:flutter_test/flutter_test.dart';
import 'package:khwarizmi_app/core/local_solver.dart';

void main() {
  group('LocalSolver On-Device Mobile Engine Tests', () {
    test('solves standalone fraction 6/8 correctly', () {
      final res = LocalSolver.solve('6/8');
      expect(res.success, isTrue);
      expect(res.finalAnswer, contains('0.75'));
      expect(res.steps.length, 4);
    });

    test('solves arithmetic order of operations 100 - 25 * 3 + 14 correctly', () {
      final res = LocalSolver.solve(r'100 - 25 \times 3 + 14');
      expect(res.success, isTrue);
      expect(res.finalAnswer, '39');
      expect(res.steps.length, greaterThanOrEqualTo(3));
    });

    test('solves linear equation 3x - 9 = 15 correctly', () {
      final res = LocalSolver.solve('3x - 9 = 15');
      expect(res.success, isTrue);
      expect(res.finalAnswer, contains('8'));
      expect(res.steps.length, 3);
    });

    test('solves quadratic equation x^2 - 5x + 6 = 0 correctly', () {
      final res = LocalSolver.solve('x^2 - 5x + 6 = 0');
      expect(res.success, isTrue);
      expect(res.finalAnswer, contains('2'));
      expect(res.finalAnswer, contains('3'));
    });
  });
}
