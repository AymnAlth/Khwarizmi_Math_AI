import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';

class HandwritingCanvasDialog extends StatefulWidget {
  final Function(Uint8List imageBytes) onRecognize;

  const HandwritingCanvasDialog({
    super.key,
    required this.onRecognize,
  });

  @override
  State<HandwritingCanvasDialog> createState() => _HandwritingCanvasDialogState();
}

class _DrawingPoint {
  final Offset offset;
  final Paint paint;
  _DrawingPoint({required this.offset, required this.paint});
}

class _HandwritingCanvasDialogState extends State<HandwritingCanvasDialog> {
  final GlobalKey _canvasKey = GlobalKey();
  final List<List<_DrawingPoint>> _strokes = [];
  List<_DrawingPoint> _currentStroke = [];

  bool _isEraser = false;
  final double _strokeWidth = 3.5;
  final Color _penColor = const Color(0xFF60A5FA);

  void _clearCanvas() {
    setState(() {
      _strokes.clear();
      _currentStroke.clear();
    });
  }

  void _undoStroke() {
    if (_strokes.isNotEmpty) {
      setState(() {
        _strokes.removeLast();
      });
    }
  }

  Future<void> _captureAndSubmit() async {
    if (_strokes.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('يرجى كتابة أو رسم معادلة أولاً على اللوحة.')),
        );
      }
      return;
    }

    try {
      final boundary = _canvasKey.currentContext?.findRenderObject() as RenderRepaintBoundary?;
      if (boundary == null) return;

      final ui.Image image = await boundary.toImage(pixelRatio: 2.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      if (byteData != null) {
        final bytes = byteData.buffer.asUint8List();
        if (mounted) {
          Navigator.pop(context);
        }
        widget.onRecognize(bytes);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('تعذر تحويل الرسم إلى صورة: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: const Color(0xFF131620),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: Color(0xFF282D3D), width: 1.5),
      ),
      insetPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
      child: Directionality(
        textDirection: TextDirection.rtl,
        child: Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.draw_outlined, color: Color(0xFF60A5FA), size: 22),
                      SizedBox(width: 8),
                      Text(
                        'كتابة المعادلة بخط اليد (Touch / Pen)',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white54, size: 20),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              const Text(
                'اكتب المعادلة بإصبعك أو القلم كما تكتب على ورقة حقيقية، وسيتعرف الذكاء الاصطناعي عليها فوراً:',
                style: TextStyle(color: Colors.white60, fontSize: 11),
              ),
              const SizedBox(height: 12),

              // Canvas Container with RepaintBoundary
              RepaintBoundary(
                key: _canvasKey,
                child: Container(
                  height: 260,
                  decoration: BoxDecoration(
                    color: const Color(0xFF0A0C12),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: const Color(0xFF32394D), width: 1.5),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(14),
                    child: GestureDetector(
                      onPanStart: (details) {
                        setState(() {
                          final paint = Paint()
                            ..color = _isEraser ? const Color(0xFF0A0C12) : _penColor
                            ..strokeCap = StrokeCap.round
                            ..strokeWidth = _isEraser ? 16.0 : _strokeWidth;
                          _currentStroke = [_DrawingPoint(offset: details.localPosition, paint: paint)];
                          _strokes.add(_currentStroke);
                        });
                      },
                      onPanUpdate: (details) {
                        setState(() {
                          final paint = Paint()
                            ..color = _isEraser ? const Color(0xFF0A0C12) : _penColor
                            ..strokeCap = StrokeCap.round
                            ..strokeWidth = _isEraser ? 16.0 : _strokeWidth;
                          _currentStroke.add(_DrawingPoint(offset: details.localPosition, paint: paint));
                        });
                      },
                      child: CustomPaint(
                        painter: _CanvasPainter(strokes: _strokes),
                        size: Size.infinite,
                      ),
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 12),

              // Tool Controls Row
              Wrap(
                alignment: WrapAlignment.spaceBetween,
                crossAxisAlignment: WrapCrossAlignment.center,
                runSpacing: 8,
                children: [
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Pen Tool
                      IconButton(
                        tooltip: 'القلم',
                        icon: Icon(
                          Icons.edit,
                          color: !_isEraser ? const Color(0xFF60A5FA) : Colors.white38,
                          size: 20,
                        ),
                        onPressed: () => setState(() => _isEraser = false),
                      ),
                      // Eraser Tool
                      IconButton(
                        tooltip: 'الممحاة',
                        icon: Icon(
                          Icons.cleaning_services_outlined,
                          color: _isEraser ? const Color(0xFFEF4444) : Colors.white38,
                          size: 20,
                        ),
                        onPressed: () => setState(() => _isEraser = true),
                      ),
                      // Undo
                      IconButton(
                        tooltip: 'تراجع',
                        icon: const Icon(Icons.undo, color: Colors.white60, size: 20),
                        onPressed: _undoStroke,
                      ),
                      // Clear
                      IconButton(
                        tooltip: 'مسح اللوحة بالكامل',
                        icon: const Icon(Icons.delete_outline, color: Colors.white60, size: 20),
                        onPressed: _clearCanvas,
                      ),
                    ],
                  ),

                  // Submit Button
                  ElevatedButton.icon(
                    icon: const Icon(Icons.auto_awesome, size: 16),
                    label: const Text('التعرف والحل الفوري', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF10B981),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    onPressed: _captureAndSubmit,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CanvasPainter extends CustomPainter {
  final List<List<_DrawingPoint>> strokes;

  _CanvasPainter({required this.strokes});

  @override
  void paint(Canvas canvas, Size size) {
    // Draw subtle math grid lines
    final gridPaint = Paint()
      ..color = const Color(0xFF1C2233).withValues(alpha: 0.5)
      ..strokeWidth = 1.0;

    for (double y = 20; y < size.height; y += 30) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }

    // Draw user strokes
    for (final stroke in strokes) {
      if (stroke.isEmpty) continue;
      for (int i = 0; i < stroke.length - 1; i++) {
        canvas.drawLine(stroke[i].offset, stroke[i + 1].offset, stroke[i].paint);
      }
      if (stroke.length == 1) {
        canvas.drawCircle(stroke[0].offset, stroke[0].paint.strokeWidth / 2, stroke[0].paint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant _CanvasPainter oldDelegate) => true;
}
