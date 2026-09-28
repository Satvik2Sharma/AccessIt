// Sahayak AI — Mobile Camera Service
// Safe hardware camera lifecycle, front/back lens toggle, snapshot capture,
// and rate-controlled frame stream analysis for vision & ISL.

import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/foundation.dart';

enum CameraState { uninitialized, initializing, active, paused, permissionDenied, unavailable, error }

class MobileCameraService {
  static final MobileCameraService _instance = MobileCameraService._internal();
  factory MobileCameraService() => _instance;
  MobileCameraService._internal();

  CameraController? _controller;
  List<CameraDescription> _cameras = [];
  int _selectedCameraIndex = 0;
  CameraState _state = CameraState.uninitialized;
  String? _errorMessage;

  Timer? _analysisTimer;
  bool _isProcessingFrame = false;

  CameraController? get controller => _controller;
  CameraState get state => _state;
  bool get isReady => _state == CameraState.active && _controller != null && _controller!.value.isInitialized;
  String? get errorMessage => _errorMessage;
  bool get hasMultipleCameras => _cameras.length > 1;
  CameraLensDirection get currentLensDirection =>
      _cameras.isNotEmpty ? _cameras[_selectedCameraIndex].lensDirection : CameraLensDirection.back;

  /// Initializes the device camera safely.
  Future<bool> initialize({CameraLensDirection preferredLens = CameraLensDirection.back}) async {
    _state = CameraState.initializing;
    _errorMessage = null;

    try {
      _cameras = await availableCameras();
      if (_cameras.isEmpty) {
        _state = CameraState.unavailable;
        _errorMessage = 'No camera hardware found on this device.';
        return false;
      }

      // Find index matching preferredLens
      int targetIndex = _cameras.indexWhere((c) => c.lensDirection == preferredLens);
      if (targetIndex < 0) targetIndex = 0;
      _selectedCameraIndex = targetIndex;

      await _initController(_cameras[_selectedCameraIndex]);
      _state = CameraState.active;
      return true;
    } on CameraException catch (e) {
      if (e.code == 'CameraAccessDenied' ||
          e.code == 'CameraAccessDeniedWithoutPrompt' ||
          e.code == 'cameraPermissionNotGranted') {
        _state = CameraState.permissionDenied;
        _errorMessage = 'Camera permission denied. Please grant camera access in system settings.';
      } else {
        _state = CameraState.error;
        _errorMessage = 'Camera error: ${e.description ?? e.code}';
      }
      return false;
    } catch (e) {
      _state = CameraState.error;
      _errorMessage = 'Camera initialization failed: $e';
      return false;
    }
  }

  Future<void> _initController(CameraDescription camera) async {
    final oldController = _controller;
    if (oldController != null) {
      await oldController.dispose();
    }

    final newController = CameraController(
      camera,
      ResolutionPreset.medium,
      enableAudio: false,
      imageFormatGroup: ImageFormatGroup.jpeg,
    );

    _controller = newController;
    await newController.initialize();
  }

  /// Switch between back and front camera
  Future<bool> toggleLens() async {
    if (_cameras.length < 2) return false;

    _selectedCameraIndex = (_selectedCameraIndex + 1) % _cameras.length;
    try {
      _state = CameraState.initializing;
      await _initController(_cameras[_selectedCameraIndex]);
      _state = CameraState.active;
      return true;
    } catch (e) {
      _state = CameraState.error;
      _errorMessage = 'Failed to switch camera: $e';
      return false;
    }
  }

  /// Captures a single image frame as compressed JPEG bytes
  Future<Uint8List?> captureFrameBytes() async {
    if (!isReady) return null;

    try {
      final xFile = await _controller!.takePicture();
      return await xFile.readAsBytes();
    } catch (e) {
      debugPrint('Camera capture error: $e');
      return null;
    }
  }

  /// Starts controlled analysis stream at specified FPS (e.g. 1.0 to 2.0 frames per second).
  /// Never queues or overloads the backend: checks `_isProcessingFrame` mutex.
  void startAnalysisLoop({
    double fps = 1.0,
    required Future<void> Function(Uint8List frameBytes) onFrame,
  }) {
    stopAnalysisLoop();

    final intervalMs = (1000 / fps).clamp(500, 3000).toInt();
    _analysisTimer = Timer.periodic(Duration(milliseconds: intervalMs), (_) async {
      if (!isReady || _isProcessingFrame) return;

      _isProcessingFrame = true;
      try {
        final bytes = await captureFrameBytes();
        if (bytes != null && bytes.isNotEmpty) {
          await onFrame(bytes);
        }
      } catch (e) {
        debugPrint('Analysis frame error: $e');
      } finally {
        _isProcessingFrame = false;
      }
    });
  }

  /// Stops background frame sampling
  void stopAnalysisLoop() {
    _analysisTimer?.cancel();
    _analysisTimer = null;
    _isProcessingFrame = false;
  }

  /// Pause camera stream
  Future<void> pause() async {
    if (_controller != null && _controller!.value.isInitialized) {
      try {
        await _controller!.pausePreview();
        _state = CameraState.paused;
      } catch (_) {}
    }
  }

  /// Resume camera stream
  Future<void> resume() async {
    if (_controller != null && _controller!.value.isInitialized) {
      try {
        await _controller!.resumePreview();
        _state = CameraState.active;
      } catch (_) {}
    }
  }

  /// Cleanly disposes the controller and timers
  Future<void> dispose() async {
    stopAnalysisLoop();
    final controller = _controller;
    _controller = null;
    _state = CameraState.uninitialized;
    if (controller != null) {
      await controller.dispose();
    }
  }
}
