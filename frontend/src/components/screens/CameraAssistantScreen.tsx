import React, { useState, useEffect } from 'react';
import { useTwin } from '../../context/TwinContext';
import { Camera, RefreshCw, Eye, Sparkles, Play, Square } from 'lucide-react';
import { HapticsService } from '../../services/haptics';

export const CameraAssistantScreen: React.FC = () => {
  const { twin, speakIfEnabled } = useTwin();
  const isHC = twin.visual.highContrast;
  const isHindi = twin.language === 'Hindi';

  const [isStreaming, setIsStreaming] = useState<boolean>(true);
  const [detectedObjects] = useState<any[]>([
    {
      label: isHindi ? 'स्कॉलरशिप फॉर्म 7F दस्तावेज' : 'Scholarship Form 7F Document',
      confidence: 0.98,
      clock_position: "12 o'clock",
      distance_meters: 0.45,
      elevation: '0° (Desk Level)'
    },
    {
      label: isHindi ? 'पानी की बोतल' : 'Water Bottle',
      confidence: 0.94,
      clock_position: "2 o'clock",
      distance_meters: 0.80,
      elevation: '+15° (Eye Level)'
    }
  ]);
  const [recognizedText] = useState<string>(
    isHindi 
      ? 'नेशनल मेरिट स्कॉलरशिप सूचना 2026 - अंतिम तिथि 30 सितंबर'
      : 'National Merit Scholarship Notification 2026 - Deadline Sept 30'
  );
  const [lightingCondition] = useState<string>('good');
  const [stabilityScore] = useState<number>(0.95);
  const [guidancePrompt, setGuidancePrompt] = useState<string>(
    isHindi
      ? 'कैमरा स्थिर रखें। स्कॉलरशिप फॉर्म 12 बजे की दिशा में केंद्रित है।'
      : 'Hold camera steady. Scholarship document centered at 12 o\'clock.'
  );

  useEffect(() => {
    speakIfEnabled(guidancePrompt);
  }, []);

  const toggleStream = () => {
    HapticsService.tactileClick();
    setIsStreaming(!isStreaming);
  };

  const handleManualAnalyze = () => {
    HapticsService.confirmationPulse();
    const prompt = isHindi
      ? 'नया फ़्रेम विश्लेषित किया गया: 2 वस्तुएं पाई गईं।'
      : 'New frame analyzed: 2 objects detected.';
    setGuidancePrompt(prompt);
    speakIfEnabled(prompt);
  };

  return (
    <div className={`flex flex-col h-full ${isHC ? 'bg-black text-[#FFD700]' : 'bg-slate-50 text-slate-800'}`}>
      {/* Header */}
      <div className={`p-4 border-b ${isHC ? 'border-[#FFD700] bg-neutral-900' : 'border-slate-200 bg-white'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Camera className={isHC ? 'text-[#FFD700]' : 'text-blue-600'} size={24} />
            <h1 className="text-xl font-bold tracking-tight">
              {isHindi ? 'कैमरा असिस्टेंट HUD' : 'Camera Assistant HUD'}
            </h1>
          </div>
          <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${
            isStreaming
              ? isHC ? 'bg-[#FFD700] text-black' : 'bg-green-100 text-green-700 border border-green-300'
              : 'bg-red-100 text-red-700 border border-red-300'
          }`}>
            {isStreaming ? (isHindi ? 'लाइव स्ट्रीम' : 'LIVE STREAM') : (isHindi ? 'रोका हुआ' : 'PAUSED')}
          </span>
        </div>
      </div>

      {/* Main Vision Viewport */}
      <div className="relative flex-1 bg-neutral-950 flex items-center justify-center overflow-hidden min-h-[260px]">
        {/* Simulated Camera Feed Backdrop */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30 pointer-events-none z-10" />

        {/* Reticle Overlay */}
        <div className="relative z-20 w-64 h-64 border-2 border-dashed border-yellow-400/80 rounded-2xl flex flex-col items-center justify-between p-4 animate-pulse">
          <div className="text-xs font-mono text-yellow-300 bg-black/70 px-2 py-0.5 rounded">
            12 O'CLOCK TARGET • LIGHT: {lightingCondition.toUpperCase()}
          </div>
          <div className="w-12 h-12 rounded-full border border-yellow-400 flex items-center justify-center text-yellow-400">
            <Eye size={20} />
          </div>
          <div className="text-xs font-mono text-yellow-300 bg-black/70 px-2 py-0.5 rounded">
            STABILITY: {Math.round(stabilityScore * 100)}%
          </div>
        </div>

        {/* Camera Controls */}
        <div className="absolute bottom-4 right-4 z-30 flex gap-2">
          <button
            onClick={toggleStream}
            className={`p-3 rounded-full shadow-lg ${
              isStreaming
                ? isHC ? 'bg-red-600 text-white' : 'bg-red-500 text-white'
                : isHC ? 'bg-[#FFD700] text-black' : 'bg-green-600 text-white'
            }`}
          >
            {isStreaming ? <Square size={20} /> : <Play size={20} />}
          </button>
          <button
            onClick={handleManualAnalyze}
            className={`p-3 rounded-full shadow-lg ${
              isHC ? 'bg-[#FFD700] text-black' : 'bg-blue-600 text-white'
            }`}
          >
            <RefreshCw size={20} />
          </button>
        </div>
      </div>

      {/* AI Guidance HUD Banner */}
      <div className={`p-3 border-y ${isHC ? 'bg-[#FFD700] text-black font-bold' : 'bg-blue-50 text-blue-900 border-blue-200'}`}>
        <div className="flex items-start gap-2 max-w-xl mx-auto">
          <Sparkles className="shrink-0 mt-0.5" size={18} />
          <p className="text-sm leading-snug">{guidancePrompt}</p>
        </div>
      </div>

      {/* Detection & OCR List */}
      <div className="p-4 flex-1 overflow-y-auto space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wider opacity-80">
          {isHindi ? 'पहचाने गए ऑब्जेक्ट और टेक्स्ट' : 'Detected Objects & Spatial OCR'}
        </h2>

        {detectedObjects.map((obj, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-xl border flex justify-between items-center ${
              isHC ? 'border-[#FFD700] bg-neutral-900' : 'border-slate-200 bg-white shadow-sm'
            }`}
          >
            <div>
              <div className="font-bold text-base">{obj.label}</div>
              <div className="text-xs opacity-75 mt-0.5">
                {obj.clock_position} • {obj.distance_meters}m • {obj.elevation}
              </div>
            </div>
            <span className={`text-xs font-bold px-2 py-1 rounded ${
              isHC ? 'bg-[#FFD700] text-black' : 'bg-blue-100 text-blue-800'
            }`}>
              {Math.round(obj.confidence * 100)}% Match
            </span>
          </div>
        ))}

        {recognizedText && (
          <div className={`p-3 rounded-xl border ${
            isHC ? 'border-[#FFD700] bg-neutral-900' : 'border-slate-200 bg-white shadow-sm'
          }`}>
            <div className="text-xs font-semibold uppercase opacity-75 mb-1">
              {isHindi ? 'पढ़ा गया लाइव टेक्स्ट' : 'Live OCR Readout'}
            </div>
            <p className="text-sm font-medium leading-relaxed">{recognizedText}</p>
          </div>
        )}
      </div>
    </div>
  );
};
