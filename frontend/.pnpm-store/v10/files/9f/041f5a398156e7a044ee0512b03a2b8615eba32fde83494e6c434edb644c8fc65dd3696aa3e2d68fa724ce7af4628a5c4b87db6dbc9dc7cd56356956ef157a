"use client";

// src/primitives/actionBar/ActionBarEdit.tsx
import {
  createActionButton
} from "../../utils/createActionButton.js";
import { useCallback } from "react";
import { useAssistantState, useAssistantApi } from "../../context/index.js";
var useActionBarEdit = () => {
  const api = useAssistantApi();
  const disabled = useAssistantState(({ composer }) => composer.isEditing);
  const callback = useCallback(() => {
    api.composer().beginEdit();
  }, [api]);
  if (disabled) return null;
  return callback;
};
var ActionBarPrimitiveEdit = createActionButton(
  "ActionBarPrimitive.Edit",
  useActionBarEdit
);
export {
  ActionBarPrimitiveEdit
};
//# sourceMappingURL=ActionBarEdit.js.map