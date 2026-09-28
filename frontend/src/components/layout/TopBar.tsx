import React from 'react';
import { useTwin } from '../../context/TwinContext';
import { Contrast, Volume2, VolumeX, Smartphone, Monitor, Globe } from 'lucide-react';

export const TopBar: React.FC = () => {
  const {
    twin,
    toggleHighContrast,
    toggleLargeText,
    setLanguage,
    deviceMode,
    setDeviceMode,
    backendStatus,
    updateTwin,
    stopSpeaking,
  } = useTwin();

  const isHC = twin.visual.highContrast;
  const isHindi = twin.language === 'Hindi';
  const isAudioOn = twin.comprehension.readInstructionsAloud;

  const toggleAudio = () => {
    if (isAudioOn) {
      stopSpeaking();
    }
    updateTwin({
      ...twin,
      comprehension: {
        ...twin.comprehension,
        readInstructionsAloud: !isAudioOn,
      },
    });
  };

  return (
    <header className={`w-full transition-colors ${
      isHC 
        ? 'bg-black text-[#FFD700] border-b-2 border-[#FFD700]' 
        : 'bg-white/95 backdrop-blur-md text-slate-800 border-b border-slate-200'
    }`}>
      {/* Mobile OS Status Bar Simulator */}
      <div className={`px-5 pt-2 pb-1 flex items-center justify-between text-[11px] font-semibold tracking-wider ${
        isHC ? 'text-[#FFD700]' : 'text-slate-500'
      }`}>
        <span>09:41</span>
        <div className="flex items-center gap-1.5">
          <span className={`inline-block w-2 h-2 rounded-full ${
            backendStatus === 'FastAPI' ? 'bg-emerald-500' : 'bg-blue-500 animate-pulse'
          }`} />
          <span className="text-[10px]">
            {backendStatus === 'FastAPI' ? 'API Online' : 'AI Engine Ready'}
          </span>
          <span className="ml-1">5G</span>
          <span>100%</span>
        </div>
      </div>

      {/* Main App Bar */}
      <div className="px-4 py-2.5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-xl flex items-center justify-center font-black text-sm shadow-sm ${
            isHC 
              ? 'bg-[#FFD700] text-black border-2 border-black' 
              : 'bg-gradient-to-tr from-blue-600 to-indigo-600 text-white'
          }`}>
            स
          </div>
          <div>
            <h1 className={`font-extrabold tracking-tight leading-none ${
              twin.visual.largeText ? 'text-lg' : 'text-base'
            } ${isHC ? 'text-[#FFD700]' : 'text-slate-900'}`}>
              {isHindi ? 'सहायक AI' : 'SAHAYAK AI'}
            </h1>
            <span className={`text-[10px] font-medium leading-none block mt-0.5 ${
              isHC ? 'text-white' : 'text-slate-500'
            }`}>
              Accessibility Copilot
            </span>
          </div>
        </div>

        {/* Quick Accessibility Toggles */}
        <div className="flex items-center gap-1">
          {/* Audio Guidance Toggle */}
          <button
            onClick={toggleAudio}
            title={isAudioOn ? 'Audio guidance on' : 'Audio guidance muted'}
            aria-label="Toggle voice guidance"
            className={`p-2 rounded-lg transition-transform active:scale-95 ${
              isAudioOn
                ? isHC ? 'bg-[#FFD700] text-black' : 'bg-blue-100 text-blue-700'
                : isHC ? 'text-[#FFD700] hover:bg-neutral-800' : 'text-slate-500 hover:bg-slate-100'
            }`}
          >
            {isAudioOn ? <Volume2 size={18} /> : <VolumeX size={18} />}
          </button>

          {/* High Contrast Toggle */}
          <button
            onClick={toggleHighContrast}
            title="Toggle High Contrast (WCAG AAA)"
            aria-label="Toggle High Contrast"
            className={`p-2 rounded-lg transition-transform active:scale-95 ${
              isHC
                ? 'bg-[#FFD700] text-black ring-2 ring-black'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Contrast size={18} />
          </button>

          {/* Text Size Scale Toggle */}
          <button
            onClick={toggleLargeText}
            title="Toggle Large Typography"
            aria-label="Toggle text size"
            className={`px-2 py-1 rounded-lg text-xs font-bold transition-transform active:scale-95 ${
              twin.visual.largeText
                ? isHC ? 'bg-[#FFD700] text-black' : 'bg-indigo-100 text-indigo-700'
                : isHC ? 'text-[#FFD700] hover:bg-neutral-800' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            {twin.visual.largeText ? 'A+' : 'A'}
          </button>

          {/* Language Switch */}
          <button
            onClick={() => setLanguage(isHindi ? 'English' : 'Hindi')}
            title="Switch Language"
            aria-label="Switch Language"
            className={`px-2 py-1 rounded-lg text-xs font-semibold flex items-center gap-1 transition-transform active:scale-95 ${
              isHC ? 'border border-[#FFD700] text-[#FFD700]' : 'border border-slate-300 text-slate-700 hover:bg-slate-100'
            }`}
          >
            <Globe size={13} />
            <span>{isHindi ? 'हिं' : 'EN'}</span>
          </button>

          {/* Device Frame Viewport Toggle */}
          <button
            onClick={() => setDeviceMode(deviceMode === 'frame' ? 'fullscreen' : 'frame')}
            title={deviceMode === 'frame' ? 'Switch to Fullscreen view' : 'Switch to Smartphone frame'}
            aria-label="Toggle mobile device frame"
            className={`hidden sm:flex p-2 rounded-lg text-slate-500 hover:bg-slate-100 transition-transform active:scale-95 ${
              isHC ? 'text-[#FFD700] hover:bg-neutral-800' : ''
            }`}
          >
            {deviceMode === 'frame' ? <Monitor size={17} /> : <Smartphone size={17} />}
          </button>
        </div>
      </div>
    </header>
  );
};
