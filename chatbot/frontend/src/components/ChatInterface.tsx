/**
 * ChatInterface Component
 * Chatbot interface with message history and query modes
 */

import React, { useState, useRef, useEffect } from "react";
import type { ChatMessage, QueryMode, Source } from "../types";
import { apiService } from "../services/api";
import "./ChatInterface.css";

interface ChatInterfaceProps {
  selectedText?: string;
  onClearSelection?: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  selectedText,
  onClearSelection,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [queryMode, setQueryMode] = useState<QueryMode>("book-wide" as QueryMode);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (selectedText && selectedText.length > 0) {
      setQueryMode("selected-text" as QueryMode);
    }
  }, [selectedText]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date(),
      mode: queryMode,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await apiService.chat({
        query: inputValue,
        mode: queryMode,
        context: queryMode === "selected-text" ? selectedText : undefined,
      });

      const assistantMessage: ChatMessage = {
        id: response.query_id,
        role: "assistant",
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
        refused: response.refused,
        confidence: response.confidence,
        mode: response.mode,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (queryMode === "selected-text" && onClearSelection) {
        onClearSelection();
        setQueryMode("book-wide" as QueryMode);
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        role: "assistant",
        content: `Error: ${error instanceof Error ? error.message : "Failed to get response"}`,
        timestamp: new Date(),
        refused: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderSource = (source: Source, index: number) => (
    <div key={index} className="chat-source">
      <div className="chat-source-header">
        <span className="chat-source-id">[{source.passage_id}]</span>
        <span className="chat-source-chapter">{source.chapter}</span>
      </div>
      <div className="chat-source-section">{source.section}</div>
      <div className="chat-source-snippet">"{source.snippet}"</div>
    </div>
  );

  const renderMessage = (message: ChatMessage) => (
    <div key={message.id} className={`chat-message chat-message-${message.role}`}>
      <div className="chat-message-header">
        <span className="chat-message-role">
          {message.role === "user" ? "You" : "AI Assistant"}
        </span>
        <span className="chat-message-time">
          {message.timestamp.toLocaleTimeString()}
        </span>
      </div>
      <div className="chat-message-content">{message.content}</div>
      {message.mode && (
        <div className="chat-message-mode">
          Mode: {message.mode === "selected-text" ? "Selected Text" : "Book-Wide Search"}
        </div>
      )}
      {message.confidence !== undefined && (
        <div className="chat-message-confidence">
          Confidence: {(message.confidence * 100).toFixed(0)}%
        </div>
      )}
      {message.sources && message.sources.length > 0 && (
        <div className="chat-sources">
          <div className="chat-sources-header">Sources:</div>
          {message.sources.map((source, idx) => renderSource(source, idx))}
        </div>
      )}
    </div>
  );

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2 className="chat-title">RAG Chatbot</h2>
        <p className="chat-subtitle">Ask questions about the book</p>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <h3>Welcome! 👋</h3>
            <p>Ask me anything about the AI-Native Software Development book.</p>
            <ul>
              <li>Select text from the book and ask specific questions</li>
              <li>Or search across the entire book for answers</li>
            </ul>
          </div>
        )}
        {messages.map(renderMessage)}
        {isLoading && (
          <div className="chat-message chat-message-assistant">
            <div className="chat-message-header">
              <span className="chat-message-role">AI Assistant</span>
            </div>
            <div className="chat-message-loading">
              <span className="chat-dot"></span>
              <span className="chat-dot"></span>
              <span className="chat-dot"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {selectedText && selectedText.length > 0 && (
        <div className="chat-selected-text">
          <div className="chat-selected-text-header">
            <span>Selected Text ({selectedText.length} chars)</span>
            <button
              onClick={onClearSelection}
              className="chat-clear-button"
              type="button"
            >
              Clear
            </button>
          </div>
          <div className="chat-selected-text-content">
            {selectedText.substring(0, 200)}
            {selectedText.length > 200 && "..."}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="chat-input-form">
        <div className="chat-mode-selector">
          <label>
            <input
              type="radio"
              value="book-wide"
              checked={queryMode === "book-wide"}
              onChange={(e) => setQueryMode(e.target.value as QueryMode)}
              disabled={!!selectedText}
            />
            Book-Wide Search
          </label>
          <label>
            <input
              type="radio"
              value="selected-text"
              checked={queryMode === "selected-text"}
              onChange={(e) => setQueryMode(e.target.value as QueryMode)}
              disabled={!selectedText}
            />
            Selected Text Only
          </label>
        </div>
        <div className="chat-input-container">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your question here..."
            className="chat-input"
            disabled={isLoading}
          />
          <button type="submit" className="chat-submit" disabled={isLoading || !inputValue.trim()}>
            {isLoading ? "..." : "Send"}
          </button>
        </div>
      </form>
    </div>
  );
};
