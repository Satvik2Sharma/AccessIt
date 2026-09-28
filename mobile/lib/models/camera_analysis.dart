// Sahayak AI — Mobile Camera Analysis Models
// Represents structured vision detections, clock directions, and multimodal guidance.

class CameraDetectedObject {
  final String label;
  final double confidence;
  final String clockDirection;
  final String relativeDirection;
  final String proximity;
  final String elevation;
  final List<double>? bbox;

  CameraDetectedObject({
    required this.label,
    required this.confidence,
    required this.clockDirection,
    required this.relativeDirection,
    required this.proximity,
    required this.elevation,
    this.bbox,
  });

  factory CameraDetectedObject.fromJson(Map<String, dynamic> json) {
    List<double>? parsedBbox;
    if (json['bbox'] is List) {
      parsedBbox = (json['bbox'] as List)
          .map((v) => (v as num).toDouble())
          .toList();
    }
    return CameraDetectedObject(
      label: json['label'] ?? json['object_label'] ?? 'object',
      confidence: ((json['confidence'] ?? 0.9) as num).toDouble(),
      clockDirection: json['clock_direction'] ?? "12 o'clock",
      relativeDirection: json['relative_direction'] ?? 'straight ahead',
      proximity: json['proximity'] ?? 'near',
      elevation: json['elevation'] ?? 'level',
      bbox: parsedBbox,
    );
  }
}

class CameraAnalysisData {
  final bool success;
  final String sessionId;
  final String mode;
  final List<CameraDetectedObject> objects;
  final List<String> texts;
  final String scene;
  final String guidance;
  final double confidence;
  final String? hapticCue;
  final String timestamp;

  CameraAnalysisData({
    required this.success,
    required this.sessionId,
    required this.mode,
    required this.objects,
    required this.texts,
    required this.scene,
    required this.guidance,
    required this.confidence,
    this.hapticCue,
    required this.timestamp,
  });

  factory CameraAnalysisData.fromJson(Map<String, dynamic> json) {
    final rawObjects = json['objects'] ??
        json['analysis']?['detected_objects'] ??
        [];
    final parsedObjects = <CameraDetectedObject>[];
    if (rawObjects is List) {
      for (final item in rawObjects) {
        if (item is Map<String, dynamic>) {
          parsedObjects.add(CameraDetectedObject.fromJson(item));
        }
      }
    }

    final rawTexts = json['text'] ??
        json['analysis']?['detected_texts'] ??
        [];
    final parsedTexts = <String>[];
    if (rawTexts is List) {
      for (final item in rawTexts) {
        if (item is String) {
          parsedTexts.add(item);
        } else if (item is Map && item['text'] != null) {
          parsedTexts.add(item['text'].toString());
        }
      }
    }

    final sceneStr = json['scene'] ??
        json['analysis']?['scene']?['summary'] ??
        'Scene analyzed';

    final guidanceStr = json['guidance'] ??
        json['assistance']?['spoken_response'] ??
        json['assistance']?['display_response'] ??
        'Object detected';

    final haptic = json['assistance']?['haptic_cue'] ??
        (parsedObjects.isNotEmpty ? 'PULSE_RIGHT' : null);

    return CameraAnalysisData(
      success: json['success'] == true,
      sessionId: json['session_id'] ?? 'cam_session',
      mode: json['mode'] ?? 'AUTO',
      objects: parsedObjects,
      texts: parsedTexts,
      scene: sceneStr,
      guidance: guidanceStr,
      confidence: ((json['confidence'] ?? 0.9) as num).toDouble(),
      hapticCue: haptic,
      timestamp: json['timestamp'] ?? DateTime.now().toIso8601String(),
    );
  }
}
