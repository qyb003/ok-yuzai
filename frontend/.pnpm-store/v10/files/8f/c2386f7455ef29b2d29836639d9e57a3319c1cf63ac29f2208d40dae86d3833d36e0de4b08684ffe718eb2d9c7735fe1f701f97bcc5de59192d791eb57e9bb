"use client";

// src/primitives/messagePart/useMessagePartImage.tsx
import { useAssistantState } from "../../context/index.js";
var useMessagePartImage = () => {
  const image = useAssistantState(({ part }) => {
    if (part.type !== "image")
      throw new Error(
        "MessagePartImage can only be used inside image message parts."
      );
    return part;
  });
  return image;
};
export {
  useMessagePartImage
};
//# sourceMappingURL=useMessagePartImage.js.map