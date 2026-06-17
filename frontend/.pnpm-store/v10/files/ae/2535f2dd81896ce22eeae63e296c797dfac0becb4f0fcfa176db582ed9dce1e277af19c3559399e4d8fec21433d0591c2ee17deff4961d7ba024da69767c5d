"use client";

// src/primitives/thread/ThreadIf.tsx
import { useAssistantState } from "../../context/index.js";
var useThreadIf = (props) => {
  return useAssistantState(({ thread }) => {
    const isEmpty = thread.messages.length === 0 && !thread.isLoading;
    if (props.empty === true && !isEmpty) return false;
    if (props.empty === false && isEmpty) return false;
    if (props.running === true && !thread.isRunning) return false;
    if (props.running === false && thread.isRunning) return false;
    if (props.disabled === true && !thread.isDisabled) return false;
    if (props.disabled === false && thread.isDisabled) return false;
    return true;
  });
};
var ThreadPrimitiveIf = ({
  children,
  ...query
}) => {
  const result = useThreadIf(query);
  return result ? children : null;
};
ThreadPrimitiveIf.displayName = "ThreadPrimitive.If";
export {
  ThreadPrimitiveIf
};
//# sourceMappingURL=ThreadIf.js.map