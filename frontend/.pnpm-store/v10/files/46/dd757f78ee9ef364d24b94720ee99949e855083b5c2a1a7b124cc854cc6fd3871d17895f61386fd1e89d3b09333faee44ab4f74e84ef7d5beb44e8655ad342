"use client";

// src/primitives/messagePart/useMessagePartReasoning.tsx
import { useAssistantState } from "../../context/index.js";
var useMessagePartReasoning = () => {
  const text = useAssistantState(({ part }) => {
    if (part.type !== "reasoning")
      throw new Error(
        "MessagePartReasoning can only be used inside reasoning message parts."
      );
    return part;
  });
  return text;
};
export {
  useMessagePartReasoning
};
//# sourceMappingURL=useMessagePartReasoning.js.map