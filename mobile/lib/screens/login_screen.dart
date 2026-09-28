// Adapt-X — Accessible Login & Sign Up Screen
// High-Contrast WCAG AAA compliant, semantic accessibility, and 1-Click Judge Quick-Start Personas.

import 'package:flutter/material.dart';
import '../models/accessibility_twin.dart';
import '../services/api_service.dart';
import '../services/haptics_service.dart';

class LoginScreen extends StatefulWidget {
  final AccessibilityTwin twin;
  final Function(AccessibilityTwin) onAuthenticated;

  const LoginScreen({
    super.key,
    required this.twin,
    required this.onAuthenticated,
  });

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool _isSignUp = false;
  bool _isLoading = false;
  String? _errorMessage;

  final _nameController = TextEditingController();
  final _emailController = TextEditingController(text: 'aarav@adaptx.ai');
  final _passwordController = TextEditingController(text: 'password123');
  final _confirmPasswordController = TextEditingController();
  String _selectedLanguage = 'English';

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _handleAuthentication() async {
    HapticsService.confirmationPulse();
    setState(() {
      _errorMessage = null;
      _isLoading = true;
    });

    final email = _emailController.text.trim();
    final password = _passwordController.text;

    if (email.isEmpty || !email.contains('@')) {
      setState(() {
        _isLoading = false;
        _errorMessage = 'Please enter a valid email address.';
      });
      return;
    }

    if (password.length < 6) {
      setState(() {
        _isLoading = false;
        _errorMessage = 'Password must be at least 6 characters.';
      });
      return;
    }

    if (_isSignUp && password != _confirmPasswordController.text) {
      setState(() {
        _isLoading = false;
        _errorMessage = 'Passwords do not match.';
      });
      return;
    }

    Map<String, dynamic> result;
    if (_isSignUp) {
      final name = _nameController.text.trim().isEmpty ? email.split('@')[0] : _nameController.text.trim();
      result = await ApiService.register(
        name: name,
        email: email,
        password: password,
        preferredLanguage: _selectedLanguage,
      );
    } else {
      result = await ApiService.login(email: email, password: password);
    }

    if (!mounted) return;

    if (result['success'] == true) {
      final data = result['data'];
      final twinData = data['twin'];
      if (twinData != null) {
        final newTwin = AccessibilityTwin(
          id: twinData['id'] ?? widget.twin.id,
          language: twinData['language'] ?? widget.twin.language,
          largeText: twinData['visual']?['large_text'] ?? widget.twin.largeText,
          highContrast: twinData['visual']?['high_contrast'] ?? widget.twin.highContrast,
          voiceInput: twinData['motor']?['voice_input'] ?? widget.twin.voiceInput,
          oneStepAtATime: twinData['comprehension']?['one_step_at_a_time'] ?? widget.twin.oneStepAtATime,
          simplifiedLanguage: twinData['comprehension']?['simplified_language'] ?? widget.twin.simplifiedLanguage,
          hapticFeedback: twinData['haptics']?['enabled'] ?? widget.twin.hapticFeedback,
        );
        widget.onAuthenticated(newTwin);
      }
      Navigator.pushReplacementNamed(context, '/home');
    } else {
      setState(() {
        _isLoading = false;
        _errorMessage = result['message'] ?? 'Authentication failed.';
      });
    }
  }

  void _handleGuestPersonaLogin(String persona, String personaTitle) async {
    HapticsService.confirmationPulse();
    setState(() {

      _errorMessage = null;
      _isLoading = true;
    });

    final res = await ApiService.guestLogin(
      persona: persona,
      language: _selectedLanguage,
      customName: 'Judge ($personaTitle)',
    );

    if (!mounted) return;

    if (res['success'] == true) {
      final twinData = res['data']['twin'];
      if (twinData != null) {
        final newTwin = AccessibilityTwin(
          id: twinData['id'] ?? widget.twin.id,
          language: twinData['language'] ?? widget.twin.language,
          largeText: twinData['visual']?['large_text'] ?? widget.twin.largeText,
          highContrast: twinData['visual']?['high_contrast'] ?? widget.twin.highContrast,
          voiceInput: twinData['motor']?['voice_input'] ?? widget.twin.voiceInput,
          oneStepAtATime: twinData['comprehension']?['one_step_at_a_time'] ?? widget.twin.oneStepAtATime,
          simplifiedLanguage: twinData['comprehension']?['simplified_language'] ?? widget.twin.simplifiedLanguage,
          hapticFeedback: twinData['haptics']?['enabled'] ?? widget.twin.hapticFeedback,
        );
        widget.onAuthenticated(newTwin);
      }
      Navigator.pushReplacementNamed(context, '/home');
    } else {
      setState(() {
        _isLoading = false;
        _errorMessage = res['message'] ?? 'Guest persona login failed.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isHC = widget.twin.highContrast;
    final primaryColor = isHC ? const Color(0xFFFFD600) : const Color(0xFF64B5F6);
    final cardBg = isHC ? const Color(0xFF141414) : const Color(0xFF1E293B);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 1. App Branding Header
                Semantics(
                  header: true,
                  label: 'Adapt-X Intent-Aware Accessibility Copilot',
                  child: Column(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: primaryColor.withOpacity(0.15),
                          shape: BoxShape.circle,
                          border: Border.all(color: primaryColor, width: isHC ? 3 : 1.5),
                        ),
                        child: Icon(Icons.accessibility_new_rounded, size: 48, color: primaryColor),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'ADAPT-X',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 2.0,
                          color: primaryColor,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Intent-Aware Personal Accessibility Copilot',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                          color: isHC ? Colors.white : Colors.white70,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 28),

                // 2. Auth Mode Switcher (Sign In vs Create Account)
                Container(
                  decoration: BoxDecoration(
                    color: cardBg,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: primaryColor.withOpacity(0.3), width: 1),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextButton(
                          style: TextButton.styleFrom(
                            backgroundColor: !_isSignUp ? primaryColor.withOpacity(0.2) : Colors.transparent,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          onPressed: () => setState(() {
                            _isSignUp = false;
                            _errorMessage = null;
                          }),
                          child: Text(
                            'Sign In',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: !_isSignUp ? primaryColor : Colors.white70,
                            ),
                          ),
                        ),
                      ),
                      Expanded(
                        child: TextButton(
                          style: TextButton.styleFrom(
                            backgroundColor: _isSignUp ? primaryColor.withOpacity(0.2) : Colors.transparent,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          onPressed: () => setState(() {
                            _isSignUp = true;
                            _errorMessage = null;
                          }),
                          child: Text(
                            'Create Account',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: _isSignUp ? primaryColor : Colors.white70,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // 3. Error Banner
                if (_errorMessage != null)
                  Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.redAccent, width: 1.5),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline, color: Colors.redAccent),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            _errorMessage!,
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
                          ),
                        ),
                      ],
                    ),
                  ),

                // 4. Form Fields
                if (_isSignUp) ...[
                  TextField(
                    controller: _nameController,
                    style: const TextStyle(color: Colors.white, fontSize: 16),
                    decoration: _inputDecoration('Full Name', Icons.person, primaryColor, isHC),
                  ),
                  const SizedBox(height: 14),
                ],

                TextField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  style: const TextStyle(color: Colors.white, fontSize: 16),
                  decoration: _inputDecoration('Email Address', Icons.email, primaryColor, isHC),
                ),
                const SizedBox(height: 14),

                TextField(
                  controller: _passwordController,
                  obscureText: true,
                  style: const TextStyle(color: Colors.white, fontSize: 16),
                  decoration: _inputDecoration('Password', Icons.lock, primaryColor, isHC),
                ),
                const SizedBox(height: 14),

                if (_isSignUp) ...[
                  TextField(
                    controller: _confirmPasswordController,
                    obscureText: true,
                    style: const TextStyle(color: Colors.white, fontSize: 16),
                    decoration: _inputDecoration('Confirm Password', Icons.lock_outline, primaryColor, isHC),
                  ),
                  const SizedBox(height: 14),
                  DropdownButtonFormField<String>(
                    value: _selectedLanguage,
                    dropdownColor: cardBg,
                    style: const TextStyle(color: Colors.white, fontSize: 16),
                    decoration: _inputDecoration('Preferred Language', Icons.language, primaryColor, isHC),
                    items: const [
                      DropdownMenuItem(value: 'English', child: Text('English (US/UK)')),
                      DropdownMenuItem(value: 'Hindi', child: Text('हिंदी (Hindi)')),
                      DropdownMenuItem(value: 'Tamil', child: Text('தமிழ் (Tamil)')),
                      DropdownMenuItem(value: 'Telugu', child: Text('తెలుగు (Telugu)')),
                    ],
                    onChanged: (val) {
                      if (val != null) setState(() => _selectedLanguage = val);
                    },
                  ),
                  const SizedBox(height: 14),
                ],

                // 5. Submit Button
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: primaryColor,
                    foregroundColor: Colors.black,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    elevation: 4,
                  ),
                  onPressed: _isLoading ? null : _handleAuthentication,
                  child: _isLoading
                      ? const SizedBox(
                          height: 24,
                          width: 24,
                          child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.black),
                        )
                      : Text(
                          _isSignUp ? 'REGISTER & CREATE TWIN' : 'SECURE SIGN IN',
                          style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w900, letterSpacing: 0.5),
                        ),
                ),
                const SizedBox(height: 28),

                // 6. Judge 1-Click Quick-Start Personas Section
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: cardBg,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: primaryColor.withOpacity(0.4), width: 1.5),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.workspace_premium_rounded, color: primaryColor, size: 22),
                          const SizedBox(width: 8),
                          Text(
                            'JUDGE 1-CLICK PERSONAS',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 1.0,
                              color: primaryColor,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      _personaButton('Low Vision & Glare', Icons.visibility_off, () {
                        _handleGuestPersonaLogin('low_vision', 'Low Vision');
                      }, primaryColor),
                      const SizedBox(height: 8),
                      _personaButton('Motor & Tremor Assistance', Icons.touch_app, () {
                        _handleGuestPersonaLogin('motor_difficulty', 'Motor Difficulty');
                      }, primaryColor),
                      const SizedBox(height: 8),
                      _personaButton('Deaf & ISL Sign Talk', Icons.sign_language, () {
                        _handleGuestPersonaLogin('hearing_impairment', 'ISL Hearing');
                      }, primaryColor),
                      const SizedBox(height: 8),
                      _personaButton('Cognitive & Jargon Relief', Icons.lightbulb_outline, () {
                        _handleGuestPersonaLogin('elderly_simplified', 'Simplified');
                      }, primaryColor),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  InputDecoration _inputDecoration(String label, IconData icon, Color color, bool isHC) {
    return InputDecoration(
      labelText: label,
      labelStyle: TextStyle(color: isHC ? color : Colors.white70),
      prefixIcon: Icon(icon, color: color),
      filled: true,
      fillColor: isHC ? const Color(0xFF141414) : const Color(0xFF1E293B),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: color.withOpacity(0.3)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: color, width: 2),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
    );
  }

  Widget _personaButton(String title, IconData icon, VoidCallback onTap, Color primaryColor) {
    return OutlinedButton.icon(
      style: OutlinedButton.styleFrom(
        foregroundColor: Colors.white,
        side: BorderSide(color: primaryColor.withOpacity(0.5)),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        alignment: Alignment.centerLeft,
      ),
      onPressed: _isLoading ? null : onTap,
      icon: Icon(icon, color: primaryColor, size: 20),
      label: Text(
        title,
        style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
      ),
    );
  }
}
