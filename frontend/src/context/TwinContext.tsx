import React, { createContext, useContext, useState, useEffect } from 'react';
import type { AccessibilityTwin } from '../types';
import { HapticsService } from '../services/haptics';
import { SpeechService } from '../services/speech';
import { ApiService } from '../services/api';

interface TwinContextType {
  twin: AccessibilityTwin;
  updateTwin: (newTwin: AccessibilityTwin) => void;
  toggleHighContrast: () => void;
  toggleLargeText: () => void;
  setLanguage: (lang: 'Hindi' | 'English') => void;
  activeScreen: string;
  setActiveScreen: (screen: string) => void;
  deviceMode: 'frame' | 'fullscreen';
  setDeviceMode: (mode: 'frame' | 'fullscreen') => void;
  backendStatus: 'FastAPI' | 'LocalEngine';
  speakIfEnabled: (text: string) => void;
  stopSpeaking: () => void;
}

const defaultTwin: AccessibilityTwin = {
  id: 'default_twin_user',
  language: 'Hindi',
  secondaryLanguage: 'English',
  visual: {
    largeText: true,
    highContrast: false,
    screenReader: false,
    magnificationLevel: 1.2,
  },
  hearing: {
    captions: true,
    visualAlerts: true,
    signLanguage: true,
  },
  motor: {
    voiceInput: true,
    largeTouchTargets: true,
    reduceScrolling: true,
    dwellTimeMs: 300,
  },
  comprehension: {
    simplifiedLanguage: true,
    oneStepAtATime: true,
    readInstructionsAloud: true,
    showTaskProgress: true,
  },
  haptics: {
    enabled: true,
    intensity: 'medium',
    tactileConfirmation: true,
  },
  preferredInput: 'voice',
  preferredOutput: 'voice_and_text',
};

const TwinContext = createContext<TwinContextType | undefined>(undefined);

export const TwinProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [twin, setTwin] = useState<AccessibilityTwin>(() => {
    try {
      const saved = localStorage.getItem('sahayak_twin');
      if (saved) return JSON.parse(saved);
    } catch (_) {}
    return defaultTwin;
  });

  const [activeScreen, setActiveScreen] = useState<string>('home');
  const [deviceMode, setDeviceMode] = useState<'frame' | 'fullscreen'>('frame');
  const [backendStatus, setBackendStatus] = useState<'FastAPI' | 'LocalEngine'>('LocalEngine');

  useEffect(() => {
    // Check backend health
    ApiService.checkHealth().then(res => {
      setBackendStatus(res.backendType);
    });
  }, []);

  const updateTwin = (newTwin: AccessibilityTwin) => {
    HapticsService.tactileClick();
    setTwin(newTwin);
    try {
      localStorage.setItem('sahayak_twin', JSON.stringify(newTwin));
    } catch (_) {}
  };

  const toggleHighContrast = () => {
    HapticsService.tactileClick();
    const updated = {
      ...twin,
      visual: {
        ...twin.visual,
        highContrast: !twin.visual.highContrast,
      },
    };
    updateTwin(updated);
  };

  const toggleLargeText = () => {
    HapticsService.tactileClick();
    const updated = {
      ...twin,
      visual: {
        ...twin.visual,
        largeText: !twin.visual.largeText,
      },
    };
    updateTwin(updated);
  };

  const setLanguage = (lang: 'Hindi' | 'English') => {
    HapticsService.tactileClick();
    const updated: AccessibilityTwin = {
      ...twin,
      language: lang,
    };
    updateTwin(updated);
  };

  const speakIfEnabled = (text: string) => {
    if (twin.comprehension.readInstructionsAloud) {
      SpeechService.speak(text, twin.language);
    }
  };

  const stopSpeaking = () => {
    SpeechService.stop();
  };

  return (
    <TwinContext.Provider
      value={{
        twin,
        updateTwin,
        toggleHighContrast,
        toggleLargeText,
        setLanguage,
        activeScreen,
        setActiveScreen,
        deviceMode,
        setDeviceMode,
        backendStatus,
        speakIfEnabled,
        stopSpeaking,
      }}
    >
      {children}
    </TwinContext.Provider>
  );
};

export const useTwin = () => {
  const context = useContext(TwinContext);
  if (!context) {
    throw new Error('useTwin must be used within a TwinProvider');
  }
  return context;
};
