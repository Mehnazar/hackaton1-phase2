/**
 * Landing Page Component
 * Introductory page for the Physical AI Humanoid Robotics Book
 */

import React from "react";
import "./LandingPage.css";

interface LandingPageProps {
  onStartReading: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onStartReading }) => {
  const currentYear = new Date().getFullYear();

  return (
    <div className="landing-page">
      <div className="landing-container">
        <div className="landing-header">
          <div className="landing-icon">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
            </svg>
          </div>
          <h1 className="landing-title">
            PHYSICAL AI
            <br />
            HUMANOID ROBOTICS
            <br />
            <span className="landing-title-highlight">BOOK</span>
          </h1>
        </div>

        <div className="landing-content">
          <div className="landing-description">
            <p className="landing-intro">
              A comprehensive guide to understanding and building intelligent humanoid robots
              using ROS 2, modern AI techniques, and physical computing principles.
            </p>

            <div className="landing-features">
              <div className="feature-item">
                <div className="feature-icon">📚</div>
                <div className="feature-text">
                  <h3>Comprehensive Coverage</h3>
                  <p>From fundamentals to advanced robotics concepts</p>
                </div>
              </div>
              <div className="feature-item">
                <div className="feature-icon">🤖</div>
                <div className="feature-text">
                  <h3>Hands-on Projects</h3>
                  <p>Build real-world humanoid robotics applications</p>
                </div>
              </div>
              <div className="feature-item">
                <div className="feature-icon">💡</div>
                <div className="feature-text">
                  <h3>AI-Powered Assistant</h3>
                  <p>Interactive chatbot to help you learn faster</p>
                </div>
              </div>
            </div>
          </div>

          <button className="start-reading-btn" onClick={onStartReading}>
            <span>Start Reading</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M12 5l7 7-7 7"></path>
            </svg>
          </button>

          <div className="landing-footer">
            <div className="author-info">
              <p className="author-label">Author</p>
              <p className="author-name">Mehnazar Umair</p>
            </div>
            <div className="copyright-info">
              <p>© {currentYear} Mehnazar Umair. All rights reserved.</p>
              <p className="copyright-note">
                This book is for educational purposes. Unauthorized reproduction or distribution is prohibited.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
