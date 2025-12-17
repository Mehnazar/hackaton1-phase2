/**
 * Footer Component
 * Footer with author info and copyright
 */

import React from "react";
import "./Footer.css";

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-left">
            <div className="footer-logo">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
              </svg>
              <span>Physical AI Humanoid Robotics Book</span>
            </div>
            <p className="footer-description">
              A comprehensive guide to building intelligent humanoid robots
            </p>
          </div>

          <div className="footer-center">
            <h4 className="footer-section-title">Quick Links</h4>
            <nav className="footer-links">
              <a href="#about" className="footer-link">About</a>
              <a href="#chapters" className="footer-link">Chapters</a>
              <a href="#resources" className="footer-link">Resources</a>
              <a href="#contact" className="footer-link">Contact</a>
            </nav>
          </div>

          <div className="footer-right">
            <h4 className="footer-section-title">Author</h4>
            <p className="footer-author">Mehnazar Umair</p>
            <p className="footer-copyright">
              © {currentYear} All rights reserved.
            </p>
          </div>
        </div>

        <div className="footer-bottom">
          <p className="footer-legal">
            This book is for educational purposes. Unauthorized reproduction or distribution is prohibited.
          </p>
        </div>
      </div>
    </footer>
  );
};
