"use client";

// src/primitives/thread/ThreadEmpty.tsx
import { useAssistantState } from "../../context/index.js";
var ThreadPrimitiveEmpty = ({
  children
}) => {
  const empty = useAssistantState(
    ({ thread }) => thread.messages.length === 0 && !thread.isLoading
  );
  return empty ? children : null;
};
ThreadPrimitiveEmpty.displayName = "ThreadPrimitive.Empty";
export {
  ThreadPrimitiveEmpty
};
//# sourceMappingURL=ThreadEmpty.js.map