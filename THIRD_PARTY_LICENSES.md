# Sahayak AI — Third-Party Licenses & Attributions

This document records all open-source repositories audited, referenced, or selectively integrated into the Sahayak AI monorepo, in compliance with open-source licensing requirements.

---

## 1. Full-Stack AI VisualAid (Flutter + Python)
* **Repository**: `Full-Stack_AI-VisualAid_Flutter_Python`
* **Upstream URL**: https://github.com/Eng-M-Abdrabbou/Full-Stack_AI-VisualAid_Flutter_Python
* **Author / Copyright**: Copyright (c) 2023 Mahmoud Abdrabbou
* **License**: **MIT License**
* **Components Used / Adapted**:
  * Camera frame streaming patterns (`camera_view_widget.dart`).
  * Scene category taxonomy (`categories_places365.txt`).
  * Accessible large action button design paradigms (`action_button.dart`).
* **Attribution Notice**:
  > Licensed under the MIT License. Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files to use, copy, modify, merge, publish, distribute, and/or sublicense the software.

---

## 2. ISL-Interpreter (Indian Sign Language)
* **Repository**: `ISL-Interpreter`
* **Upstream URL**: https://github.com/Dev-2604/ISL-Interpreter
* **Author / Copyright**: Copyright (c) 2024 Dev Patel
* **License**: **MIT License**
* **Components Used / Adapted**:
  * MediaPipe hand landmark extraction logic (21 3D coordinates per hand, gamma correction lookup).
  * Static sign alphabet dictionary (A–Z, 1–9) and dynamic emergency sign sequence labels (`Doctor`, `Help`, `Hot`, `Lose`, `Pain`, `Thief`).
  * Visual recording status indicator patterns in Flutter UI.
* **Attribution Notice**:
  > Licensed under the MIT License. Permission is hereby granted, free of charge, to any person obtaining a copy of this software to deal in the Software without restriction.

---

## 3. SightBuddy (Android Accessibility App)
* **Repository**: `SightBuddy`
* **Upstream URL**: https://github.com/DrophouseLtd/SightBuddy
* **Author / Copyright**: Copyright (c) 2024 Drophouse Ltd
* **License**: **MIT License** (with Apache-2.0 third-party model notices)
* **Components Used / Adapted**:
  * Tactile haptic feedback patterns (scanning tick, object lock pulse, directional vibration).
  * High-contrast accessibility color palettes (Yellow on Dark Navy, high-legibility tokens).
  * Directional object guidance heuristics ("to your right", "directly ahead").
* **Attribution Notice**:
  > Licensed under the MIT License. Copyright (c) 2024 Drophouse Ltd. Third-party TensorFlow and EfficientDet models are licensed under Apache-2.0.

---

## 4. SightAssist (Vision-Language Scene Assistance)
* **Repository**: `SightAssist`
* **Upstream URL**: https://github.com/ArgonArnav/SightAssist
* **Author / Copyright**: Copyright (c) 2023 Arnav Argon
* **License**: **MIT License**
* **Components Used / Adapted**:
  * `SceneFusion` spatial algorithm: Associates OCR bounding boxes with physical object bounding boxes.
  * Modular object detection and EasyOCR wrapper interfaces (modernized into asynchronous FastAPI services).
* **Attribution Notice**:
  > Licensed under the MIT License. Copyright (c) 2023 Arnav Argon.
