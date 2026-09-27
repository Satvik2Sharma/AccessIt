#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR/mobile"

export PATH=/home/user/development/flutter/bin:$PATH

echo "=== Running Flutter Doctor & Devices ==="
flutter devices

echo "=== Launching Sahayak AI Mobile Application ==="
flutter run
