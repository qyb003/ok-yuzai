"use client";

// src/primitives/actionBar/ActionBarReload.tsx
import {
  createActionButton
} from "../../utils/createActionButton.js";
import { useCallback } from "react";
import { useAssistantState, useAssistantApi } from "../../context/index.js";
var useActionBarReload = () => {
  const api = useAssistantApi();
  const disabled = useAssistantState(
    (s) => s.thread.isRunning || s.thread.isDisabled || s.message.role !== "assistant"
  );
  const callback = useCallback(() => {
    api.message().reload();
  }, [api]);
  if (disabled) return null;
  return callback;
};
var ActionBarPrimitiveReload = createActionButton(
  "ActionBarPrimitive.Reload",
  useActionBarReload
);
export {
  ActionBarPrimitiveReload
};
//# sourceMappingURL=ActionBarReload.js.map