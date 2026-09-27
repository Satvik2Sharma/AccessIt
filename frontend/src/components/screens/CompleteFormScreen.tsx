import React, { useState, useEffect } from 'react';
import { useTwin } from '../../context/TwinContext';
import { HapticsService } from '../../services/haptics';
import { SpeechService } from '../../services/speech';
import { ApiService } from '../../services/api';
import type { AccessibleTaskFlow, VerificationResult } from '../../types';
import confetti from 'canvas-confetti';
import { 
  ArrowLeft, CheckCircle2, Mic, Volume2, ShieldAlert, 
  Award, RotateCcw, ArrowRight 
} from 'lucide-react';

export const CompleteFormScreen: React.FC = () => {
  const { twin, setActiveScreen, speakIfEnabled } = useTwin();
  const [loading, setLoading] = useState(true);
  const [flow, setFlow] = useState<AccessibleTaskFlow | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [verification, setVerification] = useState<VerificationResult | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const isHC = twin.visual.highContrast;
  const isHindi = twin.language === 'Hindi';

  // Demo sample pre-fills for rapid evaluation
  const demoAnswers = [
    isHindi ? 'सात्विक शर्मा' : 'Satvik Sharma',
    '15/08/2003',
    isHindi ? 'सेक्टर 62, नोएडा, उत्तर प्रदेश - 201309' : 'Sector 62, Noida, Uttar Pradesh - 201309',
    'General',
    '₹ 1,80,000',
    '9824 5510 1289',
    'SBI0004921 / 20394812839',
  ];

  useEffect(() => {
    loadForm();
  }, [twin.language]);

  const loadForm = async () => {
    setLoading(true);
    setVerification(null);
    setCurrentStepIndex(0);
    setAnswers({});
    const res = await ApiService.analyzeForm(twin);
    setFlow(res);
    setLoading(false);

    if (res.steps.length > 0) {
      setInputValue(demoAnswers[0]);
      speakIfEnabled(res.steps[0].spoken_prompt);
    }
  };

  const handleSpeechInput = () => {
    HapticsService.tactileClick();
    setIsRecording(true);

    if (SpeechService.isRecognitionSupported()) {
      SpeechService.startListening(
        (transcript) => {
          setInputValue(transcript);
          setIsRecording(false);
          HapticsService.confirmationPulse();
        },
        () => setIsRecording(false),
        () => {
          setIsRecording(false);
          // Fallback to sample demo answer
          setInputValue(demoAnswers[currentStepIndex] || 'Confirmed');
        },
        twin.language
      );
    } else {
      setTimeout(() => {
        setInputValue(demoAnswers[currentStepIndex] || 'Confirmed');
        setIsRecording(false);
        HapticsService.confirmationPulse();
      }, 1000);
    }
  };

  const handleNextStep = async () => {
    if (!flow) return;
    const step = flow.steps[currentStepIndex];
    const val = inputValue.trim() || demoAnswers[currentStepIndex];

    HapticsService.confirmationPulse();
    const newAnswers = { ...answers, [step.field_id]: val };
    setAnswers(newAnswers);

    const res = await ApiService.respondFormField(
      flow.task_id,
      step.field_id,
      val,
      currentStepIndex,
      flow.total_steps,
      twin
    );

    if (currentStepIndex + 1 < flow.total_steps) {
      const nextIdx = currentStepIndex + 1;
      setCurrentStepIndex(nextIdx);
      setInputValue(demoAnswers[nextIdx] || '');
      speakIfEnabled(flow.steps[nextIdx].spoken_prompt);
    } else {
      // Completed all 7 fields!
      HapticsService.celebrationPulse();
      setVerification(res.verification);

      try {
        confetti({
          particleCount: 120,
          spread: 70,
          origin: { y: 0.6 },
        });
      } catch (_) {}

      const winMessage = isHindi
        ? 'बधाई हो! आपका छात्रवृत्ति फ़ॉर्म सफलतापूर्वक सत्यापित और पूर्ण हो चुका है।'
        : 'Congratulations! Your scholarship form is fully verified and completed.';
      speakIfEnabled(winMessage);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <div className={`w-12 h-12 border-4 border-t-transparent rounded-full animate-spin mb-4 ${
          isHC ? 'border-[#FFD700]' : 'border-blue-600'
        }`} />
        <h3 className="font-bold text-lg">
          {isHindi ? 'दस्तावेज़ एवं बाधाओं का विश्लेषण...' : 'Analyzing Form & Interaction Barriers...'}
        </h3>
        <p className="text-xs text-slate-500 mt-1 max-w-xs">
          Stage 3: Barrier Engine & Stage 4: Accessible Flow Compiler
        </p>
      </div>
    );
  }

  // ----------------------------------------------------
  // VERIFICATION COMPLETE VIEW
  // ----------------------------------------------------
  if (verification && verification.status === 'COMPLETED') {
    return (
      <div className="flex-1 p-5 flex flex-col justify-between space-y-4">
        <div className="space-y-4">
          <div className="text-center pt-3">
            <div className={`w-16 h-16 rounded-full mx-auto flex items-center justify-center mb-3 shadow-lg ${
              isHC ? 'bg-[#FFD700] text-black' : 'bg-emerald-500 text-white'
            }`}>
              <Award size={36} />
            </div>
            <span className={`text-[11px] font-black tracking-widest uppercase block ${
              isHC ? 'text-[#FFD700]' : 'text-emerald-600'
            }`}>
              {isHindi ? 'चरण 6: कार्य सत्यापन सफल' : 'STAGE 6: TASK VERIFIED'}
            </span>
            <h2 className={`font-black text-2xl mt-1 ${isHC ? 'text-[#FFD700]' : 'text-slate-900'}`}>
              {isHindi ? 'फ़ॉर्म पूर्ण हो गया!' : 'Form Completed!'}
            </h2>
            <p className={`text-xs mt-1 ${isHC ? 'text-white' : 'text-slate-600'}`}>
              {verification.summary_message}
            </p>
          </div>

          {/* Official Verification Certificate Card */}
          <div className={`p-4 rounded-2xl border-2 space-y-3 ${
            isHC
              ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]'
              : 'bg-white border-emerald-500/50 shadow-md'
          }`}>
            <div className="flex items-center justify-between border-b pb-2">
              <span className="text-xs font-bold uppercase tracking-wider">
                {isHindi ? 'सत्यापन टोकन' : 'Verification Token'}
              </span>
              <span className={`text-xs font-mono font-black px-2 py-0.5 rounded ${
                isHC ? 'bg-[#FFD700] text-black' : 'bg-emerald-100 text-emerald-800'
              }`}>
                {verification.verification_token}
              </span>
            </div>

            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between">
                <span className={isHC ? 'text-white' : 'text-slate-500'}>Task Type:</span>
                <span className="font-semibold">SCHOLARSHIP_FORM_7F</span>
              </div>
              <div className="flex justify-between">
                <span className={isHC ? 'text-white' : 'text-slate-500'}>Fields Completed:</span>
                <span className="font-bold text-emerald-600">7 / 7 (100%)</span>
              </div>
              <div className="flex justify-between">
                <span className={isHC ? 'text-white' : 'text-slate-500'}>Applicant:</span>
                <span className="font-semibold">{answers['full_name'] || 'Satvik Sharma'}</span>
              </div>
              <div className="flex justify-between">
                <span className={isHC ? 'text-white' : 'text-slate-500'}>Aadhaar Number:</span>
                <span className="font-mono">{answers['aadhaar'] || '9824 5510 1289'}</span>
              </div>
              <div className="flex justify-between">
                <span className={isHC ? 'text-white' : 'text-slate-500'}>Bank & IFSC:</span>
                <span className="font-mono">{answers['bank_account'] || 'SBI0004921'}</span>
              </div>
            </div>

            <div className={`p-2.5 rounded-xl text-[11px] flex items-center gap-2 ${
              isHC ? 'bg-black text-[#FFD700] border border-[#FFD700]' : 'bg-emerald-50 text-emerald-800'
            }`}>
              <CheckCircle2 size={16} className="shrink-0" />
              <span>
                {isHindi
                  ? 'सभी सरकारी नियम एवं दस्तावेज जांच सफल रही। डेटा सुरक्षित रूप से प्रेषित किया गया।'
                  : 'WCAG AAA accessible workflow satisfied. Official receipt stored locally.'}
              </span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-2 pt-2">
          <button
            onClick={() => setActiveScreen('home')}
            className={`w-full py-3.5 px-4 rounded-xl font-bold text-sm transition-all active:scale-95 shadow-md flex items-center justify-center gap-2 ${
              isHC
                ? 'bg-[#FFD700] text-black font-extrabold hover:bg-yellow-400'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            <span>{isHindi ? 'मुख्य पृष्ठ पर लौटें' : 'Return to Home'}</span>
            <ArrowRight size={16} />
          </button>
          <button
            onClick={loadForm}
            className={`w-full py-2.5 px-4 rounded-xl font-semibold text-xs transition-all active:scale-95 flex items-center justify-center gap-1.5 ${
              isHC ? 'text-[#FFD700] hover:bg-neutral-900' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <RotateCcw size={14} />
            <span>{isHindi ? 'पुनः प्रारंभ करें' : 'Start Another Application'}</span>
          </button>
        </div>
      </div>
    );
  }

  if (!flow || flow.steps.length === 0) return null;

  const currentStep = flow.steps[currentStepIndex];
  const progressPercent = Math.round(((currentStepIndex + 1) / flow.total_steps) * 100);

  return (
    <div className="flex-1 p-4 flex flex-col justify-between">
      <div className="space-y-3.5">
        {/* Top Header & Back Button */}
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
          <span className={`text-xs font-mono font-black px-2.5 py-1 rounded-full ${
            isHC ? 'bg-[#FFD700] text-black' : 'bg-blue-100 text-blue-700'
          }`}>
            {currentStepIndex + 1} / {flow.total_steps}
          </span>
        </div>

        {/* Linear Progress Bar */}
        <div>
          <div className="flex justify-between items-center text-[11px] font-semibold mb-1">
            <span className={isHC ? 'text-[#FFD700]' : 'text-slate-600'}>
              {isHindi ? 'प्रगति (Linearized Flow)' : 'Task Progress'}
            </span>
            <span className="font-mono font-bold">{progressPercent}%</span>
          </div>
          <div className={`w-full h-2.5 rounded-full overflow-hidden ${
            isHC ? 'bg-neutral-800 border border-[#FFD700]' : 'bg-slate-200'
          }`}>
            <div
              className={`h-full transition-all duration-300 ${
                isHC ? 'bg-[#FFD700]' : 'bg-blue-600'
              }`}
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Detected Barriers Pill */}
        {flow.detected_barriers.length > 0 && currentStepIndex === 0 && (
          <div className={`p-2.5 rounded-xl border flex items-start gap-2 text-xs ${
            isHC
              ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]'
              : 'bg-amber-50 border-amber-300 text-amber-900'
          }`}>
            <ShieldAlert size={16} className="shrink-0 mt-0.5 text-amber-500" />
            <div>
              <span className="font-bold block">
                {isHindi ? 'बाधा समाधान सक्रिय (Barrier Engine):' : 'Barriers Remediated:'}
              </span>
              <span className="text-[11px] opacity-90 leading-tight block">
                {flow.detected_barriers[0].description} → {flow.strategy}
              </span>
            </div>
          </div>
        )}

        {/* Current Step Question Card */}
        <div className={`p-4 rounded-2xl border-2 space-y-3 shadow-sm ${
          isHC
            ? 'bg-neutral-900 border-[#FFD700] text-[#FFD700]'
            : 'bg-white border-blue-200'
        }`}>
          <div className="flex items-start justify-between gap-2">
            <div>
              <span className={`text-[11px] font-bold tracking-wider uppercase block ${
                isHC ? 'text-white' : 'text-blue-600'
              }`}>
                {currentStep.label}
              </span>
              <h2 className={`font-black tracking-tight leading-snug mt-1 ${
                twin.visual.largeText ? 'text-xl' : 'text-lg'
              } ${isHC ? 'text-[#FFD700]' : 'text-slate-900'}`}>
                {currentStep.display_prompt}
              </h2>
            </div>
            <button
              onClick={() => {
                HapticsService.tactileClick();
                speakIfEnabled(currentStep.spoken_prompt);
              }}
              title="Speak prompt aloud"
              className={`p-2.5 rounded-xl shrink-0 transition-transform active:scale-90 ${
                isHC ? 'bg-[#FFD700] text-black' : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
              }`}
            >
              <Volume2 size={20} />
            </button>
          </div>

          <p className={`text-xs italic leading-relaxed ${isHC ? 'text-white' : 'text-slate-600'}`}>
            "{currentStep.spoken_prompt}"
          </p>

          {/* Input Box with Voice & Keyboard */}
          <div className="space-y-2 pt-2">
            <div className="relative">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={isHindi ? 'यहाँ उत्तर लिखें या बोलें...' : 'Type or dictate your answer...'}
                className={`w-full px-4 py-3 rounded-xl border text-sm font-semibold transition-all outline-none ${
                  isHC
                    ? 'bg-black text-[#FFD700] border-[#FFD700] focus:ring-2 focus:ring-[#FFD700]'
                    : 'bg-slate-50 text-slate-800 border-slate-300 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100'
                }`}
              />
              <button
                onClick={handleSpeechInput}
                title="Dictate with microphone"
                className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-transform active:scale-90 ${
                  isRecording
                    ? 'bg-red-500 text-white animate-pulse'
                    : isHC
                      ? 'bg-[#FFD700] text-black'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                <Mic size={16} />
              </button>
            </div>

            {/* Quick Demo Pre-Fill Helper Chip */}
            <div className="flex items-center justify-between pt-1">
              <span className={`text-[11px] font-medium ${isHC ? 'text-white' : 'text-slate-500'}`}>
                {isHindi ? 'त्वरित डेमो उत्तर:' : 'Demo Answer:'}
              </span>
              <button
                onClick={() => {
                  HapticsService.tactileClick();
                  setInputValue(demoAnswers[currentStepIndex] || '');
                }}
                className={`text-[11px] font-bold px-2 py-0.5 rounded-md underline transition-all ${
                  isHC ? 'text-[#FFD700]' : 'text-blue-600 hover:text-blue-800'
                }`}
              >
                {demoAnswers[currentStepIndex]}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Advance Button */}
      <div className="pt-4 space-y-2">
        <button
          onClick={handleNextStep}
          className={`w-full py-3.5 px-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all active:scale-95 shadow-md ${
            isHC
              ? 'bg-[#FFD700] text-black font-extrabold hover:bg-yellow-400'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          <span>
            {currentStepIndex + 1 === flow.total_steps
              ? (isHindi ? 'सत्यापित करें और जमा करें' : 'Verify & Submit Form')
              : (isHindi ? 'अगला चरण →' : 'Confirm & Continue →')}
          </span>
          <CheckCircle2 size={18} />
        </button>
      </div>
    </div>
  );
};
