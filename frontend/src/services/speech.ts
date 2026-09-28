// Web Speech API for TTS and Speech Recognition
import type { LanguagePreference } from '../types';

export class SpeechService {
  private static synth: SpeechSynthesis | null = typeof window !== 'undefined' ? window.speechSynthesis : null;
  private static recognition: any = null;

  static isSpeechSupported(): boolean {
    return typeof window !== 'undefined' && 'speechSynthesis' in window;
  }

  static isRecognitionSupported(): boolean {
    if (typeof window === 'undefined') return false;
    return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
  }

  // Speak out guidance or text
  static speak(text: string, language: LanguagePreference | string = 'Hindi', onEnd?: () => void): void {
    if (!this.synth) {
      if (onEnd) onEnd();
      return;
    }

    try {
      this.synth.cancel(); // Stop any active speech

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language === 'Hindi' ? 'hi-IN' : 'en-US';
      utterance.rate = 0.95; // Slightly slower for enhanced accessibility comprehension
      utterance.pitch = 1.0;

      // Find an optimal voice if available
      const voices = this.synth.getVoices();
      const targetLangPrefix = language === 'Hindi' ? 'hi' : 'en';
      const voice = voices.find(v => v.lang.startsWith(targetLangPrefix));
      if (voice) {
        utterance.voice = voice;
      }

      if (onEnd) {
        utterance.onend = onEnd;
        utterance.onerror = onEnd;
      }

      this.synth.speak(utterance);
    } catch (e) {
      console.warn('Speech synthesis error:', e);
      if (onEnd) onEnd();
    }
  }

  static stop(): void {
    if (this.synth) {
      try {
        this.synth.cancel();
      } catch (_) {}
    }
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (_) {}
    }
  }

  // Start voice listening
  static startListening(
    onResult: (text: string) => void,
    onEnd?: () => void,
    onError?: (err: string) => void,
    language: LanguagePreference | string = 'Hindi'
  ): void {
    const SpeechRecognitionClass = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognitionClass) {
      if (onError) onError('Speech recognition not supported in this browser.');
      if (onEnd) onEnd();
      return;
    }

    try {
      if (this.recognition) {
        this.recognition.abort();
      }

      const rec = new SpeechRecognitionClass();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = language === 'Hindi' ? 'hi-IN' : 'en-US';

      rec.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        onResult(transcript);
      };

      rec.onerror = (event: any) => {
        if (onError) onError(event.error || 'Speech recognition error');
        if (onEnd) onEnd();
      };

      rec.onend = () => {
        if (onEnd) onEnd();
      };

      this.recognition = rec;
      rec.start();
    } catch (e) {
      console.warn('Speech recognition start failed:', e);
      if (onError) onError('Could not access microphone');
      if (onEnd) onEnd();
    }
  }
}
