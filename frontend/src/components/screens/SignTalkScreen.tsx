import React, { useState, useRef, useEffect } from 'react';
import { useTwin } from '../../context/TwinContext';
import { HapticsService } from '../../services/haptics';
import { ApiService } from '../../services/api';
import { 
  ArrowLeft, Video, VideoOff, Volume2 
} from 'lucide-react';

export const SignTalkScreen: React.FC = () => {
  const { twin, setActiveScreen, speakIfEnabled } = useTwin();
  const [detectedSign, setDetectedSign] = useState<string>('HELP');
  const [caption, setCaption] = useState<string>('सहायता चाहिए (I need Help)');
  const [confidence, setConfidence] = useState<number>(0.96);
  const [isTranslating, setIsTranslating] = useState<boolean>(false);
  const [webcamEnabled, setWebcamEnabled] = useState<boolean>(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const isHC = twin.visual.highContrast;
  const isHindi = twin.language === 'Hindi';

  const gestureOptions = [
    { id: 'HELP', labelHi: 'सहायता', labelEn: 'HELP', color: 'bg-red-500' },
    { id: 'THANK_YOU', labelHi: 'धन्यवाद', labelEn: 'THANK YOU', color: 'bg-emerald-500' },
    { id: 'WATER', labelHi: 'पानी', labelEn: 'WATER', color: 'bg-blue-500' },
    { id: 'YES', labelHi: 'हाँ', labelEn: 'YES', color: 'bg-indigo-500' },
    { id: 'NO', labelHi: 'नहीं', labelEn: 'NO', color: 'bg-amber-500' },
  ];

  const handlePredictGesture = async (gestureId: string) => {
    HapticsService.tactileClick();
    setIsTranslating(true);

    const res = await ApiService.predictSign(gestureId, twin);
    setDetectedSign(res.sign);
    setCaption(res.caption);
    setConfidence(res.confidence);
    setIsTranslating(false);

    HapticsService.successDoublePulse();
    speakIfEnabled(res.spokenText);
  };

  const toggleWebcam = async () => {
    if (webcamEnabled) {
      if (videoRef.current && videoRef.current.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach(track => track.stop());
        videoRef.current.srcObject = null;
      }
      setWebcamEnabled(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        setWebcamEnabled(true);
      } catch (err) {
        console.warn('Camera access denied, fallback to simulated feed:', err);
      }
    }
  };

  useEffect(() => {
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="flex-1 p-4 flex flex-col justify-between space-y-3">
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => {
              HapticsService.tactileClick();
              setActiveScreen('home');
            }}
            className={`p-2 rounded-xl flex items-center gap-1 text-xs font-bold transition-all ${
              isHC ? 'text-[#FFD700] hover:bg-neutral-800' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <ArrowLeft size={16} />
            <span>{isHindi ? 'वापस' : 'Back'}</span>
          </button>
          <span className={`text-[11px] font-black uppercase tracking-wider px-2.5 py-1 rounded-full ${
            isHC ? 'bg-[#FFD700] text-black' : 'bg-emerald-100 text-emerald-800'
          }`}>
            DEMO 3: ISL INTERPRETER
          </span>
        </div>

        {/* Camera Viewport Simulation / Real Webcam */}
        <div className="relative w-full h-64 bg-black rounded-3xl overflow-hidden shadow-lg border border-slate-700 flex items-center justify-center">
          {webcamEnabled ? (
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center relative bg-gradient-to-b from-neutral-900 to-black">
              {/* MediaPipe 21 Hand Landmark Skeleton Simulation */}
              <svg className="w-48 h-48 opacity-80" viewBox="0 0 200 200">
                {/* Palm and Finger Bones */}
                <circle cx="100" cy="170" r="4" fill="#10B981" />
                <line x1="100" y1="170" x2="60" y2="120" stroke="#10B981" strokeWidth="2" />
                <line x1="100" y1="170" x2="85" y2="90" stroke="#10B981" strokeWidth="2" />
                <line x1="100" y1="170" x2="115" y2="85" stroke="#10B981" strokeWidth="2" />
                <line x1="100" y1="170" x2="140" y2="95" stroke="#10B981" strokeWidth="2" />
                <line x1="100" y1="170" x2="160" y2="125" stroke="#10B981" strokeWidth="2" />

                {/* Finger Joints */}
                {[
                  [60, 120], [45, 95], [35, 75],
                  [85, 90], [80, 60], [75, 35],
                  [115, 85], [115, 55], [115, 30],
                  [140, 95], [145, 68], [150, 45],
                  [160, 125], [170, 105], [175, 85],
                ].map(([cx, cy], idx) => (
                  <circle key={idx} cx={cx} cy={cy} r="3" fill="#34D399" />
                ))}
              </svg>

              <span className="text-xs text-neutral-400 font-mono mt-1">
                MediaPipe 3D Real-Time Landmarks
              </span>
            </div>
          )}

          {/* Top Camera Overlay Badges */}
          <div className="absolute top-3 left-3 flex items-center gap-2">
            <div className="px-2.5 py-1 rounded-full bg-black/80 backdrop-blur-sm border border-emerald-500/80 flex items-center gap-1.5 text-[10px] font-bold text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              <span>MEDIAPIPE 3D ACTIVE</span>
            </div>
          </div>

          <div className="absolute top-3 right-3">
            <button
              onClick={toggleWebcam}
              className="p-2 rounded-full bg-black/70 hover:bg-black text-white border border-white/20 transition-all"
              title={webcamEnabled ? 'Switch to landmark simulation' : 'Use live webcam'}
            >
              {webcamEnabled ? <VideoOff size={16} /> : <Video size={16} />}
            </button>
          </div>

          {/* Dynamic Gesture Tracking Box */}
          <div className="absolute inset-x-8 inset-y-6 border-2 border-emerald-500/40 rounded-2xl pointer-events-none flex items-end justify-between p-2">
            <span className="text-[10px] font-mono text-emerald-400 bg-black/70 px-1.5 py-0.5 rounded">
              Conf: {(confidence * 100).toFixed(1)}%
            </span>
            <span className="text-[10px] font-mono text-emerald-400 bg-black/70 px-1.5 py-0.5 rounded">
              FPS: 30
            </span>
          </div>
        </div>

        {/* Translation Output Caption Box */}
        <div className={`p-4 rounded-2xl border-2 transition-all ${
          isHC ? 'bg-black border-[#FFD700] text-[#FFD700]' : 'bg-white border-emerald-500/60 shadow-md'
        }`}>
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] font-black uppercase tracking-wider text-emerald-600">
              {isHindi ? 'पहचाना गया इशारा (Detected Sign)' : 'Detected Sign Gesture'}
            </span>
            <button
              onClick={() => {
                HapticsService.tactileClick();
                speakIfEnabled(caption);
              }}
              title="Speak sign aloud"
              className={`p-1.5 rounded-lg ${
                isHC ? 'bg-[#FFD700] text-black' : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
              }`}
            >
              <Volume2 size={16} />
            </button>
          </div>

          <div className={`font-black tracking-tight leading-tight ${
            twin.visual.largeText ? 'text-2xl' : 'text-xl'
          } ${isHC ? 'text-[#FFD700]' : 'text-slate-900'}`}>
            {isTranslating ? (isHindi ? 'विश्लेषण जारी...' : 'Interpreting...') : caption}
          </div>

          <p className={`text-xs mt-1.5 font-medium ${isHC ? 'text-white' : 'text-slate-500'}`}>
            {isHindi
              ? 'हाथ की 21 निर्देशांक गतियों को वास्तविक समय में आवाज़ और कैप्शन में अनुवादित किया गया।'
              : '21 hand coordinates mapped in 3D space to spoken speech and tactile feedback.'}
          </p>
        </div>
      </div>

      {/* Interactive Gestures Simulator Bar */}
      <div className="space-y-2 pt-2">
        <span className={`text-[11px] font-bold uppercase tracking-wider block ${
          isHC ? 'text-[#FFD700]' : 'text-slate-600'
        }`}>
          {isHindi ? 'इशारा चुनें (Test Gestures):' : 'Select Gesture to Interpret:'}
        </span>
        <div className="grid grid-cols-5 gap-1.5">
          {gestureOptions.map(g => (
            <button
              key={g.id}
              onClick={() => handlePredictGesture(g.id)}
              className={`py-2 px-1 rounded-xl text-center font-bold text-xs transition-all active:scale-90 border ${
                detectedSign === g.id
                  ? isHC
                    ? 'bg-[#FFD700] text-black border-black ring-2 ring-[#FFD700]'
                    : 'bg-emerald-600 text-white border-emerald-600 shadow-md'
                  : isHC
                    ? 'border-[#FFD700] text-[#FFD700] hover:bg-neutral-900'
                    : 'bg-white border-slate-200 text-slate-700 hover:bg-emerald-50'
              }`}
            >
              <div className="text-[11px] font-black">{g.labelEn}</div>
              <div className="text-[9px] opacity-80">{g.labelHi}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
