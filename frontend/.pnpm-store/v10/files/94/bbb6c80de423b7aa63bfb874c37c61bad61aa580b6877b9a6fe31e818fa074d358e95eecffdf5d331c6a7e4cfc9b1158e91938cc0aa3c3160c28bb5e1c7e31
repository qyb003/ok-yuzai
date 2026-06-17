"use client";

// src/model-context/useAssistantToolUI.tsx
import { useEffect } from "react";
import { useAssistantApi } from "../context/react/AssistantApiContext.js";
var useAssistantToolUI = (tool) => {
  const api = useAssistantApi();
  useEffect(() => {
    if (!tool?.toolName || !tool?.render) return void 0;
    return api.tools().setToolUI(tool.toolName, tool.render);
  }, [api, tool?.toolName, tool?.render]);
};
export {
  useAssistantToolUI
};
//# sourceMappingURL=useAssistantToolUI.js.map