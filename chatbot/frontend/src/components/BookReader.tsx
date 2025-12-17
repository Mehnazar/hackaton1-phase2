/**
 * BookReader Component
 * Displays book content with text selection support
 */

import React, { useState, useEffect } from "react";
import type { BookChapter } from "../types";
import { apiService } from "../services/api";
import { authService } from "../services/authService";
import { useAuth } from "../contexts/AuthContext";
import { Footer } from "./Footer";
import "./BookReader.css";

interface BookReaderProps {
  onTextSelect?: (selectedText: string) => void;
}

export const BookReader: React.FC<BookReaderProps> = ({ onTextSelect }) => {
  const { isAuthenticated } = useAuth();
  const [chapters, setChapters] = useState<BookChapter[]>([]);
  const [selectedChapter, setSelectedChapter] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [personalizing, setPersonalizing] = useState(false);
  const [translating, setTranslating] = useState(false);
  const [isPersonalized, setIsPersonalized] = useState(false);
  const [isTranslated, setIsTranslated] = useState(false);

  useEffect(() => {
    loadChapters();
  }, []);

  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim() || "";
      if (text && onTextSelect) {
        onTextSelect(text);
      }
    };

    document.addEventListener("mouseup", handleSelection);

    return () => {
      document.removeEventListener("mouseup", handleSelection);
    };
  }, [onTextSelect]);

  const loadChapters = async () => {
    try {
      setLoading(true);
      const data = await apiService.loadBookChapters();
      setChapters(data);
      if (data.length > 0) {
        setSelectedChapter(data[0].id);
      }
      setError("");
    } catch (err) {
      setError("Failed to load book content");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePersonalize = async () => {
    if (!currentChapter || !isAuthenticated) return;

    try {
      setPersonalizing(true);
      const result = await authService.personalizeChapter(
        currentChapter.id,
        currentChapter.content,
        currentChapter.title
      );

      // Update chapter content with personalized version
      setChapters(prev =>
        prev.map(ch =>
          ch.id === currentChapter.id
            ? { ...ch, content: result.personalized_content }
            : ch
        )
      );
      setIsPersonalized(true);
      setIsTranslated(false);
    } catch (err: any) {
      setError(err.message || "Failed to personalize content");
    } finally {
      setPersonalizing(false);
    }
  };

  const handleTranslate = async () => {
    if (!currentChapter || !isAuthenticated) return;

    try {
      setTranslating(true);
      const result = await authService.translateChapter(
        currentChapter.id,
        currentChapter.content,
        currentChapter.title
      );

      // Update chapter content with translated version
      setChapters(prev =>
        prev.map(ch =>
          ch.id === currentChapter.id
            ? { ...ch, content: result.translated_content, title: result.translated_title }
            : ch
        )
      );
      setIsTranslated(true);
      setIsPersonalized(false);
    } catch (err: any) {
      setError(err.message || "Failed to translate content");
    } finally {
      setTranslating(false);
    }
  };

  const handleReset = async () => {
    // Reload chapters to get original content
    await loadChapters();
    setIsPersonalized(false);
    setIsTranslated(false);
  };

  const currentChapter = chapters.find((ch) => ch.id === selectedChapter);

  if (loading) {
    return (
      <div className="book-reader">
        <div className="book-reader-loading">Loading book content...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="book-reader">
        <div className="book-reader-error">{error}</div>
      </div>
    );
  }

  return (
    <div className="book-reader">
      <div className="book-reader-layout">
        {/* Left Sidebar - Table of Contents */}
        <aside className="book-sidebar">
          <div className="sidebar-header">
            <h2>Table of Contents</h2>
          </div>
          <nav className="sidebar-nav">
            {chapters.map((chapter) => (
              <div key={chapter.id} className="sidebar-chapter">
                <button
                  className={`sidebar-chapter-btn ${
                    selectedChapter === chapter.id ? "active" : ""
                  }`}
                  onClick={() => setSelectedChapter(chapter.id)}
                >
                  <span className="chapter-number">{chapter.number}</span>
                  <span className="chapter-title">{chapter.title}</span>
                </button>
                {selectedChapter === chapter.id && chapter.sections && (
                  <div className="sidebar-sections">
                    {chapter.sections.map((section) => (
                      <a
                        key={section.id}
                        href={`#${section.id}`}
                        className="sidebar-section-link"
                      >
                        {section.title}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </nav>
        </aside>

        {/* Main Content Area */}
        {currentChapter && (
          <div className="book-reader-content">
          <div className="book-reader-header-section">
            <h1 className="book-reader-chapter-title">
              Chapter {currentChapter.number}: {currentChapter.title}
            </h1>

            {/* Personalization Controls */}
            {isAuthenticated && (
              <div className="chapter-actions">
                {isPersonalized && (
                  <span className="chapter-badge personalized">
                    ✨ Personalized
                  </span>
                )}
                {isTranslated && (
                  <span className="chapter-badge translated">
                    🌐 اردو
                  </span>
                )}
                <button
                  className="chapter-action-btn personalize-btn"
                  onClick={handlePersonalize}
                  disabled={personalizing || isPersonalized}
                  title="Personalize content based on your profile"
                >
                  {personalizing ? (
                    <>⏳ Personalizing...</>
                  ) : isPersonalized ? (
                    <>✅ Personalized</>
                  ) : (
                    <>✨ Personalize for Me</>
                  )}
                </button>
                <button
                  className="chapter-action-btn translate-btn"
                  onClick={handleTranslate}
                  disabled={translating || isTranslated}
                  title="Translate to Urdu"
                >
                  {translating ? (
                    <>⏳ Translating...</>
                  ) : isTranslated ? (
                    <>✅ Translated</>
                  ) : (
                    <>🌐 Translate to Urdu</>
                  )}
                </button>
                {(isPersonalized || isTranslated) && (
                  <button
                    className="chapter-action-btn reset-btn"
                    onClick={handleReset}
                    title="Reset to original content"
                  >
                    🔄 Reset
                  </button>
                )}
              </div>
            )}
          </div>

          {currentChapter.sections && currentChapter.sections.length > 0 ? (
            currentChapter.sections.map((section) => (
              <div key={section.id} id={section.id} className="book-reader-section">
                <h2 className="book-reader-section-title">{section.title}</h2>
                <div className="book-reader-section-content">
                  {section.content.split("\n\n").map((paragraph, idx) => {
                    if (paragraph.trim().startsWith("**") && paragraph.includes(":**")) {
                      return (
                        <p key={idx} className="book-reader-paragraph">
                          <strong>{paragraph}</strong>
                        </p>
                      );
                    }
                    if (paragraph.trim().startsWith("-")) {
                      const items = paragraph.split("\n").filter((item) => item.trim());
                      return (
                        <ul key={idx} className="book-reader-list">
                          {items.map((item, itemIdx) => (
                            <li key={itemIdx}>{item.replace(/^-\s*/, "")}</li>
                          ))}
                        </ul>
                      );
                    }
                    return (
                      <p key={idx} className="book-reader-paragraph">
                        {paragraph}
                      </p>
                    );
                  })}
                </div>
              </div>
            ))
          ) : (
            <div className="book-reader-section">
              <div className="book-reader-section-content">
                <pre style={{ whiteSpace: "pre-wrap", wordWrap: "break-word" }}>
                  {currentChapter.content}
                </pre>
              </div>
            </div>
          )}

            <div className="book-reader-footer">
              <p className="book-reader-hint">
                💡 <strong>Tip:</strong> Select any text from the book and ask questions about it in the chatbot!
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <Footer />
    </div>
  );
};
