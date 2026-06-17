"use client";

// src/primitives/branchPicker/BranchPickerCount.tsx
import { useAssistantState } from "../../context/index.js";
import { Fragment, jsx } from "react/jsx-runtime";
var useBranchPickerCount = () => {
  const branchCount = useAssistantState(({ message }) => message.branchCount);
  return branchCount;
};
var BranchPickerPrimitiveCount = () => {
  const branchCount = useBranchPickerCount();
  return /* @__PURE__ */ jsx(Fragment, { children: branchCount });
};
BranchPickerPrimitiveCount.displayName = "BranchPickerPrimitive.Count";
export {
  BranchPickerPrimitiveCount
};
//# sourceMappingURL=BranchPickerCount.js.map