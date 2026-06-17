"use client";

// src/primitives/messagePart/MessagePartInProgress.tsx
import { useAssistantState } from "../../context/index.js";
var MessagePartPrimitiveInProgress = ({ children }) => {
  const isInProgress = useAssistantState(
    ({ part }) => part.status.type === "running"
  );
  return isInProgress ? children : null;
};
MessagePartPrimitiveInProgress.displayName = "MessagePartPrimitive.InProgress";
export {
  MessagePartPrimitiveInProgress
};
//# sourceMappingURL=MessagePartInProgress.js.map