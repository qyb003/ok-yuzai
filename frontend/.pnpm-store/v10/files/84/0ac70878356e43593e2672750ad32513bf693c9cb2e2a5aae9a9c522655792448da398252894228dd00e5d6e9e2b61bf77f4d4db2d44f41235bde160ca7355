"use client";

// src/primitives/messagePart/useMessagePartSource.tsx
import { useAssistantState } from "../../context/index.js";
var useMessagePartSource = () => {
  const source = useAssistantState(({ part }) => {
    if (part.type !== "source")
      throw new Error(
        "MessagePartSource can only be used inside source message parts."
      );
    return part;
  });
  return source;
};
export {
  useMessagePartSource
};
//# sourceMappingURL=useMessagePartSource.js.map