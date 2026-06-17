"use client";

// src/primitives/messagePart/useMessagePartData.tsx
import { useAssistantState } from "../../context/index.js";
var useMessagePartData = (name) => {
  const part = useAssistantState(({ part: part2 }) => {
    if (part2.type !== "data") {
      return null;
    }
    return part2;
  });
  if (!part) {
    return null;
  }
  if (name && part.name !== name) {
    return null;
  }
  return part;
};
export {
  useMessagePartData
};
//# sourceMappingURL=useMessagePartData.js.map