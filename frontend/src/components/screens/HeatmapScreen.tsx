import React, { useState, useEffect } from 'react';
import { useTwin } from '../../context/TwinContext';
import { HapticsService } from '../../services/haptics';
import { ApiService } from '../../services/api';
import type { HeatmapItem, Recommendation } from '../../types';
import { 
  ArrowLeft, BarChart2, Sparkles, ThumbsUp, ShieldCheck 
} from 'lucide-react';

export const HeatmapScreen: React.FC = () => {
  const { twin, setActiveScreen, updateTwin } = useTwin();
  const [heatmap, setHeatmap] = useState<HeatmapItem[]>([]);
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [consented, setConsented] = useState<boolean>(false);

  const isHC = twin.visual.highContrast;
  const isHindi = twin.language === 'Hindi';

  useEffect(() => {
    ApiService.getHeatmap().then(res => {
      setHeatmap(res.heatmap);
      setRecommendation(res.recommendation);
    });
  }, []);

  const handleApplyAdaptation = () => {
    HapticsService.successDoublePulse();
    setConsented(true);
    updateTwin({
      ...twin,
      comprehension: {
        ...twin.comprehension,
        simplifiedLanguage: true,
        oneStepAtATime: true,
      },
      motor: {
        ...twin.motor,
        voiceInput: true,
      },
    });
  };

  return (
    <div className="flex-1 p-4 flex flex-col justify-between space-y-4">
      <div className="space-y-3.5">
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
            isHC ? 'bg-[#FFD700] text-black' : 'bg-purple-100 text-purple-700'
          }`}>
            STAGE 7: ACCESSIBILITY LEARNING
          </span>
        </div>

        {/* Telemetry Stats Card */}
        {recommendation && (
          <div className={`p-4 rounded-2xl border space-y-2.5 ${
            isHC ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]' : 'bg-white border-slate-200 shadow-sm'
          }`}>
            <div className="flex items-center gap-2">
              <BarChart2 size={18} className={isHC ? 'text-[#FFD700]' : 'text-blue-600'} />
              <h3 className="text-xs font-black uppercase tracking-wider">
                {isHindi ? 'स्थानीय इंटरैक्शन अंतर्दृष्टि' : 'Local Interaction Telemetry'}
              </h3>
            </div>

            <div className="grid grid-cols-2 gap-2 pt-1">
              <div className={`p-2.5 rounded-xl ${
                isHC ? 'bg-black border border-[#FFD700]' : 'bg-slate-50'
              }`}>
                <span className="text-[10px] text-slate-500 block">Total Tasks Completed</span>
                <span className="text-lg font-black">{recommendation.tasks_completed_count} Tasks</span>
              </div>
              <div className={`p-2.5 rounded-xl ${
                isHC ? 'bg-black border border-[#FFD700]' : 'bg-slate-50'
              }`}>
                <span className="text-[10px] text-slate-500 block">Voice Preference Rate</span>
                <span className="text-lg font-black text-emerald-600">{recommendation.voice_usage_percentage}%</span>
              </div>
            </div>
          </div>
        )}

        {/* Interaction Complexity Heatmap List */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className={`text-xs font-black uppercase tracking-wider ${
              isHC ? 'text-[#FFD700]' : 'text-slate-800'
            }`}>
              {isHindi ? 'इंटरैक्शन घर्षण हीटमैप' : 'Interaction Friction Heatmap'}
            </h3>
            <span className="text-[10px] text-slate-500">Live Session Metrics</span>
          </div>

          <div className="space-y-2">
            {heatmap.map((item, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-2xl border flex items-start gap-3 transition-all ${
                  isHC
                    ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]'
                    : 'bg-white border-slate-200 shadow-sm'
                }`}
              >
                {/* Friction Color Dot */}
                <div className={`w-3.5 h-3.5 rounded-full shrink-0 mt-0.5 ${
                  item.color === 'RED'
                    ? 'bg-red-500 ring-4 ring-red-100'
                    : item.color === 'YELLOW'
                      ? 'bg-amber-400 ring-4 ring-amber-100'
                      : 'bg-emerald-500 ring-4 ring-emerald-100'
                }`} />

                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs">{item.interaction_point}</span>
                    <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${
                      item.color === 'RED'
                        ? 'bg-red-100 text-red-700'
                        : item.color === 'YELLOW'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-emerald-100 text-emerald-700'
                    }`}>
                      {item.complexity}
                    </span>
                  </div>
                  <p className={`text-[11px] mt-0.5 leading-snug ${isHC ? 'text-white' : 'text-slate-500'}`}>
                    {item.reason}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Consented Proactive Adaptation Prompt */}
        {recommendation?.dialog_prompt && (
          <div className={`p-4 rounded-2xl border-2 space-y-3 ${
            consented
              ? isHC
                ? 'bg-black border-[#FFD700] text-[#FFD700]'
                : 'bg-emerald-50 border-emerald-300 text-emerald-900'
              : isHC
                ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]'
                : 'bg-purple-50/90 border-purple-200 text-purple-900'
          }`}>
            <div className="flex items-start gap-2.5">
              <Sparkles size={20} className={consented ? 'text-emerald-600' : 'text-purple-600'} />
              <div>
                <span className="text-xs font-black block">
                  {consented
                    ? (isHindi ? 'सहमति स्वीकृत: प्रोफ़ाइल अनुकूलित' : 'Consented & Profile Adapted!')
                    : (isHindi ? 'सक्रिय सुलभता अनुकूलन (Proactive Recommendation)' : 'Proactive Adaptation Proposal')}
                </span>
                <p className={`text-xs mt-1 leading-snug ${isHC ? 'text-white' : 'text-slate-700'}`}>
                  {consented
                    ? (isHindi
                        ? 'सहायक ने आपकी प्राथमिकताओं के आधार पर स्वतः आवाज़ इनपुट और सरल भाषा को सक्रिय कर दिया है।'
                        : 'Voice-first interaction and simplified language are now automatically applied to your Accessibility Twin.')
                    : recommendation.dialog_prompt}
                </p>
              </div>
            </div>

            {!consented && (
              <div className="flex items-center gap-2 pt-1">
                <button
                  onClick={handleApplyAdaptation}
                  className={`flex-1 py-2 px-3 rounded-xl font-bold text-xs flex items-center justify-center gap-1.5 transition-all active:scale-95 shadow-sm ${
                    isHC
                      ? 'bg-[#FFD700] text-black font-extrabold hover:bg-yellow-400'
                      : 'bg-purple-600 text-white hover:bg-purple-700'
                  }`}
                >
                  <ThumbsUp size={14} />
                  <span>{isHindi ? 'हाँ, हमेशा लागू करें' : 'Accept & Auto-Adapt'}</span>
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      <div className={`p-3 rounded-xl text-[11px] flex items-center gap-2 border ${
        isHC ? 'bg-black text-[#FFD700] border-[#FFD700]' : 'bg-slate-50 text-slate-600 border-slate-200'
      }`}>
        <ShieldCheck size={18} className="shrink-0 text-emerald-600" />
        <span>
          {isHindi
            ? 'गोपनीयता सुरक्षा: यह हीटमैप केवल स्थानीय सत्र में रहता है। कोई चिकित्सा लेबल नहीं लगाया जाता।'
            : 'Ethical guarantee: Telemetry is strictly local. No medical diagnosis or clinical labeling.'}
        </span>
      </div>
    </div>
  );
};
