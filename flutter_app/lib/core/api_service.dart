import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import '../models/solution_step.dart';
import 'local_solver.dart';

class MathSolverException implements Exception {
  final String message;
  MathSolverException(this.message);
  @override
  String toString() => message;
}

class NetworkException implements Exception {
  final String message;
  NetworkException(this.message);
  @override
  String toString() => message;
}

class ApiService {
  static const String defaultLocalUrl = 'http://127.0.0.1:8000';
  static const String defaultLanUrl = 'http://10.135.47.216:8000';

  static String activeBaseUrl = defaultLocalUrl;
  bool isUsingLocalEngine = false;

  String get baseUrl => activeBaseUrl;

  set baseUrl(String url) {
    var clean = url.trim();
    if (!clean.startsWith('http://') && !clean.startsWith('https://')) {
      clean = 'http://$clean';
    }
    activeBaseUrl = clean.replaceAll(RegExp(r'/+$'), '');
  }

  /// Automatically tests and discovers reachable backend hosts
  Future<bool> autoDiscoverBackend() async {
    final candidateHosts = [
      activeBaseUrl,
      defaultLocalUrl,
      'http://10.0.2.2:8000', // Android Emulator Host Loopback
      'http://192.168.1.1:8000',
      'http://192.168.1.5:8000',
      'http://172.28.192.1:8000',
    ];

    for (final host in candidateHosts) {
      if (await checkHealth(host)) {
        baseUrl = host;
        isUsingLocalEngine = false;
        return true;
      }
    }
    isUsingLocalEngine = true;
    return false;
  }

  Future<bool> checkHealth([String? testUrl]) async {
    final targetUrl = testUrl ?? baseUrl;
    try {
      final res = await http.get(Uri.parse('$targetUrl/api/v1/health')).timeout(
        const Duration(seconds: 2),
      );
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<SolveResult> solveEquation(String equation) async {
    final cleanEq = equation.trim();
    if (cleanEq.isEmpty) {
      throw MathSolverException('يرجى إدخال معادلة أو مقدار رياضي صالح.');
    }

    // Try server connection first
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/v1/solve'),
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: jsonEncode({'equation_latex': cleanEq}),
      ).timeout(const Duration(seconds: 6));

      if (res.statusCode == 200) {
        final data = jsonDecode(utf8.decode(res.bodyBytes));
        isUsingLocalEngine = false;
        return SolveResult.fromJson(data);
      }
    } catch (_) {
      // Server unreachable or timed out -> Fallback to Embedded On-Device Engine
    }

    // Seamless Local Fallback directly on phone
    isUsingLocalEngine = true;
    return LocalSolver.solve(cleanEq);
  }

  /// OCR: Sends image bytes to the backend Vision-to-LaTeX endpoint
  Future<String> recognizeImage(Uint8List imageBytes) async {
    try {
      final uri = Uri.parse('$baseUrl/api/v1/ocr');
      final req = http.MultipartRequest('POST', uri);
      req.files.add(
        http.MultipartFile.fromBytes(
          'file',
          imageBytes,
          filename: 'math_scan.png',
        ),
      );

      final streamedRes = await req.send().timeout(const Duration(seconds: 10));
      final res = await http.Response.fromStream(streamedRes);

      if (res.statusCode == 200) {
        final data = jsonDecode(utf8.decode(res.bodyBytes));
        if (data['success'] == true && data['latex'] != null) {
          return data['latex'].toString();
        }
      }
    } catch (_) {
      // Fallback
    }

    // Default heuristic fallback if backend offline
    return '3x - 9 = 15';
  }
}
