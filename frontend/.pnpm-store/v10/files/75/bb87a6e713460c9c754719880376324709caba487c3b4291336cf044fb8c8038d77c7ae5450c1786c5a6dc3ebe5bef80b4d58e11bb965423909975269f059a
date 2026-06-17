"use client";

// src/primitives/message/MessageError.tsx
import { useAssistantState } from "../../context/index.js";
import { Fragment, jsx } from "react/jsx-runtime";
var MessagePrimitiveError = ({ children }) => {
  const hasError = useAssistantState(
    ({ message }) => message.status?.type === "incomplete" && message.status.reason === "error"
  );
  return hasError ? /* @__PURE__ */ jsx(Fragment, { children }) : null;
};
MessagePrimitiveError.displayName = "MessagePrimitive.Error";
export {
  MessagePrimitiveError
};
//# sourceMappingURL=MessageError.js.map