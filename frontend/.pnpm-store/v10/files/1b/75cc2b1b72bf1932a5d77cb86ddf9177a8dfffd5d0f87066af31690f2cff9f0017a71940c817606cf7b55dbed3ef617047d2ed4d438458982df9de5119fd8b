"use client";

// src/primitives/actionBar/ActionBarSpeak.tsx
import { useCallback } from "react";
import { useAssistantState, useAssistantApi } from "../../context/index.js";
import {
  createActionButton
} from "../../utils/createActionButton.js";
var useActionBarSpeak = () => {
  const api = useAssistantApi();
  const callback = useCallback(async () => {
    api.message().speak();
  }, [api]);
  const hasSpeakableContent = useAssistantState(({ message }) => {
    return (message.role !== "assistant" || message.status?.type !== "running") && message.parts.some((c) => c.type === "text" && c.text.length > 0);
  });
  if (!hasSpeakableContent) return null;
  return callback;
};
var ActionBarPrimitiveSpeak = createActionButton(
  "ActionBarPrimitive.Speak",
  useActionBarSpeak
);
export {
  ActionBarPrimitiveSpeak
};
//# sourceMappingURL=ActionBarSpeak.js.map