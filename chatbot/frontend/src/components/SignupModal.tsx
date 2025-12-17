/**
 * Signup Modal Component
 * Multi-step signup with profile questions
 */

import React, { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import "./AuthModals.css";

interface SignupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToSignin: () => void;
}

type Step = 1 | 2 | 3;

export const SignupModal: React.FC<SignupModalProps> = ({
  isOpen,
  onClose,
  onSwitchToSignin,
}) => {
  const { signup } = useAuth();
  const [step, setStep] = useState<Step>(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    software_background: "" as "beginner" | "intermediate" | "advanced" | "",
    hardware_background: "" as "low-end" | "mid-range" | "high-end" | "",
  });

  if (!isOpen) return null;

  const handleNext = () => {
    setError("");

    if (step === 1) {
      if (!formData.name || !formData.email || !formData.password) {
        setError("Please fill in all fields");
        return;
      }
      if (formData.password.length < 8) {
        setError("Password must be at least 8 characters");
        return;
      }
      if (formData.password !== formData.confirmPassword) {
        setError("Passwords do not match");
        return;
      }
      setStep(2);
    } else if (step === 2) {
      if (!formData.software_background) {
        setError("Please select your software background");
        return;
      }
      setStep(3);
    }
  };

  const handleSubmit = async () => {
    if (!formData.hardware_background) {
      setError("Please select your hardware background");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await signup({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        software_background: formData.software_background,
        hardware_background: formData.hardware_background,
      });
      onClose();
    } catch (err: any) {
      setError(err.message || "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        <button className="auth-modal-close" onClick={onClose}>
          ✕
        </button>

        <div className="auth-modal-header">
          <h2>Create Account</h2>
          <div className="auth-steps">
            <div className={`auth-step ${step >= 1 ? "active" : ""}`}>1</div>
            <div className="auth-step-line"></div>
            <div className={`auth-step ${step >= 2 ? "active" : ""}`}>2</div>
            <div className="auth-step-line"></div>
            <div className={`auth-step ${step >= 3 ? "active" : ""}`}>3</div>
          </div>
        </div>

        <div className="auth-modal-body">
          {error && <div className="auth-error">{error}</div>}

          {/* Step 1: Basic Info */}
          {step === 1 && (
            <div className="auth-form">
              <h3>Basic Information</h3>
              <div className="auth-form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="Enter your name"
                />
              </div>

              <div className="auth-form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  placeholder="you@example.com"
                />
              </div>

              <div className="auth-form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) =>
                    setFormData({ ...formData, password: e.target.value })
                  }
                  placeholder="Min 8 characters"
                />
              </div>

              <div className="auth-form-group">
                <label>Confirm Password</label>
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) =>
                    setFormData({ ...formData, confirmPassword: e.target.value })
                  }
                  placeholder="Re-enter password"
                />
              </div>

              <button className="auth-btn auth-btn-primary" onClick={handleNext}>
                Next: Software Background
              </button>
            </div>
          )}

          {/* Step 2: Software Background */}
          {step === 2 && (
            <div className="auth-form">
              <h3>Software Background</h3>
              <p className="auth-form-description">
                Help us personalize your learning experience
              </p>

              <div className="auth-options">
                <div
                  className={`auth-option ${
                    formData.software_background === "beginner" ? "selected" : ""
                  }`}
                  onClick={() =>
                    setFormData({ ...formData, software_background: "beginner" })
                  }
                >
                  <div className="auth-option-icon">🌱</div>
                  <h4>Beginner</h4>
                  <p>New to programming or robotics</p>
                </div>

                <div
                  className={`auth-option ${
                    formData.software_background === "intermediate" ? "selected" : ""
                  }`}
                  onClick={() =>
                    setFormData({
                      ...formData,
                      software_background: "intermediate",
                    })
                  }
                >
                  <div className="auth-option-icon">📚</div>
                  <h4>Intermediate</h4>
                  <p>Familiar with Python and basic concepts</p>
                </div>

                <div
                  className={`auth-option ${
                    formData.software_background === "advanced" ? "selected" : ""
                  }`}
                  onClick={() =>
                    setFormData({ ...formData, software_background: "advanced" })
                  }
                >
                  <div className="auth-option-icon">🚀</div>
                  <h4>Advanced</h4>
                  <p>Experienced developer ready for deep dives</p>
                </div>
              </div>

              <div className="auth-form-actions">
                <button
                  className="auth-btn auth-btn-secondary"
                  onClick={() => setStep(1)}
                >
                  Back
                </button>
                <button className="auth-btn auth-btn-primary" onClick={handleNext}>
                  Next: Hardware Setup
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Hardware Background */}
          {step === 3 && (
            <div className="auth-form">
              <h3>Hardware Setup</h3>
              <p className="auth-form-description">
                We'll optimize content for your hardware
              </p>

              <div className="auth-options">
                <div
                  className={`auth-option ${
                    formData.hardware_background === "low-end" ? "selected" : ""
                  }`}
                  onClick={() =>
                    setFormData({ ...formData, hardware_background: "low-end" })
                  }
                >
                  <div className="auth-option-icon">💻</div>
                  <h4>Low-End</h4>
                  <p>Basic laptop, no GPU</p>
                </div>

                <div
                  className={`auth-option ${
                    formData.hardware_background === "mid-range" ? "selected" : ""
                  }`}
                  onClick={() =>
                    setFormData({ ...formData, hardware_background: "mid-range" })
                  }
                >
                  <div className="auth-option-icon">⚡</div>
                  <h4>Mid-Range</h4>
                  <p>Decent CPU + GPU, 8-16GB RAM</p>
                </div>

                <div
                  className={`auth-option ${
                    formData.hardware_background === "high-end" ? "selected" : ""
                  }`}
                  onClick={() =>
                    setFormData({ ...formData, hardware_background: "high-end" })
                  }
                >
                  <div className="auth-option-icon">🔥</div>
                  <h4>High-End</h4>
                  <p>Powerful workstation, RTX GPU</p>
                </div>
              </div>

              <div className="auth-form-actions">
                <button
                  className="auth-btn auth-btn-secondary"
                  onClick={() => setStep(2)}
                >
                  Back
                </button>
                <button
                  className="auth-btn auth-btn-primary"
                  onClick={handleSubmit}
                  disabled={loading}
                >
                  {loading ? "Creating Account..." : "Complete Signup"}
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="auth-modal-footer">
          Already have an account?{" "}
          <button className="auth-link" onClick={onSwitchToSignin}>
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
};
