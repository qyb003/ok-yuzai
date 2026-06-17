"use client";

// src/model-context/useAssistantTool.tsx
import { useEffect } from "react";
import { useAssistantApi } from "../context/react/AssistantApiContext.js";
var useAssistantTool = (tool) => {
  const api = useAssistantApi();
  useEffect(() => {
    if (!tool.render) return void 0;
    return api.tools().setToolUI(tool.toolName, tool.render);
  }, [api, tool.toolName, tool.render]);
  useEffect(() => {
    const { toolName, render, ...rest } = tool;
    const context = {
      tools: {
        [toolName]: rest
      }
    };
    return api.modelContext().register({
      getModelContext: () => context
    });
  }, [api, tool]);
};
export {
  useAssistantTool
};
//# sourceMappingURL=useAssistantTool.js.map