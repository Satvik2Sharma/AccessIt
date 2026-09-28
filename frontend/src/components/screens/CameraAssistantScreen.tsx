import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useTwin } from '../../context/TwinContext';
import { 
  Camera, RefreshCw, Eye, Sparkles, Play, Square, 
  SwitchCamera, AlertTriangle, CheckCircle2, Loader2, Volume2, ShieldAlert
} from 'lucide-react';
import { HapticsService } from '../../services/haptics';
import { ApiService } from '../../services/api';

export const CameraAssistantScreen: React.FC = () => {
  const { twin, speakIfEnabled } = useTwin();
  const isHC = twin.visual.highContrast;
  const isHindi = twin.language === 'Hindi';

  // Camera & Stream Refs
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // States
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [cameraState, setCameraState] = useState<'initializing' | 'active' | 'paused' | 'permission_denied' | 'unavailable' | 'error'>('initializing');
  const [cameraErrorMsg, setCameraErrorMsg] = useState<string>('');
  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('environment');

  // Mode & Query
  const [selectedMode, setSelectedMode] = useState<string>('AUTO');
  const [targetObject, setTargetObject] = useState<string>('');

  // AI Detections & Results (Real Backend Data)
  const [detectedObjects, setDetectedObjects] = useState<any[]>([]);
  const [recognizedText, setRecognizedText] = useState<string>('');
  const [guidancePrompt, setGuidancePrompt] = useState<string>(
    isHindi
      ? 'वास्तविक समय कैमरा चालू है। विश्लेषण करने के लिए "स्कैन करें" बटन दबाएं।'
      : 'Real camera ready. Press "Analyze Frame" to analyze vision with AI.'
  );
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [autoScan, setAutoScan] = useState<boolean>(false);

  // Initialize Camera
  const startCamera = useCallback(async (facing: 'environment' | 'user' = facingMode) => {
    setCameraState('initializing');
    setCameraErrorMsg('');
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setCameraState('unavailable');
        setCameraErrorMsg(
          isHindi
            ? 'आपका ब्राउज़र या डिवाइस कैमरा एक्सेस का समर्थन नहीं करता है।'
            : 'Your browser or environment does not support camera access.'
        );
        return;
      }

      // Stop existing stream if any
      if (videoRef.current && videoRef.current.srcObject) {
        const currentStream = videoRef.current.srcObject as MediaStream;
        currentStream.getTracks().forEach(track => track.stop());
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: facing,
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play().catch(() => {});
      }

      setIsStreaming(true);
      setCameraState('active');
      setCameraErrorMsg('');
    } catch (err: any) {
      console.error('Camera initialization error:', err);
      setIsStreaming(false);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setCameraState('permission_denied');
        setCameraErrorMsg(
          isHindi
            ? 'कैमरा अनुमति अस्वीकृत की गई। कृपया ब्राउज़र सेटिंग्स में कैमरा की अनुमति दें।'
            : 'Camera permission was denied. Please allow camera access in browser settings.'
        );
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setCameraState('unavailable');
        setCameraErrorMsg(
          isHindi
            ? 'कोई कैमरा उपकरण नहीं मिला।'
            : 'No camera hardware device found on this system.'
        );
      } else {
        setCameraState('error');
        setCameraErrorMsg(
          err.message || (isHindi ? 'कैमरा प्रारंभ करने में त्रुटि' : 'Failed to start camera feed')
        );
      }
    }
  }, [facingMode, isHindi]);

  const stopCamera = useCallback(() => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
    setCameraState('paused');
  }, []);

  // Effect: Start camera on mount, cleanup on unmount
  useEffect(() => {
    startCamera('environment');
    speakIfEnabled(guidancePrompt);

    return () => {
      stopCamera();
    };
  }, []);

  // Switch Rear / Front Camera
  const toggleFacingMode = () => {
    HapticsService.tactileClick();
    const nextFacing = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(nextFacing);
    startCamera(nextFacing);
  };

  // Toggle Stream Play / Pause
  const toggleStream = () => {
    HapticsService.tactileClick();
    if (isStreaming) {
      stopCamera();
    } else {
      startCamera(facingMode);
    }
  };

  // Execute Real Frame Capture & Backend API Call
  const handleAnalyzeFrame = async () => {
    if (isAnalyzing) return;
    HapticsService.confirmationPulse();
    setAnalysisError(null);

    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || cameraState !== 'active' || video.videoWidth === 0) {
      const msg = isHindi
        ? 'कैमरा फ़ीड तैयार नहीं है। कृपया लाइव स्ट्रीम सक्रिय होने की प्रतीक्षा करें।'
        : 'Camera feed is not ready. Please ensure live stream is active.';
      setAnalysisError(msg);
      speakIfEnabled(msg);
      return;
    }

    if (!canvas) return;

    setIsAnalyzing(true);

    try {
      // Capture frame onto canvas
      canvas.width = video.videoWidth || 1280;
      canvas.height = video.videoHeight || 720;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      }

      // Convert canvas snapshot to JPEG Blob
      canvas.toBlob(async (blob) => {
        if (!blob) {
          setIsAnalyzing(false);
          const err = isHindi ? 'फ़्रेम स्नैपशॉट बनाने में विफल' : 'Failed to capture image snapshot';
          setAnalysisError(err);
          speakIfEnabled(err);
          return;
        }

        try {
          // Send real frame to backend endpoint
          const result = await ApiService.analyzeCameraFrame(blob, {
            mode: selectedMode,
            twin_id: twin.id,
            language: isHindi ? 'hindi' : 'english',
            intent: targetObject ? `FIND_${targetObject}` : undefined,
            target_object: targetObject || undefined,
          });

          if (result && result.success) {
            const analysisData = result.analysis || {};
            const assistanceData = result.assistance || {};

            // Extract real objects
            const objs = (analysisData.objects || []).map((o: any) => ({
              label: o.label || 'Detected Object',
              confidence: o.confidence || 0.90,
              clock_position: o.clock_direction || "12 o'clock",
              proximity: o.proximity || 'near',
              elevation: o.elevation || 'level',
              relative_direction: o.relative_direction || 'straight ahead',
              haptic_cue: o.haptic_cue || 'DOUBLE_PULSE_CENTER',
            }));
            setDetectedObjects(objs);

            // Extract real OCR texts
            const textElems = (analysisData.text_elements || []).map((t: any) => t.text);
            setRecognizedText(textElems.join('\n'));

            // Extract AI response prompt
            const prompt =
              assistanceData.spoken_response ||
              assistanceData.display_response ||
              (isHindi ? 'कैमरा दृश्य का सफलतापूर्वक विश्लेषण किया गया।' : 'Frame analyzed successfully.');

            setGuidancePrompt(prompt);
            speakIfEnabled(prompt);

            // Trigger haptic feedback if configured
            if (assistanceData.haptic_cue) {
              HapticsService.successDoublePulse();
            }

            const latency = result.processing?.latency_ms || analysisData.processing_metadata?.latency_ms || null;
            setLatencyMs(latency);
          } else {
            const errMsg = result?.error?.message || (isHindi ? 'विश्लेषण विफल रहा' : 'Analysis request failed');
            setAnalysisError(errMsg);
            speakIfEnabled(errMsg);
          }
        } catch (err: any) {
          console.error('Backend camera analysis failure:', err);
          const errMsg = err.message || (isHindi ? 'बैकएंड सर्वर से जुड़ने में असमर्थ' : 'Unable to connect to Sahayak AI backend');
          setAnalysisError(errMsg);
          speakIfEnabled(isHindi ? 'बैकएंड कनेक्शन त्रुटि' : 'Backend connection error');
        } finally {
          setIsAnalyzing(false);
        }
      }, 'image/jpeg', 0.85);

    } catch (err: any) {
      console.error('Frame capture exception:', err);
      setIsAnalyzing(false);
      setAnalysisError(err.message || 'Frame capture exception');
    }
  };

  // Auto-scan request locking to prevent overlapping API requests
  const isAnalyzingRef = useRef<boolean>(false);
  useEffect(() => {
    isAnalyzingRef.current = isAnalyzing;
  }, [isAnalyzing]);

  // Auto-scan timer effect
  useEffect(() => {
    let timer: any = null;
    if (autoScan && isStreaming && cameraState === 'active') {
      timer = setInterval(() => {
        if (!isAnalyzingRef.current) {
          handleAnalyzeFrame();
        }
      }, 4500);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [autoScan, isStreaming, cameraState]);

  return (
    <div className={`flex flex-col h-full ${isHC ? 'bg-black text-[#FFD700]' : 'bg-slate-50 text-slate-800'}`}>
      {/* Hidden Snapshot Canvas */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Header */}
      <div className={`p-4 border-b ${isHC ? 'border-[#FFD700] bg-neutral-900' : 'border-slate-200 bg-white shadow-sm'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Camera className={isHC ? 'text-[#FFD700]' : 'text-blue-600'} size={24} />
            <div>
              <h1 className="text-xl font-bold tracking-tight leading-none">
                {isHindi ? 'कैमरा असिस्टेंट HUD' : 'Camera Assistant HUD'}
              </h1>
              <p className="text-[11px] opacity-75 mt-0.5 font-medium">
                {isHindi ? 'वास्तविक समय एआई दृष्टि एवं स्थानिक मार्गदर्शन' : 'Real-time AI Vision & Spatial Guidance'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={toggleFacingMode}
              title="Switch Front/Rear Camera"
              className={`p-2 rounded-xl border transition-all ${
                isHC
                  ? 'border-[#FFD700] text-[#FFD700] hover:bg-neutral-800'
                  : 'border-slate-200 bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              <SwitchCamera size={18} />
            </button>
            <span className={`px-2.5 py-1 text-xs font-bold rounded-full ${
              cameraState === 'active'
                ? isHC ? 'bg-[#FFD700] text-black' : 'bg-emerald-100 text-emerald-700 border border-emerald-300'
                : 'bg-red-100 text-red-700 border border-red-300'
            }`}>
              {cameraState === 'active' ? (isHindi ? 'लाइव' : 'LIVE') : (isHindi ? 'रोका हुआ' : 'PAUSED')}
            </span>
          </div>
        </div>

        {/* Vision Mode Selector */}
        <div className="flex items-center gap-1.5 mt-3 overflow-x-auto pb-1">
          {['AUTO', 'SEE', 'READ', 'FIND', 'UNDERSTAND', 'NAVIGATE'].map((m) => (
            <button
              key={m}
              onClick={() => {
                HapticsService.tactileClick();
                setSelectedMode(m);
              }}
              className={`px-3 py-1 rounded-lg text-xs font-bold tracking-wider transition-all whitespace-nowrap border ${
                selectedMode === m
                  ? isHC
                    ? 'bg-[#FFD700] text-black border-[#FFD700]'
                    : 'bg-blue-600 text-white border-blue-600 shadow-sm'
                  : isHC
                    ? 'border-[#FFD700] text-[#FFD700] bg-neutral-900'
                    : 'border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100'
              }`}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      {/* Main Vision Viewport */}
      <div className="relative flex-1 bg-black flex items-center justify-center overflow-hidden min-h-[280px]">
        {/* Real HTML Video Stream */}
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className={`w-full h-full object-cover transition-opacity duration-300 ${
            cameraState === 'active' ? 'opacity-100' : 'opacity-20'
          }`}
        />

        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30 pointer-events-none z-10" />

        {/* Camera Permission / Error Overlay */}
        {cameraState !== 'active' && (
          <div className="absolute inset-0 z-40 bg-neutral-950/95 flex flex-col items-center justify-center p-6 text-center">
            {cameraState === 'permission_denied' || cameraState === 'unavailable' ? (
              <ShieldAlert size={48} className="text-amber-400 mb-3 animate-bounce" />
            ) : cameraState === 'initializing' ? (
              <Loader2 size={40} className="text-blue-400 mb-3 animate-spin" />
            ) : (
              <AlertTriangle size={44} className="text-red-400 mb-3" />
            )}

            <h3 className="text-lg font-bold text-white mb-1">
              {cameraState === 'permission_denied'
                ? (isHindi ? 'कैमरा अनुमति आवश्यक है' : 'Camera Permission Required')
                : cameraState === 'unavailable'
                ? (isHindi ? 'कैमरा उपलब्ध नहीं है' : 'Camera Unavailable')
                : cameraState === 'initializing'
                ? (isHindi ? 'कैमरा कनेक्ट हो रहा है...' : 'Connecting to Camera...')
                : (isHindi ? 'कैमरा स्थिति' : 'Camera Paused / Stopped')}
            </h3>

            <p className="text-sm text-neutral-300 max-w-md mb-4 leading-relaxed">
              {cameraErrorMsg || (isHindi ? 'कैमरा चालू करने के लिए "कैमरा चालू करें" पर क्लिक करें।' : 'Click below to start camera stream.')}
            </p>

            <button
              onClick={() => startCamera(facingMode)}
              className={`px-5 py-2.5 rounded-xl font-bold text-sm shadow-lg flex items-center gap-2 transition-all active:scale-95 ${
                isHC ? 'bg-[#FFD700] text-black' : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              <Camera size={18} />
              <span>{isHindi ? 'कैमरा चालू करें' : 'Start Live Camera'}</span>
            </button>
          </div>
        )}

        {/* HUD Target Reticle */}
        {cameraState === 'active' && (
          <div className="relative z-20 w-64 h-64 border-2 border-dashed border-yellow-400/90 rounded-2xl flex flex-col items-center justify-between p-4 pointer-events-none">
            <div className="text-[11px] font-mono text-yellow-300 bg-black/80 backdrop-blur-sm px-2.5 py-0.5 rounded border border-yellow-400/40">
              MODE: {selectedMode} • INTENT: REAL_TIME
            </div>

            <div className={`w-14 h-14 rounded-full border-2 border-yellow-400 flex items-center justify-center text-yellow-400 bg-black/40 backdrop-blur-sm ${
              isAnalyzing ? 'animate-ping' : ''
            }`}>
              {isAnalyzing ? <Loader2 size={24} className="animate-spin" /> : <Eye size={24} />}
            </div>

            <div className="text-[11px] font-mono text-yellow-300 bg-black/80 backdrop-blur-sm px-2.5 py-0.5 rounded border border-yellow-400/40">
              {latencyMs ? `LATENCY: ${latencyMs}ms` : 'SAHAYAK AI VISION'}
            </div>
          </div>
        )}

        {/* Overlay Controls */}
        <div className="absolute bottom-4 right-4 z-30 flex items-center gap-2">
          <button
            onClick={() => setAutoScan(!autoScan)}
            title="Toggle Continuous Auto-Scan"
            className={`px-3 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-lg border backdrop-blur-md transition-all ${
              autoScan
                ? 'bg-amber-500 text-black border-amber-400'
                : 'bg-black/70 text-white border-white/20 hover:bg-black'
            }`}
          >
            <Sparkles size={14} />
            <span>{autoScan ? (isHindi ? 'ऑटो-स्कैन ऑन' : 'AUTO-SCAN ON') : (isHindi ? 'ऑटो-स्कैन ऑफ' : 'AUTO-SCAN OFF')}</span>
          </button>

          <button
            onClick={toggleStream}
            title={isStreaming ? 'Pause Camera' : 'Start Camera'}
            className={`p-3 rounded-full shadow-xl transition-all ${
              isStreaming
                ? isHC ? 'bg-red-600 text-white' : 'bg-red-500 hover:bg-red-600 text-white'
                : isHC ? 'bg-[#FFD700] text-black' : 'bg-emerald-600 hover:bg-emerald-700 text-white'
            }`}
          >
            {isStreaming ? <Square size={18} /> : <Play size={18} />}
          </button>

          <button
            onClick={handleAnalyzeFrame}
            disabled={isAnalyzing || cameraState !== 'active'}
            className={`px-4 py-3 rounded-full font-bold text-sm shadow-xl flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50 ${
              isHC ? 'bg-[#FFD700] text-black' : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {isAnalyzing ? <Loader2 size={18} className="animate-spin" /> : <RefreshCw size={18} />}
            <span>{isAnalyzing ? (isHindi ? 'विश्लेषण...' : 'Analyzing...') : (isHindi ? 'स्कैन करें' : 'Analyze Frame')}</span>
          </button>
        </div>
      </div>

      {/* AI Guidance HUD Banner */}
      <div className={`p-3 border-y ${isHC ? 'bg-[#FFD700] text-black font-bold' : 'bg-blue-50 text-blue-900 border-blue-200'}`}>
        <div className="flex items-start justify-between gap-2 max-w-xl mx-auto">
          <div className="flex items-start gap-2">
            <Sparkles className="shrink-0 mt-0.5 text-blue-600" size={18} />
            <p className="text-sm leading-snug font-medium">{guidancePrompt}</p>
          </div>
          <button
            onClick={() => speakIfEnabled(guidancePrompt)}
            title="Read guidance aloud"
            className="p-1 text-blue-700 hover:text-blue-900 shrink-0"
          >
            <Volume2 size={16} />
          </button>
        </div>
      </div>

      {/* Analysis Error Alert Banner */}
      {analysisError && (
        <div className="p-3 bg-red-100 border-b border-red-300 text-red-800 text-xs font-semibold flex items-center gap-2">
          <AlertTriangle size={16} className="shrink-0 text-red-600" />
          <p className="flex-1">{analysisError}</p>
        </div>
      )}

      {/* Real Detection & OCR Result Cards */}
      <div className="p-4 flex-1 overflow-y-auto space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-wider opacity-80">
            {isHindi ? 'वास्तविक एआई परिणाम' : 'Real AI Camera Detections'}
          </h2>
          {latencyMs && (
            <span className="text-[10px] font-mono opacity-70">
              {latencyMs}ms processed
            </span>
          )}
        </div>

        {/* Target Object Search Input (Optional FIND Mode) */}
        {selectedMode === 'FIND' && (
          <div className="flex gap-2">
            <input
              type="text"
              value={targetObject}
              onChange={(e) => setTargetObject(e.target.value)}
              placeholder={isHindi ? 'खोजने के लिए वस्तु दर्ज करें (उदा. bottle, keys)' : 'Enter object to find (e.g. bottle, keys)'}
              className={`flex-1 px-3 py-1.5 text-xs rounded-xl border ${
                isHC ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]' : 'bg-white border-slate-300 text-slate-800'
              }`}
            />
          </div>
        )}

        {/* Objects List */}
        {detectedObjects.length > 0 ? (
          detectedObjects.map((obj, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-xl border flex justify-between items-center transition-all ${
                isHC ? 'border-[#FFD700] bg-neutral-900' : 'border-slate-200 bg-white shadow-sm hover:shadow'
              }`}
            >
              <div>
                <div className="font-bold text-sm flex items-center gap-1.5">
                  <CheckCircle2 size={15} className="text-emerald-500" />
                  <span>{obj.label}</span>
                </div>
                <div className="text-xs opacity-75 mt-0.5 font-medium">
                  {obj.clock_position} • {obj.relative_direction || obj.proximity} • {obj.elevation}
                </div>
              </div>
              <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                isHC ? 'bg-[#FFD700] text-black' : 'bg-blue-100 text-blue-800'
              }`}>
                {Math.round(obj.confidence * 100)}% Match
              </span>
            </div>
          ))
        ) : (
          !isAnalyzing && (
            <div className={`p-4 text-center rounded-xl border border-dashed text-xs ${
              isHC ? 'border-neutral-700 text-neutral-400' : 'border-slate-300 text-slate-500'
            }`}>
              {isHindi
                ? 'अभी तक कोई वस्तु या टेक्स्ट नहीं पहचाना गया है। विश्लेषण के लिए "स्कैन करें" दबाएं।'
                : 'No objects detected yet. Click "Analyze Frame" to scan camera view.'}
            </div>
          )
        )}

        {/* Recognized OCR Text */}
        {recognizedText && (
          <div className={`p-3.5 rounded-xl border ${
            isHC ? 'border-[#FFD700] bg-neutral-900' : 'border-slate-200 bg-white shadow-sm'
          }`}>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600">
                {isHindi ? 'पहचाना गया टेक्स्ट (OCR Readout)' : 'Real Recognized OCR Text'}
              </span>
              <button
                onClick={() => speakIfEnabled(recognizedText)}
                className="text-xs text-blue-600 font-semibold hover:underline"
              >
                {isHindi ? 'पढ़ें' : 'Read Aloud'}
              </button>
            </div>
            <p className="text-sm font-medium leading-relaxed whitespace-pre-wrap">{recognizedText}</p>
          </div>
        )}
      </div>
    </div>
  );
};
