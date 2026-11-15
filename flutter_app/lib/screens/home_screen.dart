import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_math_fork/flutter_math.dart';
import 'package:image_picker/image_picker.dart';
import '../core/api_service.dart';
import '../core/latex_formatter.dart';
import '../models/solution_step.dart';
import '../widgets/step_card.dart';
import '../widgets/math_keyboard.dart';
import '../widgets/handwriting_canvas_dialog.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _eqController = TextEditingController(text: '3x - 9 = 15');
  final FocusNode _focusNode = FocusNode();
  final ApiService _api = ApiService();
  final ImagePicker _imagePicker = ImagePicker();

  bool _isLoading = false;
  bool _isBackendOnline = false;
  bool _showCustomKeyboard = true;
  String? _errorMessage;
  SolveResult? _result;

  // Quick mathematical presets for rapid testing and demonstrations
  final List<Map<String, String>> _presets = [
    {'label': 'تبسيط كسر (6/8)', 'eq': '6/8'},
    {'label': 'أولويات (100 - 25 × 3 + 14)', 'eq': r'100 - 25 \times 3 + 14'},
    {'label': 'كسر مركب (8×9÷7 + 5)', 'eq': r'8 \times 9 \div 7 + 5'},
    {'label': 'معادلة خطية (3x - 9 = 15)', 'eq': '3x - 9 = 15'},
    {'label': 'معادلة تربيعية (x² - 5x + 6 = 0)', 'eq': 'x^2 - 5x + 6 = 0'},
    {'label': 'تكامل (∫(2x + 3)dx)', 'eq': r'\int (2x + 3) dx'},
  ];

  @override
  void initState() {
    super.initState();
    _checkBackendStatus();
    _handleSolve();
  }

  @override
  void dispose() {
    _eqController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  Future<void> _checkBackendStatus() async {
    final online = await _api.checkHealth();
    if (!online) {
      // Try auto discovery on local subnet
      await _api.autoDiscoverBackend();
    }
    final finalStatus = await _api.checkHealth();
    if (mounted) {
      setState(() => _isBackendOnline = finalStatus);
    }
  }

  void _copyToClipboard(String text, String message) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Directionality(
          textDirection: TextDirection.rtl,
          child: Row(
            children: [
              const Icon(Icons.check_circle, color: Color(0xFF10B981), size: 18),
              const SizedBox(width: 8),
              Text(message, style: const TextStyle(fontSize: 13)),
            ],
          ),
        ),
        backgroundColor: const Color(0xFF1E2230),
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  Future<void> _pasteFromClipboard() async {
    final data = await Clipboard.getData(Clipboard.kTextPlain);
    if (data != null && data.text != null && data.text!.isNotEmpty) {
      setState(() {
        _eqController.text = data.text!.trim();
      });
      _handleSolve();
    }
  }

  void _clearInput() {
    _eqController.clear();
    setState(() {
      _errorMessage = null;
    });
  }

  void _loadPreset(String eq) {
    setState(() {
      _eqController.text = eq;
    });
    _handleSolve();
  }

  // Vision OCR: Handle Camera or Gallery photo upload
  Future<void> _pickAndRecognizeImage(ImageSource source) async {
    try {
      final XFile? file = await _imagePicker.pickImage(
        source: source,
        maxWidth: 1600,
        maxHeight: 1600,
        imageQuality: 90,
      );

      if (file == null) return;

      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });

      final Uint8List bytes = await file.readAsBytes();
      final recognizedLatex = await _api.recognizeImage(bytes);

      if (mounted) {
        setState(() {
          _eqController.text = recognizedLatex;
          _isLoading = false;
        });
        _copyToClipboard(recognizedLatex, 'تم استخراج المعادلة عبر الرؤية الحاسوبية بنجاح');
        _handleSolve();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = 'تعذر معالجة الصورة: $e';
        });
      }
    }
  }

  // Vision OCR: Open Handwriting Drawing Canvas
  void _openHandwritingCanvas() {
    showDialog(
      context: context,
      builder: (ctx) => HandwritingCanvasDialog(
        onRecognize: (Uint8List bytes) async {
          setState(() {
            _isLoading = true;
            _errorMessage = null;
          });

          final recognizedLatex = await _api.recognizeImage(bytes);

          if (mounted) {
            setState(() {
              _eqController.text = recognizedLatex;
              _isLoading = false;
            });
            _copyToClipboard(recognizedLatex, 'تم استخراج المعادلة من خط اليد بنجاح');
            _handleSolve();
          }
        },
      ),
    );
  }

  void _copyFullSolution() {
    if (_result == null) return;
    final buf = StringBuffer();
    buf.writeln('=== حل خوارزمي الرياضي الموثق ===');
    buf.writeln('المسألة: ${_eqController.text}');
    buf.writeln('النتيجة النهائية: ${_result!.finalAnswer}');
    buf.writeln('نمط التشغيل: ${_api.isUsingLocalEngine ? "المحرك المحلي المدمج في الهاتف" : "خادم الذكاء الاصطناعي الهجين"}');
    buf.writeln('زمن المعالجة: ${_result!.computationTimeMs} ms\n');
    buf.writeln('--- مسار الاستدلال والخطوات المنهجية ---');
    for (final s in _result!.steps) {
      buf.writeln('الخطوة ${s.stepNum}: [${s.ruleNameAr}]');
      buf.writeln('المعادلة: ${s.latex}');
      buf.writeln('الشرح التعليمي: ${s.explanationAr}\n');
    }
    _copyToClipboard(buf.toString(), 'تم نسخ خطوات الحل والشرح بالكامل إلى الحافظة');
  }

  Future<void> _handleSolve() async {
    final eq = _eqController.text.trim();
    if (eq.isEmpty) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _result = null;
    });

    try {
      final res = await _api.solveEquation(eq);
      if (mounted) {
        setState(() {
          _isLoading = false;
          _result = res;
          _isBackendOnline = !_api.isUsingLocalEngine;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = e.toString().replaceFirst('Exception: ', '');
        });
      }
    }
  }

  void _showServerConfigDialog() {
    final ipCtrl = TextEditingController(text: _api.baseUrl);
    bool testing = false;
    String? testMsg;
    bool? testSuccess;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDialogState) => Directionality(
          textDirection: TextDirection.rtl,
          child: AlertDialog(
            backgroundColor: const Color(0xFF161922),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
              side: const BorderSide(color: Color(0xFF282D3D), width: 1.2),
            ),
            title: const Row(
              children: [
                Icon(Icons.lan_outlined, color: Color(0xFF10B981), size: 22),
                SizedBox(width: 8),
                Text(
                  'إعدادات الاتصال والوضع المحلي',
                  style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: const Color(0xFF10B981).withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: const Color(0xFF10B981).withValues(alpha: 0.3)),
                    ),
                    child: const Text(
                      '📱 التطبيق مزود بمحرك محلي مدمج (On-Device Local Engine) يعمل على الهاتف مباشرة بدون إنترنت، ويتصل تلقائياً بالكمبيوتر عند توفر الشبكة.',
                      style: TextStyle(color: Color(0xFF6EE7B7), fontSize: 11.5),
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'عناوين الخادم السريعة:',
                    style: TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      ActionChip(
                        backgroundColor: const Color(0xFF1E2230),
                        side: const BorderSide(color: Color(0xFF32394D)),
                        avatar: const Icon(Icons.wifi_find, size: 15, color: Color(0xFF10B981)),
                        label: const Text('استكشاف تلقائي على الشبكة', style: TextStyle(color: Colors.white, fontSize: 11)),
                        onPressed: () async {
                          setDialogState(() {
                            testing = true;
                            testMsg = 'جاري فحص الشبكة واستكشاف الخادم...';
                          });
                          final found = await _api.autoDiscoverBackend();
                          setDialogState(() {
                            testing = false;
                            testSuccess = found;
                            ipCtrl.text = _api.baseUrl;
                            testMsg = found
                                ? 'تم العثور على خادم خوارزمي: ${_api.baseUrl}'
                                : 'لم يتم العثور على خادم خارجي. التطبيق سيعمل بالوضع المحلي المستقل على الهاتف.';
                          });
                        },
                      ),
                      ActionChip(
                        backgroundColor: const Color(0xFF1E2230),
                        side: const BorderSide(color: Color(0xFF32394D)),
                        avatar: const Icon(Icons.computer, size: 15, color: Color(0xFF3B82F6)),
                        label: const Text('الكمبيوتر (127.0.0.1:8000)', style: TextStyle(color: Colors.white, fontSize: 11)),
                        onPressed: () {
                          setDialogState(() {
                            ipCtrl.text = ApiService.defaultLocalUrl;
                          });
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  Directionality(
                    textDirection: TextDirection.ltr,
                    child: TextField(
                      controller: ipCtrl,
                      style: const TextStyle(color: Colors.white, fontFamily: 'monospace', fontSize: 13),
                      decoration: InputDecoration(
                        labelText: 'Server URL',
                        labelStyle: const TextStyle(color: Colors.white54, fontSize: 12),
                        filled: true,
                        fillColor: const Color(0xFF0F1117),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFF32394D))),
                        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFF32394D))),
                        focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFF10B981))),
                      ),
                    ),
                  ),
                  if (testMsg != null) ...[
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: testSuccess == true
                            ? const Color(0xFF10B981).withValues(alpha: 0.15)
                            : const Color(0xFFEF4444).withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: testSuccess == true ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                          width: 1,
                        ),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            testSuccess == true ? Icons.check_circle : Icons.info_outline,
                            color: testSuccess == true ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                            size: 18,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              testMsg!,
                              style: TextStyle(
                                color: testSuccess == true ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                                fontSize: 11,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('إلغاء', style: TextStyle(color: Colors.white54)),
              ),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF10B981),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                onPressed: testing
                    ? null
                    : () async {
                        setDialogState(() {
                          testing = true;
                          testMsg = null;
                        });
                        final targetUrl = ipCtrl.text.trim();
                        final ok = await _api.checkHealth(targetUrl);
                        setDialogState(() {
                          testing = false;
                          testSuccess = ok;
                          testMsg = ok
                              ? 'تم الاتصال بالخادم بنجاح!'
                              : 'تعذر الوصول إلى هذا العنوان. سيتم تفعيل المحرك المحلي على الهاتف.';
                        });
                        if (ok) {
                          _api.baseUrl = targetUrl;
                          if (mounted) {
                            setState(() => _isBackendOnline = true);
                          }
                          Future.delayed(const Duration(milliseconds: 600), () {
                            if (ctx.mounted) Navigator.pop(ctx);
                          });
                        }
                      },
                child: testing
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Text('تطبيق واختبار'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Physical Windows Keyboard Shortcuts Map
    return CallbackShortcuts(
      bindings: <ShortcutActivator, VoidCallback>{
        const SingleActivator(LogicalKeyboardKey.enter): () {
          if (!_isLoading) _handleSolve();
        },
        const SingleActivator(LogicalKeyboardKey.numpadEnter): () {
          if (!_isLoading) _handleSolve();
        },
        const SingleActivator(LogicalKeyboardKey.escape): _clearInput,
        const SingleActivator(LogicalKeyboardKey.keyK, control: true): () {
          setState(() => _showCustomKeyboard = !_showCustomKeyboard);
        },
        const SingleActivator(LogicalKeyboardKey.f2): () {
          setState(() => _showCustomKeyboard = !_showCustomKeyboard);
        },
      },
      child: Focus(
        autofocus: true,
        child: Scaffold(
          backgroundColor: const Color(0xFF0F1117),
          appBar: AppBar(
            backgroundColor: const Color(0xFF161922),
            elevation: 0,
            title: Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFF10B981).withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFF10B981), width: 1),
                  ),
                  child: const Text(
                    'خوارزمي',
                    style: TextStyle(
                      color: Color(0xFF10B981),
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                const Flexible(
                  child: Text(
                    'المعلم الرياضي والحل الرمزي الموثق',
                    style: TextStyle(fontSize: 13, color: Colors.white70),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            actions: [
              IconButton(
                tooltip: 'إعدادات الاتصال والوضع المحلي',
                icon: const Icon(
                  Icons.lan_outlined,
                  color: Colors.white70,
                  size: 20,
                ),
                onPressed: _showServerConfigDialog,
              ),
              IconButton(
                tooltip: _showCustomKeyboard ? 'إخفاء الكيبورد الرياضي (F2 / Ctrl+K)' : 'إظهار الكيبورد الرياضي (F2 / Ctrl+K)',
                icon: Icon(
                  _showCustomKeyboard ? Icons.keyboard_hide_outlined : Icons.keyboard_outlined,
                  color: Colors.white70,
                ),
                onPressed: () => setState(() => _showCustomKeyboard = !_showCustomKeyboard),
              ),
              InkWell(
                onTap: _showServerConfigDialog,
                borderRadius: BorderRadius.circular(8),
                child: Padding(
                  padding: const EdgeInsets.only(right: 8, left: 12, top: 8, bottom: 8),
                  child: Row(
                    children: [
                      Container(
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: _isBackendOnline ? const Color(0xFF10B981) : const Color(0xFF3B82F6),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        _isBackendOnline ? 'الخادم نشط' : 'محلي (على الهاتف)',
                        style: TextStyle(
                          fontSize: 11.5,
                          fontWeight: FontWeight.w600,
                          color: _isBackendOnline ? const Color(0xFF10B981) : const Color(0xFF60A5FA),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          body: Directionality(
            textDirection: TextDirection.rtl,
            child: Column(
              children: [
                // Scrollable Main Content
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Live LaTeX Preview & Input Container
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: const Color(0xFF1A1D27),
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: const Color(0xFF282D3D), width: 1.2),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  const Row(
                                    children: [
                                      Icon(Icons.auto_awesome, color: Color(0xFF60A5FA), size: 16),
                                      SizedBox(width: 6),
                                      Text(
                                        'المعادلة المدخلة (معاينة حية منسقة):',
                                        style: TextStyle(color: Colors.white70, fontSize: 13, fontWeight: FontWeight.w600),
                                      ),
                                    ],
                                  ),
                                  if (_isLoading)
                                    const Row(
                                      children: [
                                        Text('جاري المعالجة...', style: TextStyle(color: Color(0xFF60A5FA), fontSize: 11)),
                                        SizedBox(width: 6),
                                        SizedBox(
                                          width: 14,
                                          height: 14,
                                          child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF3B82F6)),
                                        ),
                                      ],
                                    ),
                                ],
                              ),
                              const SizedBox(height: 10),

                              // Live Rendered Math Display (Safe formatting via LatexFormatter)
                              Container(
                                padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 16),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF10121A),
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(color: const Color(0xFF32394D)),
                                ),
                                alignment: Alignment.center,
                                child: SingleChildScrollView(
                                  scrollDirection: Axis.horizontal,
                                  child: Math.tex(
                                    LatexFormatter.formatForPreview(_eqController.text),
                                    textStyle: const TextStyle(
                                      fontSize: 26,
                                      color: Color(0xFF60A5FA),
                                      fontWeight: FontWeight.bold,
                                    ),
                                    onErrorFallback: (err) => Text(
                                      _eqController.text.isNotEmpty ? _eqController.text : '...',
                                      style: const TextStyle(color: Color(0xFF93C5FD), fontSize: 18, fontFamily: 'monospace'),
                                    ),
                                  ),
                                ),
                              ),

                              const SizedBox(height: 10),

                              // Direct Text Input Field (Interactive with Windows Physical Keyboard)
                              Directionality(
                                textDirection: TextDirection.ltr,
                                child: TextField(
                                  controller: _eqController,
                                  focusNode: _focusNode,
                                  onSubmitted: (_) => _handleSolve(),
                                  onChanged: (_) => setState(() {}),
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontFamily: 'monospace',
                                    fontSize: 14,
                                  ),
                                  decoration: InputDecoration(
                                    prefixIcon: const Icon(Icons.edit_note_outlined, color: Colors.white38, size: 18),
                                    suffixIcon: IconButton(
                                      tooltip: 'مسح (Escape)',
                                      icon: const Icon(Icons.clear, color: Colors.white38, size: 16),
                                      onPressed: _clearInput,
                                    ),
                                    hintText: 'اكتب هنا أو استخدم الكاميرا / الرسم (مثال: 6/8 أو 3x - 9 = 15)',
                                    hintStyle: const TextStyle(color: Colors.white24, fontSize: 12),
                                    filled: true,
                                    fillColor: const Color(0xFF141722),
                                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                    border: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(8),
                                      borderSide: const BorderSide(color: Color(0xFF282D3D)),
                                    ),
                                    enabledBorder: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(8),
                                      borderSide: const BorderSide(color: Color(0xFF282D3D)),
                                    ),
                                    focusedBorder: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(8),
                                      borderSide: const BorderSide(color: Color(0xFF3B82F6), width: 1.2),
                                    ),
                                  ),
                                ),
                              ),

                              const SizedBox(height: 10),

                              // Vision & Smart Input Toolbar (Handwriting Canvas, Camera OCR, Gallery Picker)
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF131722),
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(color: const Color(0xFF283042)),
                                ),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                                  children: [
                                    // 1. Handwriting Canvas
                                    TextButton.icon(
                                      icon: const Icon(Icons.draw_outlined, size: 16, color: Color(0xFF60A5FA)),
                                      label: const Text('كتابة باليد', style: TextStyle(color: Color(0xFF93C5FD), fontSize: 12, fontWeight: FontWeight.bold)),
                                      onPressed: _openHandwritingCanvas,
                                    ),
                                    Container(width: 1, height: 20, color: const Color(0xFF283042)),

                                    // 2. Camera OCR
                                    TextButton.icon(
                                      icon: const Icon(Icons.camera_alt_outlined, size: 16, color: Color(0xFF34D399)),
                                      label: const Text('تصوير بالكاميرا', style: TextStyle(color: Color(0xFF6EE7B7), fontSize: 12, fontWeight: FontWeight.bold)),
                                      onPressed: () => _pickAndRecognizeImage(ImageSource.camera),
                                    ),
                                    Container(width: 1, height: 20, color: const Color(0xFF283042)),

                                    // 3. Gallery OCR
                                    TextButton.icon(
                                      icon: const Icon(Icons.photo_library_outlined, size: 16, color: Color(0xFFFBBF24)),
                                      label: const Text('من المعرض', style: TextStyle(color: Color(0xFFFDE68A), fontSize: 12, fontWeight: FontWeight.bold)),
                                      onPressed: () => _pickAndRecognizeImage(ImageSource.gallery),
                                    ),
                                  ],
                                ),
                              ),

                              const SizedBox(height: 10),

                              // Quick Action Buttons Toolbar (Paste, Copy, Clear, Solve)
                              Wrap(
                                spacing: 8,
                                runSpacing: 6,
                                alignment: WrapAlignment.spaceBetween,
                                crossAxisAlignment: WrapCrossAlignment.center,
                                children: [
                                  Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      TextButton.icon(
                                        icon: const Icon(Icons.paste_outlined, size: 15, color: Color(0xFF93C5FD)),
                                        label: const Text('لصق', style: TextStyle(fontSize: 12, color: Color(0xFF93C5FD))),
                                        style: TextButton.styleFrom(
                                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                          backgroundColor: const Color(0xFF232938),
                                        ),
                                        onPressed: _pasteFromClipboard,
                                      ),
                                      const SizedBox(width: 6),
                                      TextButton.icon(
                                        icon: const Icon(Icons.copy_outlined, size: 15, color: Colors.white70),
                                        label: const Text('نسخ', style: TextStyle(fontSize: 12, color: Colors.white70)),
                                        style: TextButton.styleFrom(
                                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                          backgroundColor: const Color(0xFF232938),
                                        ),
                                        onPressed: () => _copyToClipboard(_eqController.text, 'تم نسخ صيغة المعادلة'),
                                      ),
                                      const SizedBox(width: 6),
                                      TextButton.icon(
                                        icon: const Icon(Icons.delete_sweep_outlined, size: 15, color: Colors.white54),
                                        label: const Text('مسح', style: TextStyle(fontSize: 12, color: Colors.white54)),
                                        style: TextButton.styleFrom(
                                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                          backgroundColor: const Color(0xFF232938),
                                        ),
                                        onPressed: _clearInput,
                                      ),
                                    ],
                                  ),
                                  ElevatedButton.icon(
                                    icon: const Icon(Icons.play_arrow_rounded, size: 18),
                                    label: const Text('حل المسألة (Enter)', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: const Color(0xFF2563EB),
                                      foregroundColor: Colors.white,
                                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                    ),
                                    onPressed: _isLoading ? null : _handleSolve,
                                  ),
                                ],
                              ),

                              const SizedBox(height: 12),

                              // Quick Math Presets Chips
                              SingleChildScrollView(
                                scrollDirection: Axis.horizontal,
                                child: Row(
                                  children: [
                                    const Padding(
                                      padding: EdgeInsets.only(left: 8),
                                      child: Text(
                                        'أمثلة سريعة:',
                                        style: TextStyle(color: Colors.white54, fontSize: 11),
                                      ),
                                    ),
                                    ..._presets.map(
                                      (p) => Padding(
                                        padding: const EdgeInsets.symmetric(horizontal: 3),
                                        child: ActionChip(
                                          label: Text(p['label']!, style: const TextStyle(fontSize: 11, color: Color(0xFF93C5FD))),
                                          backgroundColor: const Color(0xFF131722),
                                          side: const BorderSide(color: Color(0xFF283042)),
                                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                          onPressed: () => _loadPreset(p['eq']!),
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(height: 16),

                        // Error Message Banner (if any)
                        if (_errorMessage != null)
                          Container(
                            padding: const EdgeInsets.all(14),
                            margin: const EdgeInsets.only(bottom: 16),
                            decoration: BoxDecoration(
                              color: const Color(0xFF7F1D1D).withValues(alpha: 0.3),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: const Color(0xFFEF4444), width: 1.2),
                            ),
                            child: Row(
                              children: [
                                const Icon(Icons.error_outline, color: Color(0xFFEF4444), size: 20),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Text(
                                    _errorMessage!,
                                    style: const TextStyle(color: Color(0xFFFCA5A5), fontSize: 13),
                                  ),
                                ),
                              ],
                            ),
                          ),

                        // ========================================================
                        // RESULTS SECTION: Clear Separation (Result vs Explanation)
                        // ========================================================
                        if (_result != null) ...[
                          // 1. Prominent Final Result Card
                          Container(
                            padding: const EdgeInsets.all(18),
                            margin: const EdgeInsets.only(bottom: 22),
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: [
                                  const Color(0xFF064E3B).withValues(alpha: 0.55),
                                  const Color(0xFF0F172A),
                                ],
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                              ),
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: const Color(0xFF10B981), width: 1.8),
                              boxShadow: [
                                BoxShadow(
                                  color: const Color(0xFF10B981).withValues(alpha: 0.15),
                                  blurRadius: 18,
                                  offset: const Offset(0, 4),
                                ),
                              ],
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Expanded(
                                      child: Row(
                                        children: [
                                          Container(
                                            padding: const EdgeInsets.all(6),
                                            decoration: const BoxDecoration(
                                              color: Color(0xFF10B981),
                                              shape: BoxShape.circle,
                                            ),
                                            child: const Icon(Icons.check, color: Colors.black, size: 16),
                                          ),
                                          const SizedBox(width: 8),
                                          const Flexible(
                                            child: Text(
                                              'النتيجة النهائية الموثقة رمزياً',
                                              style: TextStyle(
                                                color: Color(0xFF6EE7B7),
                                                fontSize: 14,
                                                fontWeight: FontWeight.bold,
                                              ),
                                              overflow: TextOverflow.ellipsis,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                      decoration: BoxDecoration(
                                        color: Colors.white10,
                                        borderRadius: BorderRadius.circular(6),
                                      ),
                                      child: Text(
                                        '${_result!.computationTimeMs} ms • ${_api.isUsingLocalEngine ? "محرك الهاتف" : "الخادم"}',
                                        style: const TextStyle(color: Colors.white60, fontSize: 11, fontFamily: 'monospace'),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 14),

                                // Large Display of Final Result
                                Container(
                                  padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF090D14),
                                    borderRadius: BorderRadius.circular(10),
                                    border: Border.all(color: const Color(0xFF1E2D3D)),
                                  ),
                                  alignment: Alignment.center,
                                  child: SingleChildScrollView(
                                    scrollDirection: Axis.horizontal,
                                    child: Math.tex(
                                      _result!.finalAnswer,
                                      textStyle: const TextStyle(
                                        color: Color(0xFF34D399),
                                        fontSize: 28,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 12),

                                // Quick Action Buttons for the Result
                                Wrap(
                                  alignment: WrapAlignment.end,
                                  spacing: 8,
                                  runSpacing: 8,
                                  children: [
                                    OutlinedButton.icon(
                                      icon: const Icon(Icons.copy, size: 14),
                                      label: const Text('نسخ النتيجة فقط', style: TextStyle(fontSize: 12)),
                                      style: OutlinedButton.styleFrom(
                                        foregroundColor: const Color(0xFF6EE7B7),
                                        side: const BorderSide(color: Color(0xFF059669)),
                                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                      ),
                                      onPressed: () => _copyToClipboard(_result!.finalAnswer, 'تم نسخ النتيجة النهائية'),
                                    ),
                                    ElevatedButton.icon(
                                      icon: const Icon(Icons.content_copy_outlined, size: 14),
                                      label: const Text('نسخ الحل كاملاً', style: TextStyle(fontSize: 12)),
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: const Color(0xFF059669),
                                        foregroundColor: Colors.white,
                                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                      ),
                                      onPressed: _copyFullSolution,
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),

                          // 2. Pedagogical Step-by-Step Explanation Section
                          Container(
                            margin: const EdgeInsets.only(bottom: 8),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Row(
                                    children: [
                                      const Icon(Icons.menu_book_outlined, color: Color(0xFF60A5FA), size: 20),
                                      const SizedBox(width: 8),
                                      Flexible(
                                        child: Text(
                                          'مسار الاستدلال والشرح المنهجي (${_result!.steps.length} خطوات):',
                                          style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                TextButton.icon(
                                  icon: const Icon(Icons.copy_all_outlined, size: 14, color: Colors.white54),
                                  label: const Text('نسخ الشرح', style: TextStyle(color: Colors.white54, fontSize: 11)),
                                  onPressed: _copyFullSolution,
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 8),

                          // Steps List
                          ..._result!.steps.map((s) => StepCard(step: s)),
                        ],
                      ],
                    ),
                  ),
                ),

                // Bottom Dedicated Math Keyboard
                if (_showCustomKeyboard)
                  MathKeyboard(
                    controller: _eqController,
                    onSolve: _handleSolve,
                    onChanged: () => setState(() {}),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
