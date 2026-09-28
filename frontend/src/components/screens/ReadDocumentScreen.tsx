import React, { useState, useEffect } from 'react';
import { useTwin } from '../../context/TwinContext';
import { HapticsService } from '../../services/haptics';
import { ApiService } from '../../services/api';
import { 
  ArrowLeft, BookOpen, Calendar, FileText, Volume2, 
  Sparkles, CheckCircle2, ArrowRight 
} from 'lucide-react';

export const ReadDocumentScreen: React.FC = () => {
  const { twin, setActiveScreen, speakIfEnabled } = useTwin();
  const [loading, setLoading] = useState(true);
  const [docData, setDocData] = useState<any>(null);

  const isHC = twin.visual.highContrast;
  const isHindi = twin.language === 'Hindi';

  useEffect(() => {
    analyzeDocument();
  }, [twin.language]);

  const analyzeDocument = async () => {
    setLoading(true);
    const query = isHindi ? 'इस नोटिस में क्या ज़रूरी है?' : 'What is important in this notice?';
    const data = await ApiService.readDocument(query, twin);
    setDocData(data);
    setLoading(false);
    HapticsService.successDoublePulse();

    speakIfEnabled(data.spokenSummary);
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
            isHC ? 'bg-[#FFD700] text-black' : 'bg-indigo-100 text-indigo-700'
          }`}>
            DEMO 1: OCR & READ
          </span>
        </div>

        {/* Voice Query Banner */}
        <div className={`p-3 rounded-xl border flex items-center gap-2.5 ${
          isHC
            ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]'
            : 'bg-indigo-50/80 border-indigo-200 text-indigo-900'
        }`}>
          <div className={`p-1.5 rounded-lg ${isHC ? 'bg-[#FFD700] text-black' : 'bg-indigo-600 text-white'}`}>
            <BookOpen size={16} />
          </div>
          <p className="text-xs font-bold leading-tight">
            {isHindi ? '"इस नोटिस में क्या ज़रूरी है?"' : '"What is important in this notice?"'}
          </p>
        </div>

        {loading ? (
          <div className="py-12 flex flex-col items-center justify-center text-center">
            <div className={`w-10 h-10 border-4 border-t-transparent rounded-full animate-spin mb-3 ${
              isHC ? 'border-[#FFD700]' : 'border-indigo-600'
            }`} />
            <h4 className="font-bold text-sm">
              {isHindi ? 'OCR व कानूनी भाषा का सरलीकरण जारी...' : 'Running OCR & Barrier Simplification...'}
            </h4>
          </div>
        ) : docData && (
          <div className="space-y-3">
            {/* Title & Speech Card */}
            <div className={`p-4 rounded-2xl border-2 space-y-2.5 ${
              isHC ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]' : 'bg-white border-indigo-200 shadow-sm'
            }`}>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className={`text-[10px] font-bold uppercase tracking-wider block ${
                    isHC ? 'text-white' : 'text-indigo-600'
                  }`}>
                    {isHindi ? 'दस्तावेज़ शीर्षक' : 'Document Identified'}
                  </span>
                  <h3 className={`font-black text-base leading-tight mt-0.5 ${
                    isHC ? 'text-[#FFD700]' : 'text-slate-900'
                  }`}>
                    {docData.title}
                  </h3>
                </div>
                <button
                  onClick={() => {
                    HapticsService.tactileClick();
                    speakIfEnabled(docData.simplifiedSummary);
                  }}
                  title="Read aloud"
                  className={`p-2 rounded-xl shrink-0 ${
                    isHC ? 'bg-[#FFD700] text-black' : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100'
                  }`}
                >
                  <Volume2 size={18} />
                </button>
              </div>

              {/* Simplified Hindi/English Summary */}
              <div className={`p-3 rounded-xl text-xs leading-relaxed ${
                isHC ? 'bg-black text-white border border-[#FFD700]' : 'bg-slate-50 text-slate-700'
              }`}>
                {docData.simplifiedSummary}
              </div>
            </div>

            {/* Key Deadlines Card */}
            <div className={`p-3.5 rounded-2xl border ${
              isHC ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]' : 'bg-white border-slate-200 shadow-sm'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <Calendar size={17} className={isHC ? 'text-[#FFD700]' : 'text-red-500'} />
                <h4 className="text-xs font-black uppercase tracking-wider">
                  {isHindi ? 'अंतिम समय-सीमा (Deadlines)' : 'Key Deadlines'}
                </h4>
              </div>
              {docData.deadlines.map((dl: string, i: number) => (
                <div key={i} className={`p-2 rounded-lg font-bold text-xs flex items-center justify-between ${
                  isHC ? 'bg-black text-[#FFD700] border border-[#FFD700]' : 'bg-red-50 text-red-700'
                }`}>
                  <span>{dl}</span>
                  <span className="text-[10px] font-extrabold px-1.5 py-0.5 bg-red-200 text-red-800 rounded">
                    URGENT
                  </span>
                </div>
              ))}
            </div>

            {/* Required Documents / Certificates */}
            <div className={`p-3.5 rounded-2xl border ${
              isHC ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]' : 'bg-white border-slate-200 shadow-sm'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <FileText size={17} className={isHC ? 'text-[#FFD700]' : 'text-blue-600'} />
                <h4 className="text-xs font-black uppercase tracking-wider">
                  {isHindi ? 'आवश्यक प्रमाणपत्र (Documents Needed)' : 'Required Documents'}
                </h4>
              </div>
              <ul className="space-y-1.5">
                {docData.requiredDocuments.map((doc: string, i: number) => (
                  <li key={i} className="flex items-center gap-2 text-xs">
                    <CheckCircle2 size={14} className={isHC ? 'text-[#FFD700]' : 'text-emerald-600'} />
                    <span className="font-semibold">{doc}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Proactive Copilot CTA to Application Form */}
      <div className={`p-4 rounded-2xl border-2 space-y-3 ${
        isHC ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]' : 'bg-blue-50/90 border-blue-300'
      }`}>
        <div className="flex items-start gap-2.5">
          <Sparkles size={18} className={isHC ? 'text-[#FFD700]' : 'text-blue-600 shrink-0 mt-0.5'} />
          <div>
            <span className="text-xs font-black block">
              {isHindi ? 'सक्रिय मार्गदर्शन (Proactive Copilot)' : 'Proactive Assistance Available'}
            </span>
            <p className={`text-[11px] leading-tight mt-0.5 ${isHC ? 'text-white' : 'text-slate-600'}`}>
              {isHindi
                ? 'क्या आप चाहते हैं कि मैं छात्रवृत्ति फ़ॉर्म भरने में आपकी सहायता करूँ?'
                : 'Would you like Sahayak Copilot to guide you through the application form now?'}
            </p>
          </div>
        </div>

        <button
          onClick={() => {
            HapticsService.tactileClick();
            setActiveScreen('complete');
          }}
          className={`w-full py-3 px-4 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all active:scale-95 shadow-md ${
            isHC ? 'bg-[#FFD700] text-black hover:bg-yellow-400' : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          <span>{isHindi ? 'फ़ॉर्म आवेदन प्रारंभ करें' : 'Start Form Guidance (Demo 2)'}</span>
          <ArrowRight size={14} />
        </button>
      </div>
    </div>
  );
};
