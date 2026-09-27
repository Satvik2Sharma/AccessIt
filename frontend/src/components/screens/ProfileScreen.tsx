import React, { useState } from 'react';
import { useTwin } from '../../context/TwinContext';
import { HapticsService } from '../../services/haptics';
import type { AccessibilityTwin } from '../../types';
import { 
  ArrowLeft, ShieldCheck, Check, 
  Eye, MousePointer, BookOpen, Sparkles 
} from 'lucide-react';

export const ProfileScreen: React.FC = () => {
  const { twin, updateTwin, setActiveScreen } = useTwin();

  const [formTwin, setFormTwin] = useState<AccessibilityTwin>(twin);
  const [savedToast, setSavedToast] = useState(false);

  const isHC = twin.visual.highContrast;
  const isHindi = formTwin.language === 'Hindi';

  const handleSave = () => {
    HapticsService.successDoublePulse();
    updateTwin(formTwin);
    setSavedToast(true);
    setTimeout(() => {
      setSavedToast(false);
      setActiveScreen('home');
    }, 900);
  };

  return (
    <div className="flex-1 p-4 flex flex-col justify-between space-y-4">
      <div className="space-y-3.5">
        {/* Top Header */}
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
            isHC ? 'bg-[#FFD700] text-black' : 'bg-blue-100 text-blue-800'
          }`}>
            ACCESSIBILITY TWIN
          </span>
        </div>

        {/* Ethical Guarantee Banner */}
        <div className={`p-3 rounded-xl border flex items-start gap-2.5 ${
          isHC
            ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]'
            : 'bg-emerald-50 border-emerald-200 text-emerald-900'
        }`}>
          <ShieldCheck size={18} className="shrink-0 mt-0.5 text-emerald-600" />
          <div className="text-[11px] leading-tight">
            <span className="font-bold block">
              {isHindi ? 'नैतिक गारंटी (Ethical Guarantee):' : 'Ethical Guarantee:'}
            </span>
            <span className="opacity-90">
              {isHindi
                ? 'यह प्रोफ़ाइल बातचीत की प्राथमिकताओं का मॉडल है, कोई चिकित्सा निदान नहीं।'
                : 'Models functional interaction preferences without clinical diagnosis or pathology.'}
            </span>
          </div>
        </div>

        {/* Language Selector */}
        <div className={`p-3.5 rounded-2xl border space-y-2 ${
          isHC ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]' : 'bg-white border-slate-200 shadow-sm'
        }`}>
          <label className="text-xs font-black uppercase tracking-wider block">
            {isHindi ? 'प्राथमिक भाषा (Language)' : 'Primary Language'}
          </label>
          <div className="grid grid-cols-2 gap-2">
            {(['Hindi', 'English'] as const).map(lang => (
              <button
                key={lang}
                onClick={() => {
                  HapticsService.tactileClick();
                  setFormTwin({ ...formTwin, language: lang });
                }}
                className={`py-2 px-3 rounded-xl font-bold text-xs transition-all border ${
                  formTwin.language === lang
                    ? isHC
                      ? 'bg-[#FFD700] text-black border-black'
                      : 'bg-blue-600 text-white border-blue-600 shadow-sm'
                    : isHC
                      ? 'border-[#FFD700] text-[#FFD700]'
                      : 'border-slate-200 text-slate-700 hover:bg-slate-50'
                }`}
              >
                {lang === 'Hindi' ? 'Hindi (हिंदी)' : 'English'}
              </button>
            ))}
          </div>
        </div>

        {/* Visual Preferences */}
        <div className={`p-3.5 rounded-2xl border space-y-2.5 ${
          isHC ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]' : 'bg-white border-slate-200 shadow-sm'
        }`}>
          <div className="flex items-center gap-2">
            <Eye size={16} className={isHC ? 'text-[#FFD700]' : 'text-blue-600'} />
            <h4 className="text-xs font-black uppercase tracking-wider">
              {isHindi ? 'दृश्य प्राथमिकताएं (Visual)' : 'Visual Preferences'}
            </h4>
          </div>

          <label className="flex items-center justify-between p-2 rounded-xl cursor-pointer hover:bg-slate-50/50">
            <div>
              <span className="text-xs font-bold block">{isHindi ? 'उच्च कंट्रास्ट (WCAG AAA)' : 'High Contrast Mode'}</span>
              <span className="text-[10px] text-slate-500">Yellow on Black (WCAG AAA)</span>
            </div>
            <input
              type="checkbox"
              checked={formTwin.visual.highContrast}
              onChange={(e) => setFormTwin({
                ...formTwin,
                visual: { ...formTwin.visual, highContrast: e.target.checked }
              })}
              className="w-5 h-5 rounded accent-blue-600"
            />
          </label>

          <label className="flex items-center justify-between p-2 rounded-xl cursor-pointer hover:bg-slate-50/50">
            <div>
              <span className="text-xs font-bold block">{isHindi ? 'बड़ा फ़ॉन्ट (Large Text)' : 'Large Typography (20pt+)'}</span>
              <span className="text-[10px] text-slate-500">Expanded typography scale</span>
            </div>
            <input
              type="checkbox"
              checked={formTwin.visual.largeText}
              onChange={(e) => setFormTwin({
                ...formTwin,
                visual: { ...formTwin.visual, largeText: e.target.checked }
              })}
              className="w-5 h-5 rounded accent-blue-600"
            />
          </label>
        </div>

        {/* Motor Preferences */}
        <div className={`p-3.5 rounded-2xl border space-y-2.5 ${
          isHC ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]' : 'bg-white border-slate-200 shadow-sm'
        }`}>
          <div className="flex items-center gap-2">
            <MousePointer size={16} className={isHC ? 'text-[#FFD700]' : 'text-indigo-600'} />
            <h4 className="text-xs font-black uppercase tracking-wider">
              {isHindi ? 'गति प्राथमिकताएं (Motor)' : 'Motor Preferences'}
            </h4>
          </div>

          <label className="flex items-center justify-between p-2 rounded-xl cursor-pointer hover:bg-slate-50/50">
            <div>
              <span className="text-xs font-bold block">{isHindi ? 'आवाज़ इनपुट प्राथमिकता' : 'Voice-First Input'}</span>
              <span className="text-[10px] text-slate-500">Dictate answers instead of typing</span>
            </div>
            <input
              type="checkbox"
              checked={formTwin.motor.voiceInput}
              onChange={(e) => setFormTwin({
                ...formTwin,
                motor: { ...formTwin.motor, voiceInput: e.target.checked }
              })}
              className="w-5 h-5 rounded accent-blue-600"
            />
          </label>

          <label className="flex items-center justify-between p-2 rounded-xl cursor-pointer hover:bg-slate-50/50">
            <div>
              <span className="text-xs font-bold block">{isHindi ? 'बड़े टच बटन' : 'Large Touch Targets'}</span>
              <span className="text-[10px] text-slate-500">Expanded 48px+ touch hitboxes</span>
            </div>
            <input
              type="checkbox"
              checked={formTwin.motor.largeTouchTargets}
              onChange={(e) => setFormTwin({
                ...formTwin,
                motor: { ...formTwin.motor, largeTouchTargets: e.target.checked }
              })}
              className="w-5 h-5 rounded accent-blue-600"
            />
          </label>
        </div>

        {/* Comprehension Preferences */}
        <div className={`p-3.5 rounded-2xl border space-y-2.5 ${
          isHC ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]' : 'bg-white border-slate-200 shadow-sm'
        }`}>
          <div className="flex items-center gap-2">
            <BookOpen size={16} className={isHC ? 'text-[#FFD700]' : 'text-emerald-600'} />
            <h4 className="text-xs font-black uppercase tracking-wider">
              {isHindi ? 'बोधगम्यता (Comprehension)' : 'Comprehension & Flow'}
            </h4>
          </div>

          <label className="flex items-center justify-between p-2 rounded-xl cursor-pointer hover:bg-slate-50/50">
            <div>
              <span className="text-xs font-bold block">{isHindi ? 'एक समय में एक चरण' : 'One Step at a Time'}</span>
              <span className="text-[10px] text-slate-500">Linearize multi-field forms</span>
            </div>
            <input
              type="checkbox"
              checked={formTwin.comprehension.oneStepAtATime}
              onChange={(e) => setFormTwin({
                ...formTwin,
                comprehension: { ...formTwin.comprehension, oneStepAtATime: e.target.checked }
              })}
              className="w-5 h-5 rounded accent-blue-600"
            />
          </label>

          <label className="flex items-center justify-between p-2 rounded-xl cursor-pointer hover:bg-slate-50/50">
            <div>
              <span className="text-xs font-bold block">{isHindi ? 'सरल भाषा' : 'Simplified Language'}</span>
              <span className="text-[10px] text-slate-500">Replace bureaucratic jargon</span>
            </div>
            <input
              type="checkbox"
              checked={formTwin.comprehension.simplifiedLanguage}
              onChange={(e) => setFormTwin({
                ...formTwin,
                comprehension: { ...formTwin.comprehension, simplifiedLanguage: e.target.checked }
              })}
              className="w-5 h-5 rounded accent-blue-600"
            />
          </label>

          <label className="flex items-center justify-between p-2 rounded-xl cursor-pointer hover:bg-slate-50/50">
            <div>
              <span className="text-xs font-bold block">{isHindi ? 'निर्देश बोलकर सुनाएं' : 'Read Instructions Aloud'}</span>
              <span className="text-[10px] text-slate-500">Automatic TTS voice narration</span>
            </div>
            <input
              type="checkbox"
              checked={formTwin.comprehension.readInstructionsAloud}
              onChange={(e) => setFormTwin({
                ...formTwin,
                comprehension: { ...formTwin.comprehension, readInstructionsAloud: e.target.checked }
              })}
              className="w-5 h-5 rounded accent-blue-600"
            />
          </label>
        </div>
      </div>

      {/* Save Button */}
      <div className="pt-2">
        <button
          onClick={handleSave}
          className={`w-full py-3.5 px-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all active:scale-95 shadow-md ${
            isHC
              ? 'bg-[#FFD700] text-black font-extrabold hover:bg-yellow-400'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {savedToast ? (
            <>
              <Check size={18} />
              <span>{isHindi ? 'सुलभता प्रोफ़ाइल सहेजी गई!' : 'Preferences Saved!'}</span>
            </>
          ) : (
            <>
              <Sparkles size={18} />
              <span>{isHindi ? 'प्राथमिकताएं सहेजें' : 'Save Accessibility Twin'}</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
