class LatexFormatter {
  /// Formats user-entered text (whether ASCII math, partial LaTeX, or symbols)
  /// into clean, syntax-safe LaTeX suitable for live rendering with KaTeX/flutter_math.
  static String formatForPreview(String raw) {
    var s = raw.trim();
    if (s.isEmpty) return r'\dots';

    // 1. Remove trailing dangling backslashes (e.g., "\sqrt{x}\" or lone "\")
    while (s.endsWith(r'\')) {
      s = s.substring(0, s.length - 1).trim();
    }
    if (s.isEmpty) return r'\dots';

    // 2. Normalize ASCII power syntax "x^2" or "x^{2}" is already fine,
    // but convert "sqrt(...)" and "sqrt{...}" without leading backslash to "\sqrt{...}"
    s = s.replaceAllMapped(RegExp(r'(?<!\\)sqrt\(([^)]*)\)'), (m) => '\\sqrt{${m[1]}}');
    s = s.replaceAllMapped(RegExp(r'(?<!\\)sqrt\{([^}]*)\}'), (m) => '\\sqrt{${m[1]}}');
    s = s.replaceAllMapped(RegExp(r'(?<!\\)cbrt\(([^)]*)\)'), (m) => '\\sqrt[3]{${m[1]}}');
    s = s.replaceAllMapped(RegExp(r'(?<!\\)cbrt\{([^}]*)\}'), (m) => '\\sqrt[3]{${m[1]}}');

    // 3. Convert ASCII trigonometric & logarithmic functions if unescaped
    s = s.replaceAllMapped(
      RegExp(r'(?<!\\)\b(sin|cos|tan|cot|sec|csc|arcsin|arccos|arctan|sinh|cosh|tanh|log|ln|lim)\b'),
      (m) => '\\${m[1]}',
    );

    // 4. Convert Greek words if unescaped
    s = s.replaceAllMapped(
      RegExp(r'(?<!\\)\b(pi|theta|alpha|beta|gamma|lambda|mu|sigma|omega)\b'),
      (m) => '\\${m[1]}',
    );
    s = s.replaceAllMapped(
      RegExp(r'(?<!\\)\b(Delta|Omega|Phi|Sigma|Theta)\b'),
      (m) => '\\${m[1]}',
    );

    // 5. Convert relational and arithmetic operators
    s = s.replaceAll('!=', r' \ne ');
    s = s.replaceAll('<=', r' \le ');
    s = s.replaceAll('>=', r' \ge ');
    s = s.replaceAll('~=', r' \approx ');
    s = s.replaceAll(RegExp(r'(?<!\\)\bapprox\b'), r'\approx');
    s = s.replaceAll(RegExp(r'(?<!\\)\binf(inity)?\b'), r'\infty');
    s = s.replaceAll('deg', r'^\circ');
    s = s.replaceAll('°', r'^\circ');

    // 6. Convert standalone asterisk "*" to "\times " when used between numbers or variables
    s = s.replaceAllMapped(
      RegExp(r'(\d+|\w+|\))\s*\*\s*(\d+|\w+|\()'),
      (m) => '${m[1]} \\times ${m[2]}',
    );

    // 7. Auto-close incomplete opening braces/brackets that occur while typing
    // Count unmatched curly braces
    int openBraces = 0;
    for (int i = 0; i < s.length; i++) {
      if (s[i] == '{') {
        openBraces++;
      } else if (s[i] == '}') {
        if (openBraces > 0) openBraces--;
      }
    }
    if (openBraces > 0) {
      s += '}' * openBraces;
    }

    // Count unmatched parentheses
    int openParens = 0;
    for (int i = 0; i < s.length; i++) {
      if (s[i] == '(') {
        openParens++;
      } else if (s[i] == ')') {
        if (openParens > 0) openParens--;
      }
    }
    if (openParens > 0) {
      s += ')' * openParens;
    }

    // Count unmatched square brackets
    int openBrackets = 0;
    for (int i = 0; i < s.length; i++) {
      if (s[i] == '[') {
        openBrackets++;
      } else if (s[i] == ']') {
        if (openBrackets > 0) openBrackets--;
      }
    }
    if (openBrackets > 0) {
      s += ']' * openBrackets;
    }

    // 8. If text ends with an open binary operator, append a subtle placeholder so KaTeX compiles
    if (s.endsWith('+') || s.endsWith('-') || s.endsWith('=') || s.endsWith(r'\times') || s.endsWith('/')) {
      s += r' \dots';
    }

    return s;
  }
}
