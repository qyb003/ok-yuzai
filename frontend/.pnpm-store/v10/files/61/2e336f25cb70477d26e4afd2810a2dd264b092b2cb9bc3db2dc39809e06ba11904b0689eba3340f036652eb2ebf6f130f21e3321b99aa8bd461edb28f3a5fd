"use client";

// src/primitives/messagePart/useMessagePartText.tsx
import { useAssistantState } from "../../context/index.js";
var useMessagePartText = () => {
  const text = useAssistantState(({ part }) => {
    if (part.type !== "text" && part.type !== "reasoning")
      throw new Error(
        "MessagePartText can only be used inside text or reasoning message parts."
      );
    return part;
  });
  return text;
};
export {
  useMessagePartText
};
//# sourceMappingURL=useMessagePartText.js.map