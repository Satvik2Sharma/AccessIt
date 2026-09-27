import React, { useState } from 'react';
import { useTwin } from '../../context/TwinContext';
import { HapticsService } from '../../services/haptics';
import { SpeechService } from '../../services/speech';
import { ApiService } from '../../services/api';
import { Mic, Sparkles, FileCheck, BookOpen, HandMetal, Compass, ArrowRight, Zap } from 'lucide-react';

export const HomeScreen: React.FC = () => {
  const { twin, setActiveScreen, speakIfEnabled } = useTwin();
  const [isListening, setIsListening] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState<string>('');
  const [detectedIntent, setDetectedIntent] = useState<string | null>(null);

  const isHC = twin.visual.highContrast;
  const isHindi = twin.language === 'Hindi';

  const defaultStatus = isHindi
    ? 'माइक्रोफ़ोन दबाएं या नीचे दिए गए विकल्पों में से चुनें'
    : 'Tap the microphone or choose a mode below';

  const handleVoiceCopilot = async (sampleQuery?: string) => {
    HapticsService.confirmationPulse();
    setIsListening(true);
    setDetectedIntent(null);

    const listeningText = isHindi ? 'सुन रहा हूँ... बोलिए...' : 'Listening... speak your request...';
    setVoiceStatus(listeningText);

    if (sampleQuery) {
      processQuery(sampleQuery);
      return;
    }

    if (SpeechService.isRecognitionSupported()) {
      SpeechService.startListening(
        (transcript) => {
          processQuery(transcript);
        },
        () => {
          setIsListening(false);
        },
        () => {
          // Fallback simulation if mic is blocked or fails
          simulateQuery();
        },
        twin.language
      );
    } else {
      simulateQuery();
    }
  };

  const simulateQuery = () => {
    setTimeout(() => {
      const defaultQuery = isHindi
        ? 'छात्रवृत्ति फ़ॉर्म भरने में मदद करो'
        : 'Help me fill this scholarship form';
      processQuery(defaultQuery);
    }, 1200);
  };

  const processQuery = async (query: string) => {
    setIsListening(true);
    setVoiceStatus(isHindi ? `सुना गया: "${query}"` : `Understood: "${query}"`);

    const result = await ApiService.classifyIntent(query, twin);
    setIsListening(false);
    setDetectedIntent(result.intent);

    HapticsService.successDoublePulse();

    const announce = isHindi
      ? `लक्ष्य समझा गया: ${result.summary}`
      : `Intent understood: ${result.summary}`;
    speakIfEnabled(announce);

    // Auto-advance to matching screen after short confirmation
    setTimeout(() => {
      if (result.intent === 'FORM_COMPLETION') {
        setActiveScreen('complete');
      } else if (result.intent === 'UNDERSTAND_DOCUMENT') {
        setActiveScreen('read');
      } else if (result.intent === 'COMMUNICATE') {
        setActiveScreen('talk');
      } else if (result.intent === 'SEE') {
        setActiveScreen('see');
      }
    }, 1100);
  };

  const samplePrompts = isHindi
    ? [
        { label: 'फ़ॉर्म भरें', query: 'छात्रवृत्ति फ़ॉर्म भरने में मदद करो' },
        { label: 'नोटिस समझें', query: 'इस छात्रवृत्ति नोटिस में क्या महत्वपूर्ण है?' },
        { label: 'सांकेतिक भाषा', query: 'सांकेतिक भाषा का अनुवाद करो' },
        { label: 'बोतल खोजें', query: 'मेरी पानी की बोतल कहां रखी है?' },
      ]
    : [
        { label: 'Fill Form', query: 'Help me fill this scholarship form' },
        { label: 'Notice Info', query: 'What is important in this scholarship notice?' },
        { label: 'Sign Talk', query: 'Translate sign language gestures' },
        { label: 'Find Bottle', query: 'Find my water bottle on table' },
      ];

  return (
    <div className="flex-1 p-4 space-y-4">
      {/* Accessibility Twin Active Status Card */}
      <section
        onClick={() => {
          HapticsService.tactileClick();
          setActiveScreen('profile');
        }}
        className={`p-3.5 rounded-2xl cursor-pointer transition-all border ${
          isHC
            ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]'
            : 'bg-gradient-to-r from-blue-50/90 to-indigo-50/90 border-blue-200/80 shadow-sm hover:shadow-md'
        }`}
      >
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Sparkles size={17} className={isHC ? 'text-[#FFD700]' : 'text-blue-600'} />
            <span className="text-xs font-black tracking-wider uppercase">
              {isHindi ? 'सुलभता प्रोफ़ाइल सक्रिय' : 'ACCESSIBILITY TWIN ACTIVE'}
            </span>
          </div>
          <span className={`text-[11px] font-semibold flex items-center gap-1 ${
            isHC ? 'text-[#FFD700]' : 'text-blue-600'
          }`}>
            {isHindi ? 'बदलें' : 'Edit'} <ArrowRight size={12} />
          </span>
        </div>

        {/* Feature Preference Chips */}
        <div className="flex flex-wrap gap-1.5">
          <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
            isHC ? 'bg-[#FFD700] text-black' : 'bg-blue-600 text-white'
          }`}>
            {twin.language}
          </span>
          {twin.motor.voiceInput && (
            <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
              isHC ? 'border border-[#FFD700]' : 'bg-white text-slate-700 border border-slate-200'
            }`}>
              {isHindi ? 'आवाज़ प्राथमिकता' : 'Voice First'}
            </span>
          )}
          {twin.comprehension.oneStepAtATime && (
            <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
              isHC ? 'border border-[#FFD700]' : 'bg-white text-slate-700 border border-slate-200'
            }`}>
              {isHindi ? 'एक समय में एक चरण' : '1-Step-at-a-Time'}
            </span>
          )}
          {twin.comprehension.simplifiedLanguage && (
            <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
              isHC ? 'border border-[#FFD700]' : 'bg-white text-slate-700 border border-slate-200'
            }`}>
              {isHindi ? 'सरल भाषा' : 'Simplified'}
            </span>
          )}
        </div>
      </section>

      {/* Main Intent-Aware Prompt */}
      <div className="text-center pt-2 pb-1 space-y-1">
        <h2 className={`font-black tracking-tight ${
          twin.visual.largeText ? 'text-2xl' : 'text-xl'
        } ${isHC ? 'text-[#FFD700]' : 'text-slate-900'}`}>
          {isHindi ? 'मैं आपकी क्या मदद करूँ?' : 'How can I assist you?'}
        </h2>
        <p className={`text-xs px-4 min-h-[32px] flex items-center justify-center font-medium ${
          isListening 
            ? 'text-red-500 font-bold animate-pulse' 
            : detectedIntent 
              ? isHC ? 'text-emerald-400 font-bold' : 'text-emerald-600 font-bold'
              : isHC ? 'text-white' : 'text-slate-500'
        }`}>
          {voiceStatus || defaultStatus}
        </p>
      </div>

      {/* Large Voice Copilot Button (Heart of the app) */}
      <div className="flex flex-col items-center justify-center py-2">
        <button
          onClick={() => handleVoiceCopilot()}
          aria-label="Tap to speak your intent"
          className={`relative group w-28 h-28 rounded-full flex flex-col items-center justify-center transition-all duration-300 active:scale-95 shadow-xl ${
            isListening
              ? 'bg-red-500 text-white animate-pulse-mic-active shadow-red-500/50'
              : isHC
                ? 'bg-[#FFD700] text-black border-4 border-black hover:bg-yellow-400 shadow-yellow-500/30'
                : 'bg-gradient-to-tr from-blue-600 to-indigo-600 text-white animate-pulse-mic shadow-blue-500/40'
          }`}
        >
          <Mic size={42} className={isListening ? 'animate-bounce' : ''} />
          <span className="text-[10px] font-extrabold uppercase mt-1 tracking-wider">
            {isListening ? (isHindi ? 'सुन रहा हूँ' : 'Listening') : (isHindi ? 'बोलें' : 'Speak')}
          </span>
        </button>

        {/* Quick Voice Suggestion Pills */}
        <div className="mt-4 flex flex-wrap justify-center gap-1.5 max-w-sm">
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleVoiceCopilot(p.query)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all active:scale-95 border ${
                isHC
                  ? 'border-[#FFD700] text-[#FFD700] hover:bg-neutral-800'
                  : 'bg-white hover:bg-blue-50 text-slate-700 border-slate-200 shadow-sm'
              }`}
            >
              <Zap size={11} className={isHC ? 'text-[#FFD700]' : 'text-blue-500'} />
              <span>{p.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Primary Capability Cards Grid */}
      <div className="grid grid-cols-2 gap-3 pt-1">
        {/* COMPLETE FORM */}
        <button
          onClick={() => {
            HapticsService.tactileClick();
            setActiveScreen('complete');
          }}
          className={`p-4 rounded-2xl text-left transition-all active:scale-95 border-2 flex flex-col justify-between ${
            isHC
              ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]'
              : 'bg-white border-blue-500/40 shadow-sm hover:shadow-md hover:border-blue-500'
          }`}
        >
          <div>
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-2.5 ${
              isHC ? 'bg-[#FFD700] text-black' : 'bg-blue-600 text-white'
            }`}>
              <FileCheck size={22} />
            </div>
            <h3 className={`font-black leading-tight ${isHC ? 'text-[#FFD700]' : 'text-slate-900'}`}>
              {isHindi ? 'फ़ॉर्म भरें' : 'COMPLETE'}
            </h3>
            <p className={`text-[11px] mt-1 leading-snug ${isHC ? 'text-white' : 'text-slate-500'}`}>
              {isHindi ? 'स्टेप-बाय-स्टेप 7 चरणों में छात्रवृत्ति' : '7-Step linearized scholarship form'}
            </p>
          </div>
          <span className={`text-[10px] font-bold mt-3 uppercase tracking-wider block ${
            isHC ? 'text-[#FFD700]' : 'text-blue-600'
          }`}>
            {isHindi ? 'शुरू करें →' : 'Launch →'}
          </span>
        </button>

        {/* READ NOTICE */}
        <button
          onClick={() => {
            HapticsService.tactileClick();
            setActiveScreen('read');
          }}
          className={`p-4 rounded-2xl text-left transition-all active:scale-95 border flex flex-col justify-between ${
            isHC
              ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]'
              : 'bg-white border-slate-200 shadow-sm hover:shadow-md hover:border-indigo-400'
          }`}
        >
          <div>
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-2.5 ${
              isHC ? 'bg-[#FFD700] text-black' : 'bg-indigo-600 text-white'
            }`}>
              <BookOpen size={22} />
            </div>
            <h3 className={`font-black leading-tight ${isHC ? 'text-[#FFD700]' : 'text-slate-900'}`}>
              {isHindi ? 'पढ़ें (Read)' : 'READ'}
            </h3>
            <p className={`text-[11px] mt-1 leading-snug ${isHC ? 'text-white' : 'text-slate-500'}`}>
              {isHindi ? 'नोटिस व आवश्यक प्रमाणपत्र समझें' : 'Document OCR & simplified deadlines'}
            </p>
          </div>
          <span className={`text-[10px] font-bold mt-3 uppercase tracking-wider block ${
            isHC ? 'text-[#FFD700]' : 'text-indigo-600'
          }`}>
            {isHindi ? 'विश्लेषण करें →' : 'Analyze →'}
          </span>
        </button>

        {/* SIGN TALK (ISL) */}
        <button
          onClick={() => {
            HapticsService.tactileClick();
            setActiveScreen('talk');
          }}
          className={`p-4 rounded-2xl text-left transition-all active:scale-95 border flex flex-col justify-between ${
            isHC
              ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]'
              : 'bg-white border-slate-200 shadow-sm hover:shadow-md hover:border-emerald-400'
          }`}
        >
          <div>
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-2.5 ${
              isHC ? 'bg-[#FFD700] text-black' : 'bg-emerald-600 text-white'
            }`}>
              <HandMetal size={22} />
            </div>
            <h3 className={`font-black leading-tight ${isHC ? 'text-[#FFD700]' : 'text-slate-900'}`}>
              {isHindi ? 'सांकेतिक (ISL)' : 'SIGN TALK'}
            </h3>
            <p className={`text-[11px] mt-1 leading-snug ${isHC ? 'text-white' : 'text-slate-500'}`}>
              {isHindi ? 'भारतीय सांकेतिक भाषा से आवाज़' : 'Indian Sign Language to Voice'}
            </p>
          </div>
          <span className={`text-[10px] font-bold mt-3 uppercase tracking-wider block ${
            isHC ? 'text-[#FFD700]' : 'text-emerald-600'
          }`}>
            {isHindi ? 'कैमरा खोलें →' : 'Translate →'}
          </span>
        </button>

        {/* SEE SPATIAL */}
        <button
          onClick={() => {
            HapticsService.tactileClick();
            setActiveScreen('see');
          }}
          className={`p-4 rounded-2xl text-left transition-all active:scale-95 border flex flex-col justify-between ${
            isHC
              ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]'
              : 'bg-white border-slate-200 shadow-sm hover:shadow-md hover:border-amber-400'
          }`}
        >
          <div>
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-2.5 ${
              isHC ? 'bg-[#FFD700] text-black' : 'bg-amber-600 text-white'
            }`}>
              <Compass size={22} />
            </div>
            <h3 className={`font-black leading-tight ${isHC ? 'text-[#FFD700]' : 'text-slate-900'}`}>
              {isHindi ? 'देखें (See)' : 'SPATIAL SEE'}
            </h3>
            <p className={`text-[11px] mt-1 leading-snug ${isHC ? 'text-white' : 'text-slate-500'}`}>
              {isHindi ? 'वस्तु ढूंढें व दिशा मार्गदर्शन' : 'Object finder & directional haptics'}
            </p>
          </div>
          <span className={`text-[10px] font-bold mt-3 uppercase tracking-wider block ${
            isHC ? 'text-[#FFD700]' : 'text-amber-600'
          }`}>
            {isHindi ? 'खोजें →' : 'Find →'}
          </span>
        </button>
      </div>

      {/* Stage 7 Telemetry Quick Bar */}
      <div
        onClick={() => {
          HapticsService.tactileClick();
          setActiveScreen('heatmap');
        }}
        className={`p-3 rounded-xl flex items-center justify-between cursor-pointer border ${
          isHC
            ? 'border-[#FFD700] text-[#FFD700] bg-neutral-900'
            : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200'
        }`}
      >
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
          <span className="text-xs font-bold">
            {isHindi ? 'चरण 7: सजीव सुलभता अंतर्दृष्टि (Heatmap)' : 'Stage 7: Live Interaction Heatmap'}
          </span>
        </div>
        <ArrowRight size={14} />
      </div>
    </div>
  );
};
