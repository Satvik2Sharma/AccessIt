import React from 'react';
import { useTwin } from '../../context/TwinContext';
import { TopBar } from './TopBar';
import { BottomNav } from './BottomNav';

interface MobileFrameProps {
  children: React.ReactNode;
}

export const MobileFrame: React.FC<MobileFrameProps> = ({ children }) => {
  const { twin, deviceMode } = useTwin();
  const isHC = twin.visual.highContrast;

  if (deviceMode === 'fullscreen') {
    return (
      <div className={`min-h-screen flex flex-col transition-colors ${
        isHC ? 'bg-black text-[#FFD700]' : 'bg-slate-100 text-slate-900'
      }`}>
        <div className="w-full max-w-2xl mx-auto flex-1 flex flex-col shadow-xl bg-white dark:bg-slate-900 overflow-hidden relative">
          <TopBar />
          <main className="flex-1 overflow-y-auto no-scrollbar flex flex-col">
            {children}
          </main>
          <BottomNav />
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen py-4 md:py-8 px-2 flex items-center justify-center transition-colors ${
      isHC ? 'bg-neutral-950 text-[#FFD700]' : 'bg-slate-900 text-slate-800'
    }`}>
      {/* Smartphone Chassis Frame */}
      <div className={`relative w-full max-w-[412px] h-[860px] max-h-[96vh] rounded-[48px] p-3 shadow-2xl flex flex-col transition-all ${
        isHC
          ? 'bg-neutral-900 border-4 border-[#FFD700] ring-4 ring-neutral-800'
          : 'bg-slate-800 border-[6px] border-slate-700 ring-1 ring-slate-600 shadow-[0_25px_60px_-15px_rgba(0,0,0,0.7)]'
      }`}>
        {/* Dynamic Island / Earpiece pill */}
        <div className="absolute top-5 left-1/2 -translate-x-1/2 w-28 h-6 bg-black rounded-full z-50 flex items-center justify-end px-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-slate-900 ring-1 ring-slate-800 flex items-center justify-center">
            <div className="w-1 h-1 rounded-full bg-blue-900/60" />
          </div>
        </div>

        {/* Screen Bezel & Content Area */}
        <div className={`w-full h-full rounded-[38px] overflow-hidden flex flex-col relative transition-colors ${
          isHC ? 'bg-black' : 'bg-slate-50'
        }`}>
          <TopBar />

          {/* Screen Content */}
          <main className="flex-1 overflow-y-auto no-scrollbar flex flex-col">
            {children}
          </main>

          <BottomNav />
        </div>
      </div>
    </div>
  );
};
