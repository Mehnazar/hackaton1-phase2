/**
 * API Service for RAG Chatbot Backend
 */

import type { ChatRequest, ChatResponse, BookChapter } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

class APIService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Send a chat request to the backend
   */
  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.baseURL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to get response from chatbot");
    }

    return response.json();
  }

  /**
   * Get health status
   */
  async health(): Promise<{ status: string; qdrant_status: string }> {
    const response = await fetch(`${this.baseURL}/health`);

    if (!response.ok) {
      throw new Error("Health check failed");
    }

    return response.json();
  }

  /**
   * Load book chapters from backend
   */
  async loadBookChapters(): Promise<BookChapter[]> {
    const response = await fetch(`${this.baseURL}/book/chapters`);

    if (!response.ok) {
      throw new Error("Failed to load book chapters");
    }

    const backendChapters = await response.json();

    // Convert backend format to frontend format with sections
    return backendChapters.map((chapter: any) => {
      const sections = this.parseMarkdownSections(chapter.content);

      return {
        id: chapter.id,
        number: chapter.number,
        title: chapter.title,
        content: chapter.content,
        sections: sections,
      };
    });
  }

  /**
   * Parse markdown content into sections
   */
  private parseMarkdownSections(content: string): any[] {
    const sections: any[] = [];
    const lines = content.split("\n");

    let currentSection: any = null;
    let currentContent: string[] = [];
    let inFrontmatter = false;
    let frontmatterCount = 0;

    for (const line of lines) {
      // Handle frontmatter (skip content between --- delimiters)
      if (line.trim() === "---") {
        frontmatterCount++;
        if (frontmatterCount <= 2) {
          inFrontmatter = frontmatterCount === 1;
          continue;
        }
      }

      if (inFrontmatter) {
        continue;
      }

      // Check for section header (## but not ###)
      const sectionMatch = line.match(/^##\s+(.+)$/);
      if (sectionMatch && !line.startsWith("###")) {
        // Save previous section if exists
        if (currentSection) {
          currentSection.content = currentContent.join("\n").trim();
          if (currentSection.content) {
            sections.push(currentSection);
          }
        }

        // Start new section
        const title = sectionMatch[1].trim();
        currentSection = {
          id: `section-${sections.length + 1}`,
          title: title,
          content: "",
        };
        currentContent = [];
      } else if (currentSection) {
        currentContent.push(line);
      } else if (!line.startsWith("#")) {
        // Collect content before first section (introduction)
        currentContent.push(line);
      }
    }

    // Save last section
    if (currentSection) {
      currentSection.content = currentContent.join("\n").trim();
      if (currentSection.content) {
        sections.push(currentSection);
      }
    }

    // If no sections found, create a default section with all content
    if (sections.length === 0) {
      // Remove frontmatter and main title
      const contentWithoutFrontmatter = content
        .split("\n")
        .filter((line, idx, arr) => {
          const dashCount = arr.filter((l) => l.trim() === "---").length;
          if (dashCount >= 2) {
            const firstDash = arr.indexOf("---");
            const secondDash = arr.indexOf("---", firstDash + 1);
            return idx < firstDash || idx > secondDash;
          }
          return true;
        })
        .filter((line) => !line.match(/^#\s+/)) // Remove main title
        .join("\n")
        .trim();

      sections.push({
        id: "section-1",
        title: "Content",
        content: contentWithoutFrontmatter || content,
      });
    }

    return sections;
  }
}

export const apiService = new APIService();
