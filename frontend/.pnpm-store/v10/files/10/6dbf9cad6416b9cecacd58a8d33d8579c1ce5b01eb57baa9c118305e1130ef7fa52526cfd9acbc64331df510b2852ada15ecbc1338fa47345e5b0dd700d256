"use client";

// src/model-context/useAssistantInstructions.tsx
import { useEffect } from "react";
import { useAssistantApi } from "../context/react/AssistantApiContext.js";
var getInstructions = (instruction) => {
  if (typeof instruction === "string") return { instruction };
  return instruction;
};
var useAssistantInstructions = (config) => {
  const { instruction, disabled = false } = getInstructions(config);
  const api = useAssistantApi();
  useEffect(() => {
    if (disabled) return;
    const config2 = {
      system: instruction
    };
    return api.modelContext().register({
      getModelContext: () => config2
    });
  }, [api, instruction, disabled]);
};
export {
  useAssistantInstructions
};
//# sourceMappingURL=useAssistantInstructions.js.map