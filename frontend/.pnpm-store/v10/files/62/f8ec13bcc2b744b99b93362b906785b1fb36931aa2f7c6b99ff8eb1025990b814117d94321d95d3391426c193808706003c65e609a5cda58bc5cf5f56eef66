"use client";

// src/primitives/branchPicker/BranchPickerPrevious.tsx
import {
  createActionButton
} from "../../utils/createActionButton.js";
import { useCallback } from "react";
import { useAssistantState, useAssistantApi } from "../../context/index.js";
var useBranchPickerPrevious = () => {
  const api = useAssistantApi();
  const disabled = useAssistantState(({ thread, message }) => {
    if (message.branchNumber <= 1) return true;
    if (thread.isRunning && !thread.capabilities.switchBranchDuringRun) {
      return true;
    }
    return false;
  });
  const callback = useCallback(() => {
    api.message().switchToBranch({ position: "previous" });
  }, [api]);
  if (disabled) return null;
  return callback;
};
var BranchPickerPrimitivePrevious = createActionButton(
  "BranchPickerPrimitive.Previous",
  useBranchPickerPrevious
);
export {
  BranchPickerPrimitivePrevious
};
//# sourceMappingURL=BranchPickerPrevious.js.map