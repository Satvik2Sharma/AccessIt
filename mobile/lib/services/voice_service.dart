// Sahayak AI — Mobile Voice Assistant & Speech Service
// Safe microphone permissions, STT initialization, speech synthesis, and text fallback.

import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';

class MobileVoiceService {
  static final MobileVoiceService _instance = MobileVoiceService._internal();
  factory MobileVoiceService() => _instance;
  MobileVoiceService._internal();

  final stt.SpeechToText _speech = stt.SpeechToText();
  final FlutterTts _tts = FlutterTts();

  bool _isInitialized = false;
  bool _isListening = false;
  bool _isAvailable = false;
  String _lastWords = '';

  bool get isListening => _isListening;
  bool get isAvailable => _isAvailable;
  String get lastWords => _lastWords;

  /// Initializes Speech-to-Text and TTS engines safely.
  Future<bool> initialize({String language = 'en-US'}) async {
    try {
      _isAvailable = await _speech.initialize(
        onError: (val) => debugPrint('STT Error: ${val.errorMsg}'),
        onStatus: (val) {
          if (val == 'done' || val == 'notListening') {
            _isListening = false;
          }
        },
      );

      await _tts.setLanguage(language.toLowerCase().startsWith('hi') ? 'hi-IN' : 'en-US');
      await _tts.setSpeechRate(0.5);
      await _tts.setVolume(1.0);
      await _tts.setPitch(1.0);

      _isInitialized = true;
      return _isAvailable;
    } catch (e) {
      debugPrint('Voice service initialization error: $e');
      _isAvailable = false;
      return false;
    }
  }

  /// Starts listening to voice input with callbacks.
  Future<void> startListening({
    required Function(String recognizedWords) onResult,
    VoidCallback? onComplete,
    String? localeId,
  }) async {
    if (!_isInitialized) {
      await initialize();
    }

    if (!_isAvailable) {
      debugPrint('STT not available on this device');
      return;
    }

    _lastWords = '';
    _isListening = true;

    try {
      await _speech.listen(
        onResult: (result) {
          _lastWords = result.recognizedWords;
          onResult(_lastWords);
          if (result.finalResult) {
            _isListening = false;
            if (onComplete != null) onComplete();
          }
        },
        listenOptions: stt.SpeechListenOptions(
          listenMode: stt.ListenMode.confirmation,
          cancelOnError: true,
          partialResults: true,
        ),

      );
    } catch (e) {
      debugPrint('Error starting STT listen: $e');
      _isListening = false;
    }
  }

  /// Stops active listening
  Future<void> stopListening() async {
    if (_isListening) {
      await _speech.stop();
      _isListening = false;
    }
  }

  /// Synthesizes spoken output via Text-To-Speech
  Future<void> speak(String text, {String? language}) async {
    if (text.trim().isEmpty) return;
    try {
      if (language != null) {
        final langCode = language.toLowerCase().startsWith('hi') ? 'hi-IN' : 'en-US';
        await _tts.setLanguage(langCode);
      }
      await _tts.speak(text);
    } catch (e) {
      debugPrint('TTS speak error: $e');
    }
  }

  /// Stops current speech output
  Future<void> stopSpeaking() async {
    try {
      await _tts.stop();
    } catch (_) {}
  }

  /// Text Input Fallback Modal for environments where microphone is restricted or unavailable
  static Future<String?> showTextFallbackDialog({
    required BuildContext context,
    required String title,
    String hintText = 'Type your command or query...',
    String initialText = '',
    bool isHindi = false,
  }) async {
    final controller = TextEditingController(text: initialText);
    return showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(title),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: InputDecoration(
            hintText: hintText,
            border: const OutlineInputBorder(),
          ),
          onSubmitted: (val) => Navigator.pop(ctx, val.trim()),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, null),
            child: Text(isHindi ? 'रद्द करें' : 'Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, controller.text.trim()),
            child: Text(isHindi ? 'भेजें' : 'Submit'),
          ),
        ],
      ),
    );
  }
}
