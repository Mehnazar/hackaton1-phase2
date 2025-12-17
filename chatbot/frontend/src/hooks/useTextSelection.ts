/**
 * Custom hook for managing text selection
 */

import { useState, useEffect, useCallback } from "react";

export function useTextSelection() {
  const [selectedText, setSelectedText] = useState<string>("");

  const handleSelectionChange = useCallback(() => {
    const selection = window.getSelection();
    const text = selection?.toString().trim() || "";
    setSelectedText(text);
  }, []);

  useEffect(() => {
    document.addEventListener("selectionchange", handleSelectionChange);

    return () => {
      document.removeEventListener("selectionchange", handleSelectionChange);
    };
  }, [handleSelectionChange]);

  const clearSelection = useCallback(() => {
    setSelectedText("");
    window.getSelection()?.removeAllRanges();
  }, []);

  return {
    selectedText,
    clearSelection,
    hasSelection: selectedText.length > 0,
  };
}
