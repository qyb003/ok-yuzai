"use client";

// src/primitives/composer/ComposerCancel.tsx
import {
  createActionButton
} from "../../utils/createActionButton.js";
import { useCallback } from "react";
import { useAssistantState, useAssistantApi } from "../../context/index.js";
var useComposerCancel = () => {
  const api = useAssistantApi();
  const disabled = useAssistantState(({ composer }) => !composer.canCancel);
  const callback = useCallback(() => {
    api.composer().cancel();
  }, [api]);
  if (disabled) return null;
  return callback;
};
var ComposerPrimitiveCancel = createActionButton(
  "ComposerPrimitive.Cancel",
  useComposerCancel
);
export {
  ComposerPrimitiveCancel
};
//# sourceMappingURL=ComposerCancel.js.map