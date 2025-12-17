/**
 * Header Component
 * Navigation header with home, search, and auth options
 */

import React, { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { SigninModal } from "./SigninModal";
import { SignupModal } from "./SignupModal";
import "./Header.css";

interface HeaderProps {
  onHomeClick?: () => void;
  showHomeButton?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onHomeClick, showHomeButton = false }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [showSignin, setShowSignin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const { user, isAuthenticated, signout } = useAuth();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement search functionality
    console.log("Searching for:", searchQuery);
  };

  const handleSignout = async () => {
    await signout();
    setShowUserMenu(false);
  };

  return (
    <>
      <header className="app-header">
        <div className="header-container">
          {/* Left Section - Home + Book Name */}
          <div className="header-left">
            {showHomeButton && (
              <button className="header-home-btn" onClick={onHomeClick}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                  <polyline points="9 22 9 12 15 12 15 22"></polyline>
                </svg>
                <span>Home</span>
              </button>
            )}
            <div className="header-divider"></div>
            <div className="header-logo">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
              </svg>
              <span className="header-logo-text">Physical AI Humanoid Robotics</span>
            </div>
          </div>

          {/* Center Section - Search Bar */}
          <div className="header-center">
            <form className="header-search" onSubmit={handleSearch}>
              <svg className="header-search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
              <input
                type="text"
                className="header-search-input"
                placeholder="Search the book..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </form>
          </div>

          {/* Right Section - Auth Buttons or User Menu */}
          <div className="header-right">
            {isAuthenticated ? (
              <div className="header-user-menu">
                <button
                  className="header-user-btn"
                  onClick={() => setShowUserMenu(!showUserMenu)}
                >
                  <div className="header-user-avatar">
                    {user?.name?.charAt(0).toUpperCase()}
                  </div>
                  <span className="header-user-name">{user?.name}</span>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </button>
                {showUserMenu && (
                  <div className="header-dropdown">
                    <div className="header-dropdown-item header-user-info">
                      <div className="header-user-email">{user?.email}</div>
                    </div>
                    <div className="header-dropdown-divider"></div>
                    <button className="header-dropdown-item" onClick={handleSignout}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                        <polyline points="16 17 21 12 16 7"></polyline>
                        <line x1="21" y1="12" x2="9" y2="12"></line>
                      </svg>
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <button
                  className="header-btn header-signin-btn"
                  onClick={() => setShowSignin(true)}
                >
                  Sign In
                </button>
                <button
                  className="header-btn header-signup-btn"
                  onClick={() => setShowSignup(true)}
                >
                  Sign Up
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Auth Modals */}
      <SigninModal
        isOpen={showSignin}
        onClose={() => setShowSignin(false)}
        onSwitchToSignup={() => {
          setShowSignin(false);
          setShowSignup(true);
        }}
      />
      <SignupModal
        isOpen={showSignup}
        onClose={() => setShowSignup(false)}
        onSwitchToSignin={() => {
          setShowSignup(false);
          setShowSignin(true);
        }}
      />
    </>
  );
};
