"use client";

// src/primitives/branchPicker/BranchPickerNext.tsx
import {
  createActionButton
} from "../../utils/createActionButton.js";
import { useCallback } from "react";
import { useAssistantState, useAssistantApi } from "../../context/index.js";
var useBranchPickerNext = () => {
  const api = useAssistantApi();
  const disabled = useAssistantState(({ thread, message }) => {
    if (message.branchNumber >= message.branchCount) return true;
    if (thread.isRunning && !thread.capabilities.switchBranchDuringRun) {
      return true;
    }
    return false;
  });
  const callback = useCallback(() => {
    api.message().switchToBranch({ position: "next" });
  }, [api]);
  if (disabled) return null;
  return callback;
};
var BranchPickerPrimitiveNext = createActionButton(
  "BranchPickerPrimitive.Next",
  useBranchPickerNext
);
export {
  BranchPickerPrimitiveNext
};
//# sourceMappingURL=BranchPickerNext.js.map