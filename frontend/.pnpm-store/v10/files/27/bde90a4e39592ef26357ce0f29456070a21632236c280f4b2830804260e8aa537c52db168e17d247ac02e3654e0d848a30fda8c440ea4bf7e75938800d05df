"use client";

// src/primitives/messagePart/useMessagePartFile.tsx
import { useAssistantState } from "../../context/index.js";
var useMessagePartFile = () => {
  const file = useAssistantState(({ part }) => {
    if (part.type !== "file")
      throw new Error(
        "MessagePartFile can only be used inside file message parts."
      );
    return part;
  });
  return file;
};
export {
  useMessagePartFile
};
//# sourceMappingURL=useMessagePartFile.js.map