import React from 'react';
import { useTwin } from '../../context/TwinContext';
import { HapticsService } from '../../services/haptics';
import { Home, FileCheck, BookOpen, HandMetal, Compass, BarChart2, User } from 'lucide-react';

export const BottomNav: React.FC = () => {
  const { twin, activeScreen, setActiveScreen } = useTwin();
  const isHC = twin.visual.highContrast;
  const isHindi = twin.language === 'Hindi';

  const navItems = [
    {
      id: 'home',
      label: isHindi ? 'होम' : 'Home',
      icon: Home,
    },
    {
      id: 'complete',
      label: isHindi ? 'फ़ॉर्म' : 'Form',
      icon: FileCheck,
      badge: '7-Step',
    },
    {
      id: 'read',
      label: isHindi ? 'पढ़ें' : 'Read',
      icon: BookOpen,
    },
    {
      id: 'talk',
      label: isHindi ? 'इशारे' : 'ISL Sign',
      icon: HandMetal,
    },
    {
      id: 'see',
      label: isHindi ? 'देखें' : 'See',
      icon: Compass,
    },
    {
      id: 'heatmap',
      label: isHindi ? 'हीटमैप' : 'Heatmap',
      icon: BarChart2,
    },
    {
      id: 'profile',
      label: isHindi ? 'ट्विन' : 'Twin',
      icon: User,
    },
  ];

  const handleSelect = (id: string) => {
    HapticsService.tactileClick();
    setActiveScreen(id);
  };

  return (
    <nav
      className={`w-full safe-area-bottom select-none transition-colors border-t ${
        isHC
          ? 'bg-black text-[#FFD700] border-[#FFD700]'
          : 'bg-white/95 backdrop-blur-md text-slate-600 border-slate-200'
      }`}
    >
      <div className="grid grid-cols-7 items-center justify-around px-1 py-1.5 max-w-lg mx-auto">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = activeScreen === item.id;

          return (
            <button
              key={item.id}
              onClick={() => handleSelect(item.id)}
              className={`flex flex-col items-center justify-center py-1 px-0.5 rounded-xl transition-all relative ${
                isActive
                  ? isHC
                    ? 'bg-[#FFD700] text-black font-extrabold shadow-sm'
                    : 'text-blue-600 font-bold bg-blue-50/80'
                  : isHC
                    ? 'text-[#FFD700] hover:bg-neutral-900'
                    : 'hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="relative">
                <Icon size={twin.visual.largeText ? 22 : 20} strokeWidth={isActive ? 2.5 : 1.8} />
                {item.badge && !isActive && (
                  <span className="absolute -top-1 -right-2 w-2 h-2 rounded-full bg-blue-600 ring-2 ring-white" />
                )}
              </div>
              <span className={`tracking-tight truncate max-w-full text-center leading-none mt-1 ${
                twin.visual.largeText ? 'text-[11px]' : 'text-[10px]'
              }`}>
                {item.label}
              </span>
            </button>
          );
        })}
      </div>
      {/* Home indicator bar for mobile aesthetic */}
      <div className="w-28 h-1 mx-auto my-1 rounded-full bg-slate-300 dark:bg-neutral-700 opacity-60" />
    </nav>
  );
};
