import 'package:flutter/material.dart';

class MathKeyboard extends StatefulWidget {
  final TextEditingController controller;
  final VoidCallback onSolve;
  final VoidCallback onChanged;

  const MathKeyboard({
    super.key,
    required this.controller,
    required this.onSolve,
    required this.onChanged,
  });

  @override
  State<MathKeyboard> createState() => _MathKeyboardState();
}

class _MathKeyboardState extends State<MathKeyboard> {
  // 0: Basic & Arithmetic, 1: Algebra & Powers, 2: Calculus & Functions, 3: Symbols & Geometry
  int _activeCategory = 0;

  void _insert(String text, {int cursorOffsetFromEnd = 0}) {
    final cur = widget.controller.text;
    final sel = widget.controller.selection;

    if (sel.isValid && sel.start >= 0 && sel.start != sel.end) {
      // Smart Wrapping: If user has highlighted text, wrap it inside the formula
      final selectedText = cur.substring(sel.start, sel.end);
      String replaced;
      int newCursor;

      if (text == r'\sqrt{}') {
        replaced = '\\sqrt{$selectedText}';
        newCursor = sel.start + replaced.length;
      } else if (text == r'\frac{}{}') {
        replaced = '\\frac{$selectedText}{}';
        newCursor = sel.start + replaced.length - 1; // place cursor in denominator
      } else if (text == '^{}') {
        replaced = '^{$selectedText}';
        newCursor = sel.start + replaced.length;
      } else if (text == '_{}') {
        replaced = '_{$selectedText}';
        newCursor = sel.start + replaced.length;
      } else if (text == '(' || text == ')') {
        replaced = '($selectedText)';
        newCursor = sel.start + replaced.length;
      } else if (text == r'\{ \}') {
        replaced = '\\{$selectedText\\}';
        newCursor = sel.start + replaced.length;
      } else if (text == r'\vec{}') {
        replaced = '\\vec{$selectedText}';
        newCursor = sel.start + replaced.length;
      } else {
        replaced = text;
        newCursor = sel.start + text.length - cursorOffsetFromEnd;
      }

      final newText = cur.replaceRange(sel.start, sel.end, replaced);
      widget.controller.text = newText;
      if (newCursor < 0) newCursor = 0;
      if (newCursor > newText.length) newCursor = newText.length;
      widget.controller.selection = TextSelection.collapsed(offset: newCursor);
    } else {
      // Normal Insertion without highlighted selection
      int start = (sel.isValid && sel.start >= 0) ? sel.start : cur.length;
      final newText = cur.replaceRange(start, start, text);
      widget.controller.text = newText;
      int newOffset = start + text.length - cursorOffsetFromEnd;
      if (newOffset < 0) newOffset = 0;
      if (newOffset > newText.length) newOffset = newText.length;
      widget.controller.selection = TextSelection.collapsed(offset: newOffset);
    }
    widget.onChanged();
  }

  void _delete() {
    final cur = widget.controller.text;
    if (cur.isEmpty) return;
    final sel = widget.controller.selection;
    if (sel.isValid && sel.start > 0) {
      if (sel.start == sel.end) {
        final newText = cur.replaceRange(sel.start - 1, sel.start, '');
        widget.controller.text = newText;
        widget.controller.selection = TextSelection.collapsed(offset: sel.start - 1);
      } else {
        final newText = cur.replaceRange(sel.start, sel.end, '');
        widget.controller.text = newText;
        widget.controller.selection = TextSelection.collapsed(offset: sel.start);
      }
    } else {
      widget.controller.text = cur.substring(0, cur.length - 1);
      widget.controller.selection = TextSelection.collapsed(offset: widget.controller.text.length);
    }
    widget.onChanged();
  }

  void _clear() {
    widget.controller.clear();
    widget.onChanged();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      decoration: const BoxDecoration(
        color: Color(0xFF13161F),
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        border: Border(top: BorderSide(color: Color(0xFF282D3D), width: 1.5)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Category Navigation Bar
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildCategoryTab(0, 'حساب وأرقام', Icons.calculate_outlined),
                _buildCategoryTab(1, 'جبر وقوى', Icons.superscript_outlined),
                _buildCategoryTab(2, 'تفاضل ودوال', Icons.functions_outlined),
                _buildCategoryTab(3, 'رموز وهندسة', Icons.category_outlined),
              ],
            ),
          ),
          const SizedBox(height: 6),

          // Active Keypad View
          if (_activeCategory == 0) _buildBasicKeypad(),
          if (_activeCategory == 1) _buildAlgebraKeypad(),
          if (_activeCategory == 2) _buildCalculusKeypad(),
          if (_activeCategory == 3) _buildSymbolsKeypad(),
        ],
      ),
    );
  }

  Widget _buildCategoryTab(int idx, String title, IconData icon) {
    final isSelected = _activeCategory == idx;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 3),
      child: InkWell(
        onTap: () => setState(() => _activeCategory = idx),
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF2563EB).withValues(alpha: 0.25) : const Color(0xFF1A1D27),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: isSelected ? const Color(0xFF3B82F6) : const Color(0xFF2D3345),
              width: 1,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 14, color: isSelected ? const Color(0xFF60A5FA) : Colors.white60),
              const SizedBox(width: 5),
              Text(
                title,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  color: isSelected ? const Color(0xFF60A5FA) : Colors.white70,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // 1. Basic Keypad (Arithmetic, Numbers & Main Actions)
  Widget _buildBasicKeypad() {
    return Column(
      children: [
        // Quick variables bar
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              _buildSpecialKey('x', 'x'),
              _buildSpecialKey('y', 'y'),
              _buildSpecialKey('z', 'z'),
              _buildSpecialKey('(', '('),
              _buildSpecialKey(')', ')'),
              _buildSpecialKey('a/b', r'\frac{}{}', cursorOffsetFromEnd: 3),
              _buildSpecialKey('√x', r'\sqrt{}', cursorOffsetFromEnd: 1),
              _buildSpecialKey('x²', '^2'),
              _buildSpecialKey('xⁿ', '^{}', cursorOffsetFromEnd: 1),
              _buildSpecialKey('π', r'\pi '),
              _buildSpecialKey('±', r'\pm '),
            ],
          ),
        ),
        const SizedBox(height: 6),
        _buildKeyRow([
          _buildKey('7', '7'),
          _buildKey('8', '8'),
          _buildKey('9', '9'),
          _buildKey('÷', ' / ', isOp: true),
          _buildActionKey('DEL', Icons.backspace_outlined, _delete, color: const Color(0xFFEF4444)),
        ]),
        _buildKeyRow([
          _buildKey('4', '4'),
          _buildKey('5', '5'),
          _buildKey('6', '6'),
          _buildKey('×', r' \times ', isOp: true),
          _buildKey('^', '^{}', isOp: true, cursorOffset: 1),
        ]),
        _buildKeyRow([
          _buildKey('1', '1'),
          _buildKey('2', '2'),
          _buildKey('3', '3'),
          _buildKey('-', ' - ', isOp: true),
          _buildKey('+', ' + ', isOp: true),
        ]),
        _buildKeyRow([
          _buildActionKey('AC', null, _clear, color: const Color(0xFF6B7280)),
          _buildKey('0', '0'),
          _buildKey('.', '.'),
          _buildKey('=', ' = ', isOp: true),
          _buildSolveKey(),
        ]),
      ],
    );
  }

  // 2. Algebra Keypad (Roots, Powers, Fractions, Relations)
  Widget _buildAlgebraKeypad() {
    return Column(
      children: [
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              _buildSpecialKey('x', 'x'),
              _buildSpecialKey('y', 'y'),
              _buildSpecialKey('z', 'z'),
              _buildSpecialKey('a', 'a'),
              _buildSpecialKey('b', 'b'),
              _buildSpecialKey('c', 'c'),
              _buildSpecialKey('k', 'k'),
              _buildSpecialKey('n', 'n'),
              _buildSpecialKey('m', 'm'),
              _buildSpecialKey('t', 't'),
            ],
          ),
        ),
        const SizedBox(height: 6),
        _buildKeyRow([
          _buildKey('a/b', r'\frac{}{}', isOp: true, cursorOffset: 3),
          _buildKey('√x', r'\sqrt{}', isOp: true, cursorOffset: 1),
          _buildKey('∛x', r'\sqrt[3]{}', isOp: true, cursorOffset: 1),
          _buildKey('ⁿ√x', r'\sqrt[]{}', isOp: true, cursorOffset: 3),
          _buildKey('xⁿ', '^{}', isOp: true, cursorOffset: 1),
        ]),
        _buildKeyRow([
          _buildKey('x²', '^2'),
          _buildKey('x³', '^3'),
          _buildKey('|x|', '|', isOp: true),
          _buildKey('%', r'\% ', isOp: true),
          _buildKey('±', r'\pm ', isOp: true),
        ]),
        _buildKeyRow([
          _buildKey('≤', r' \le ', isOp: true),
          _buildKey('≥', r' \ge ', isOp: true),
          _buildKey('≠', r' \ne ', isOp: true),
          _buildKey('≈', r' \approx ', isOp: true),
          _buildKey('=', ' = ', isOp: true),
        ]),
        _buildKeyRow([
          _buildKey('log', r'\log('),
          _buildKey('ln', r'\ln('),
          _buildKey('10ⁿ', '10^{}', cursorOffset: 1),
          _buildKey('eⁿ', 'e^{}', cursorOffset: 1),
          _buildSolveKey(),
        ]),
      ],
    );
  }

  // 3. Calculus Keypad (Calculus, Integrals, Limits, Trig)
  Widget _buildCalculusKeypad() {
    return Column(
      children: [
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              _buildSpecialKey('dx', ' dx'),
              _buildSpecialKey('dt', ' dt'),
              _buildSpecialKey('∞', r'\infty '),
              _buildSpecialKey('π', r'\pi '),
              _buildSpecialKey('e', 'e'),
              _buildSpecialKey('θ', r'\theta '),
              _buildSpecialKey('(', '('),
              _buildSpecialKey(')', ')'),
            ],
          ),
        ),
        const SizedBox(height: 6),
        _buildKeyRow([
          _buildKey('d/dx', r'\frac{d}{dx}('),
          _buildKey('∂/∂x', r'\frac{\partial}{\partial x}('),
          _buildKey('∫', r'\int '),
          _buildKey('∫ₐᵇ', r'\int_{}^{}', cursorOffset: 3),
          _buildKey('lim', r'\lim_{x \to 0}('),
        ]),
        _buildKeyRow([
          _buildKey('∑', r'\sum_{i=1}^{n}'),
          _buildKey('∏', r'\prod_{i=1}^{n}'),
          _buildKey('∞', r'\infty '),
          _buildKey('eⁿ', 'e^{}', cursorOffset: 1),
          _buildKey("x'", "'"),
        ]),
        _buildKeyRow([
          _buildKey('sin', r'\sin('),
          _buildKey('cos', r'\cos('),
          _buildKey('tan', r'\tan('),
          _buildKey('cot', r'\cot('),
          _buildKey('sec', r'\sec('),
        ]),
        _buildKeyRow([
          _buildKey('sin⁻¹', r'\arcsin('),
          _buildKey('cos⁻¹', r'\arccos('),
          _buildKey('tan⁻¹', r'\arctan('),
          _buildKey('sinh', r'\sinh('),
          _buildSolveKey(),
        ]),
      ],
    );
  }

  // 4. Symbols & Geometry Keypad (Greek, Geometry, Sets & Logic)
  Widget _buildSymbolsKeypad() {
    return Column(
      children: [
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              _buildSpecialKey('π', r'\pi '),
              _buildSpecialKey('θ', r'\theta '),
              _buildSpecialKey('α', r'\alpha '),
              _buildSpecialKey('β', r'\beta '),
              _buildSpecialKey('γ', r'\gamma '),
              _buildSpecialKey('Δ', r'\Delta '),
              _buildSpecialKey('λ', r'\lambda '),
              _buildSpecialKey('μ', r'\mu '),
              _buildSpecialKey('σ', r'\sigma '),
              _buildSpecialKey('ω', r'\omega '),
              _buildSpecialKey('ϕ', r'\phi '),
            ],
          ),
        ),
        const SizedBox(height: 6),
        _buildKeyRow([
          _buildKey('°', r'^\circ'),
          _buildKey('∠', r'\angle '),
          _buildKey('△', r'\triangle '),
          _buildKey('⊥', r'\perp '),
          _buildKey('∥', r'\parallel '),
        ]),
        _buildKeyRow([
          _buildKey('v⃗', r'\vec{}', cursorOffset: 1),
          _buildKey('{ }', r'\{ \}', cursorOffset: 2),
          _buildKey('[ ]', '[ ]', cursorOffset: 1),
          _buildKey('( )', '( )', cursorOffset: 1),
          _buildKey('!', '!'),
        ]),
        _buildKeyRow([
          _buildKey('∈', r'\in '),
          _buildKey('∉', r'\notin '),
          _buildKey('⊂', r'\subset '),
          _buildKey('∪', r'\cup '),
          _buildKey('∩', r'\cap '),
        ]),
        _buildKeyRow([
          _buildKey('∅', r'\emptyset '),
          _buildKey('⇒', r'\implies '),
          _buildKey('⇔', r'\iff '),
          _buildKey('∴', r'\therefore '),
          _buildSolveKey(),
        ]),
      ],
    );
  }

  Widget _buildKeyRow(List<Widget> children) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2.5),
      child: Row(
        children: children
            .map((w) => Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 2),
                    child: w,
                  ),
                ))
            .toList(),
      ),
    );
  }

  Widget _buildKey(String label, String insertVal, {bool isOp = false, int cursorOffset = 0}) {
    return InkWell(
      onTap: () => _insert(insertVal, cursorOffsetFromEnd: cursorOffset),
      borderRadius: BorderRadius.circular(9),
      child: Container(
        height: 42,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: isOp ? const Color(0xFF232938) : const Color(0xFF1B1F2B),
          borderRadius: BorderRadius.circular(9),
          border: Border.all(
            color: isOp ? const Color(0xFF384259) : const Color(0xFF282E3E),
            width: 1,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: isOp ? 15 : 16,
            fontWeight: isOp ? FontWeight.bold : FontWeight.w500,
            color: isOp ? const Color(0xFF60A5FA) : Colors.white,
            fontFamily: 'monospace',
          ),
        ),
      ),
    );
  }

  Widget _buildSpecialKey(String label, String insertVal, {int cursorOffsetFromEnd = 0}) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 2.5),
      child: InkWell(
        onTap: () => _insert(insertVal, cursorOffsetFromEnd: cursorOffsetFromEnd),
        borderRadius: BorderRadius.circular(7),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
          decoration: BoxDecoration(
            color: const Color(0xFF202636),
            borderRadius: BorderRadius.circular(7),
            border: Border.all(color: const Color(0xFF333C52), width: 1),
          ),
          child: Text(
            label,
            style: const TextStyle(
              fontSize: 13,
              color: Color(0xFF93C5FD),
              fontWeight: FontWeight.bold,
              fontFamily: 'monospace',
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildActionKey(String label, IconData? icon, VoidCallback onTap, {required Color color}) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(9),
      child: Container(
        height: 42,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.18),
          borderRadius: BorderRadius.circular(9),
          border: Border.all(color: color.withValues(alpha: 0.4), width: 1),
        ),
        child: icon != null
            ? Icon(icon, color: color, size: 18)
            : Text(
                label,
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: color),
              ),
      ),
    );
  }

  Widget _buildSolveKey() {
    return InkWell(
      onTap: widget.onSolve,
      borderRadius: BorderRadius.circular(9),
      child: Container(
        height: 42,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFF2563EB), Color(0xFF1D4ED8)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(9),
          boxShadow: [
            BoxShadow(
              color: const Color(0xFF2563EB).withValues(alpha: 0.35),
              blurRadius: 5,
              offset: const Offset(0, 2),
            )
          ],
        ),
        child: const Text(
          'حل',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ),
    );
  }
}
