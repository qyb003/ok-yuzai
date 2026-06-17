"use client";

// src/primitives/composer/ComposerSend.tsx
import {
  createActionButton
} from "../../utils/createActionButton.js";
import { useCallback } from "react";
import { useAssistantState, useAssistantApi } from "../../context/index.js";
var useComposerSend = () => {
  const api = useAssistantApi();
  const disabled = useAssistantState(
    (s) => s.thread.isRunning || !s.composer.isEditing || s.composer.isEmpty
  );
  const callback = useCallback(() => {
    api.composer().send();
  }, [api]);
  if (disabled) return null;
  return callback;
};
var ComposerPrimitiveSend = createActionButton(
  "ComposerPrimitive.Send",
  useComposerSend
);
export {
  ComposerPrimitiveSend,
  useComposerSend
};
//# sourceMappingURL=ComposerSend.js.map