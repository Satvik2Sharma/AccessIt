// Browser Haptic Feedback Service using Navigator Vibration API

export class HapticsService {
  private static isAvailable(): boolean {
    return typeof window !== 'undefined' && 'navigator' in window && 'vibrate' in navigator;
  }

  // Soft click for buttons and selections
  static tactileClick(): void {
    if (this.isAvailable()) {
      try {
        navigator.vibrate(25);
      } catch (_) {}
    }
  }

  // Single confirmation pulse when field is answered
  static confirmationPulse(): void {
    if (this.isAvailable()) {
      try {
        navigator.vibrate(60);
      } catch (_) {}
    }
  }

  // Double pulse for completion and successful action
  static successDoublePulse(): void {
    if (this.isAvailable()) {
      try {
        navigator.vibrate([60, 50, 90]);
      } catch (_) {}
    }
  }

  // Celebratory verification sequence
  static celebrationPulse(): void {
    if (this.isAvailable()) {
      try {
        navigator.vibrate([70, 40, 100, 40, 150]);
      } catch (_) {}
    }
  }

  // Directional spatial buzz
  static directionalBuzz(direction: string): void {
    if (!this.isAvailable()) return;
    try {
      if (direction.includes('RIGHT')) {
        // Double rightward pulse
        navigator.vibrate([40, 60, 100]);
      } else if (direction.includes('LEFT')) {
        // Double leftward pulse
        navigator.vibrate([100, 60, 40]);
      } else {
        navigator.vibrate(50);
      }
    } catch (_) {}
  }
}
