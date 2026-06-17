"use client";

// src/primitives/actionBar/useActionBarFloatStatus.tsx
import { useAssistantState } from "../../context/index.js";
var HideAndFloatStatus = /* @__PURE__ */ ((HideAndFloatStatus2) => {
  HideAndFloatStatus2["Hidden"] = "hidden";
  HideAndFloatStatus2["Floating"] = "floating";
  HideAndFloatStatus2["Normal"] = "normal";
  return HideAndFloatStatus2;
})(HideAndFloatStatus || {});
var useActionBarFloatStatus = ({
  hideWhenRunning,
  autohide,
  autohideFloat
}) => {
  return useAssistantState(({ thread, message }) => {
    if (hideWhenRunning && thread.isRunning) return "hidden" /* Hidden */;
    const autohideEnabled = autohide === "always" || autohide === "not-last" && !message.isLast;
    if (!autohideEnabled) return "normal" /* Normal */;
    if (!message.isHovering) return "hidden" /* Hidden */;
    if (autohideFloat === "always" || autohideFloat === "single-branch" && message.branchCount <= 1)
      return "floating" /* Floating */;
    return "normal" /* Normal */;
  });
};
export {
  HideAndFloatStatus,
  useActionBarFloatStatus
};
//# sourceMappingURL=useActionBarFloatStatus.js.map