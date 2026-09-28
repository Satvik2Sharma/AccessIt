import React, { useState, useEffect } from 'react';
import { useTwin } from '../../context/TwinContext';
import { HapticsService } from '../../services/haptics';
import { ApiService } from '../../services/api';
import { 
  ArrowLeft, Volume2, 
  MapPin, Crosshair 
} from 'lucide-react';

export const SeeScreen: React.FC = () => {
  const { twin, setActiveScreen, speakIfEnabled } = useTwin();
  const [selectedObject, setSelectedObject] = useState<string>('bottle');
  const [guidance, setGuidance] = useState<string>('Locating object...');
  const [direction, setDirection] = useState<string>('slightly to your right');
  const [distance, setDistance] = useState<string>('near (~45 cm, arm reach)');
  const [hapticCue, setHapticCue] = useState<string>('PULSE_RIGHT');

  const isHC = twin.visual.highContrast;
  const isHindi = twin.language === 'Hindi';

  const objects = [
    { id: 'bottle', labelHi: 'बोतल', labelEn: 'Bottle' },
    { id: 'keys', labelHi: 'चाबियां', labelEn: 'Keys' },
    { id: 'phone', labelHi: 'मोबाइल', labelEn: 'Phone' },
    { id: 'document', labelHi: 'दस्तावेज़', labelEn: 'Doc' },
  ];

  useEffect(() => {
    locateObject(selectedObject);
  }, [selectedObject, twin.language]);

  const locateObject = async (objName: string) => {
    HapticsService.tactileClick();
    setSelectedObject(objName);

    const res = await ApiService.findObject(objName, twin);
    setGuidance(res.displayGuidance);
    setDirection(res.direction);
    setDistance(res.distanceEstimate);
    setHapticCue(res.hapticCue);

    HapticsService.directionalBuzz(res.hapticCue);
    speakIfEnabled(res.spokenGuidance);
  };

  return (
    <div className="flex-1 p-4 flex flex-col justify-between space-y-3">
      <div className="space-y-3">
        {/* Top Bar */}
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
            isHC ? 'bg-[#FFD700] text-black' : 'bg-amber-100 text-amber-900'
          }`}>
            SPATIAL VISION COPILOT
          </span>
        </div>

        {/* Spatial Camera Viewport */}
        <div className="relative w-full h-64 bg-black rounded-3xl overflow-hidden shadow-lg border border-slate-700 flex items-center justify-center">
          {/* Simulated desk scene with grid lines */}
          <div className="absolute inset-0 bg-gradient-to-b from-neutral-900 via-neutral-950 to-black opacity-90 flex items-center justify-center">
            <Crosshair size={48} className="text-white/20 animate-spin-slow" />
          </div>

          {/* Dynamic Bounding Box matching selected object */}
          <div
            className={`absolute transition-all duration-500 rounded-xl border-2 flex flex-col justify-between p-1.5 ${
              selectedObject === 'bottle'
                ? 'right-6 top-10 w-28 h-44 border-emerald-400 bg-emerald-500/10'
                : selectedObject === 'keys'
                  ? 'left-6 top-16 w-28 h-28 border-amber-400 bg-amber-500/10'
                  : selectedObject === 'phone'
                    ? 'inset-x-24 top-14 h-36 border-blue-400 bg-blue-500/10'
                    : 'inset-x-16 top-12 h-40 border-purple-400 bg-purple-500/10'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-black/80 text-white font-mono">
                {selectedObject}
              </span>
              <span className="text-[9px] font-mono text-emerald-300 bg-black/80 px-1 rounded">
                94%
              </span>
            </div>
            <div className="text-[10px] font-bold text-center text-white bg-black/70 rounded py-0.5">
              {direction}
            </div>
          </div>

          {/* Directional Spatial Arrow Overlay */}
          <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/80 backdrop-blur-md border border-white/20 text-white text-xs font-bold">
            <MapPin size={14} className="text-amber-400" />
            <span>{distance}</span>
          </div>
        </div>

        {/* Directional Audio & Guidance Card */}
        <div className={`p-4 rounded-2xl border-2 space-y-2 ${
          isHC ? 'bg-black border-[#FFD700] text-[#FFD700]' : 'bg-white border-amber-500/50 shadow-md'
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-black uppercase tracking-wider text-amber-600">
              {isHindi ? 'स्थानिक दिशा निर्देश (Spatial Cue)' : 'Spatial Guidance Cue'}
            </span>
            <button
              onClick={() => {
                HapticsService.tactileClick();
                speakIfEnabled(guidance);
              }}
              className={`p-1.5 rounded-lg ${
                isHC ? 'bg-[#FFD700] text-black' : 'bg-amber-50 text-amber-700 hover:bg-amber-100'
              }`}
            >
              <Volume2 size={16} />
            </button>
          </div>

          <h3 className={`font-black text-base leading-snug ${isHC ? 'text-[#FFD700]' : 'text-slate-900'}`}>
            {guidance}
          </h3>

          <div className={`p-2.5 rounded-xl text-xs flex items-center justify-between ${
            isHC ? 'bg-neutral-900 text-white border border-[#FFD700]' : 'bg-amber-50 text-amber-900'
          }`}>
            <span>{isHindi ? 'हैप्टिक कंपन संकेत:' : 'Tactile Haptic Cue:'}</span>
            <span className="font-mono font-bold text-xs uppercase px-2 py-0.5 rounded bg-black text-amber-400">
              {hapticCue}
            </span>
          </div>
        </div>
      </div>

      {/* Target Object Selector */}
      <div className="space-y-2 pt-2">
        <span className={`text-[11px] font-bold uppercase tracking-wider block ${
          isHC ? 'text-[#FFD700]' : 'text-slate-600'
        }`}>
          {isHindi ? 'ढूंढने के लिए वस्तु चुनें:' : 'Select Target Object:'}
        </span>
        <div className="grid grid-cols-4 gap-2">
          {objects.map(obj => (
            <button
              key={obj.id}
              onClick={() => locateObject(obj.id)}
              className={`py-2.5 px-1 rounded-xl text-center font-bold text-xs transition-all active:scale-90 border ${
                selectedObject === obj.id
                  ? isHC
                    ? 'bg-[#FFD700] text-black border-black ring-2 ring-[#FFD700]'
                    : 'bg-amber-600 text-white border-amber-600 shadow-md'
                  : isHC
                    ? 'border-[#FFD700] text-[#FFD700] hover:bg-neutral-900'
                    : 'bg-white border-slate-200 text-slate-700 hover:bg-amber-50'
              }`}
            >
              <div className="text-[12px] font-black">{obj.labelEn}</div>
              <div className="text-[10px] opacity-80">{obj.labelHi}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
