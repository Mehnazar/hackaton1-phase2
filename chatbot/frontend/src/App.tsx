/**
 * Main App Component
 * Landing page with introductory content, then full-screen BookReader with floating chatbot icon and popup
 */

import { useState } from "react";
import { Header } from "./components/Header";
import { LandingPage } from "./components/LandingPage";
import { BookReader } from "./components/BookReader";
import { ChatInterface } from "./components/ChatInterface";
import { useTextSelection } from "./hooks/useTextSelection";
import "./App.css";

function App() {
  const [showLanding, setShowLanding] = useState<boolean>(true);
  const [selectedText, setSelectedText] = useState<string>("");
  const [isChatOpen, setIsChatOpen] = useState(false);
  const { clearSelection } = useTextSelection();

  const handleStartReading = () => {
    setShowLanding(false);
  };

  const handleTextSelect = (text: string) => {
    setSelectedText(text);
  };

  const handleClearSelection = () => {
    setSelectedText("");
    clearSelection();
  };

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  // Show landing page first
  if (showLanding) {
    return (
      <>
        <Header showHomeButton={false} />
        <LandingPage onStartReading={handleStartReading} />

        {/* Floating Chatbot Icon on Landing Page */}
        <button
          className="chatbot-icon"
          onClick={toggleChat}
          aria-label="Toggle chatbot"
        >
          <svg
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            <line x1="9" y1="10" x2="15" y2="10"></line>
            <line x1="9" y1="14" x2="13" y2="14"></line>
          </svg>
          {isChatOpen && <span className="chatbot-icon-close">×</span>}
        </button>

        {/* Chat Popup Window */}
        {isChatOpen && (
          <div className="chat-popup">
            <div className="chat-popup-header">
              <h3>AI Assistant</h3>
              <button
                className="chat-popup-close"
                onClick={toggleChat}
                aria-label="Close chat"
              >
                ×
              </button>
            </div>
            <div className="chat-popup-body">
              <ChatInterface
                selectedText={selectedText}
                onClearSelection={handleClearSelection}
              />
            </div>
          </div>
        )}

        {/* Overlay for mobile */}
        {isChatOpen && (
          <div
            className="chat-overlay"
            onClick={toggleChat}
          ></div>
        )}
      </>
    );
  }

  return (
    <div className="app">
      {/* Header with Home Button */}
      <Header showHomeButton={true} onHomeClick={() => setShowLanding(true)} />

      {/* Full-screen Book Reader */}
      <div className="app-book-panel">
        <BookReader onTextSelect={handleTextSelect} />
      </div>

      {/* Floating Chatbot Icon */}
      <button
        className="chatbot-icon"
        onClick={toggleChat}
        aria-label="Toggle chatbot"
      >
        <svg
          width="32"
          height="32"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          <line x1="9" y1="10" x2="15" y2="10"></line>
          <line x1="9" y1="14" x2="13" y2="14"></line>
        </svg>
        {isChatOpen && <span className="chatbot-icon-close">×</span>}
      </button>

      {/* Chat Popup Window */}
      {isChatOpen && (
        <div className="chat-popup">
          <div className="chat-popup-header">
            <h3>AI Assistant</h3>
            <button
              className="chat-popup-close"
              onClick={toggleChat}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>
          <div className="chat-popup-body">
            <ChatInterface
              selectedText={selectedText}
              onClearSelection={handleClearSelection}
            />
          </div>
        </div>
      )}

      {/* Overlay for mobile */}
      {isChatOpen && (
        <div
          className="chat-overlay"
          onClick={toggleChat}
        ></div>
      )}
    </div>
  );
}

export default App;
