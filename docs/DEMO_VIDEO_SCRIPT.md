# Adapt-X — Judge Demo Video Script & Flow (3-Minute Walkthrough)

**Video Duration**: ~3:00 minutes  
**Goal**: Demonstrate how Adapt-X dynamically personalizes, detects barriers, compiles accessible flows, and verifies real task completion across diverse accessibility modalities.

---

## Scene 1: The Hook & Landing Page (0:00 - 0:30)

* **Visual**: Screen opens on the Adapt-X interactive landing page (`sahayak_ai.html`).
* **Voiceover**: 
  > *"Over 1.3 billion people face digital and physical barriers every day. Today, accessibility tools are fragmented—screen readers don't understand context, OCR apps don't understand intent, and forms are overwhelming. Welcome to **Adapt-X**—the Intent-Aware Personal Accessibility Copilot."*
* **Action**:
  1. Click **"Launch Demo / Login"**.
  2. Show **Judge Quick-Start Persona Selection**: Select *"Low Vision & Glare Sensitivity"*.
  3. One click triggers `POST /api/v1/auth/guest` $\to$ Instant authentication and high-contrast, large-typography UI generation.

---

## Scene 2: The Accessibility Twin in Action (0:30 - 1:00)

* **Visual**: Home Screen instantly re-renders in high contrast with tailored voice prompts and large touch targets.
* **Voiceover**:
  > *"Adapt-X creates an Accessibility Twin—a dynamic software model of user preferences, not medical diagnoses. Notice how contrast, dwell times, and 12-hour clock spatial guidance adapt in real time."*
* **Action**:
  1. Switch language toggle between English and Hindi $\to$ Voice and captions instantly adapt.
  2. Highlight the Accessibility Twin profile drawer showing active sensor tolerances.

---

## Scene 3: Demo 1 — Document Understanding to Action Flow (1:00 - 1:45)

* **Visual**: User holds camera up to a complex Indian Scholarship Notice.
* **Voiceover**:
  > *"Here is a dense government scholarship notice. Rather than dumping raw text, Adapt-X understands the user's intent."*
* **Action**:
  1. Camera frame processed via RapidOCR (`POST /api/v1/read`).
  2. Ask voice question: *"What is the deadline to apply?"* $\to$ Adapt-X answers: *"The deadline is October 31, 2026."*
  3. Click **"Convert Document to Action"** $\to$ Adapt-X automatically extracts required fields and constructs a 3-step accessible form journey (`POST /api/v1/read/tasks`).

---

## Scene 4: Demo 2 — Accessible Form Completion & ISL Sign Talk (1:45 - 2:30)

* **Visual**: Form Completion screen rendering one single field at a time with voice prompts.
* **Voiceover**:
  > *"Complex forms are flattened into single-step prompts with automatic validation. Users can respond via voice, touch, or Indian Sign Language."*
* **Action**:
  1. Spoken Prompt: *"Please state your full name."* $\to$ User speaks *"Aarav Sharma"*.
  2. Demonstrate **ISL Sign Talk**: Camera captures hand gesture $\to$ MediaPipe hand tracking classifies sign $\to$ Spoken audio output.

---

## Scene 5: Demo 3 — Verification, Heatmap & Closing (2:30 - 3:00)

* **Visual**: Verification Screen displaying 100% completion badge and interaction friction heatmap.
* **Voiceover**:
  > *"Adapt-X never leaves the user hanging. It verifies completion with a cryptographic token, detects points of user hesitation, and learns without violating privacy. Adapt-X: Independence, empowered."*
* **Action**:
  1. Show Verification Token (`VRF-2026-COMPLETE`).
  2. Display Interaction Friction Heatmap (`GET /api/v1/learning/heatmap`) showing green zero-barrier nodes.
  3. Conclude with Adapt-X logo and GitHub repository link.
