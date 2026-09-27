import React from 'react';
import { TwinProvider, useTwin } from './context/TwinContext';
import { MobileFrame } from './components/layout/MobileFrame';
import { HomeScreen } from './components/screens/HomeScreen';
import { CompleteFormScreen } from './components/screens/CompleteFormScreen';
import { ReadDocumentScreen } from './components/screens/ReadDocumentScreen';
import { SignTalkScreen } from './components/screens/SignTalkScreen';
import { SeeScreen } from './components/screens/SeeScreen';
import { HeatmapScreen } from './components/screens/HeatmapScreen';
import { ProfileScreen } from './components/screens/ProfileScreen';

const MainAppContent: React.FC = () => {
  const { twin, activeScreen } = useTwin();

  const isHC = twin.visual.highContrast;
  const isLarge = twin.visual.largeText;

  const renderScreen = () => {
    switch (activeScreen) {
      case 'home':
        return <HomeScreen />;
      case 'complete':
        return <CompleteFormScreen />;
      case 'read':
        return <ReadDocumentScreen />;
      case 'talk':
        return <SignTalkScreen />;
      case 'see':
        return <SeeScreen />;
      case 'heatmap':
        return <HeatmapScreen />;
      case 'profile':
        return <ProfileScreen />;
      default:
        return <HomeScreen />;
    }
  };

  return (
    <div className={`min-h-screen ${isHC ? 'high-contrast' : ''} ${isLarge ? 'large-text' : ''}`}>
      <MobileFrame>
        {renderScreen()}
      </MobileFrame>
    </div>
  );
};

export default function App() {
  return (
    <TwinProvider>
      <MainAppContent />
    </TwinProvider>
  );
}
