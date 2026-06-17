// src/client/Tools.ts
import { resource, tapState, tapEffect } from "@assistant-ui/tap";
import { tapApi } from "../utils/tap-store/index.js";
import { tapModelContext } from "./ModelContext.js";
var Tools = resource(({ toolkit }) => {
  const [state, setState] = tapState(() => ({
    tools: {}
  }));
  const modelContext = tapModelContext();
  tapEffect(() => {
    if (!toolkit) return;
    const unsubscribes = [];
    for (const [toolName, tool] of Object.entries(toolkit)) {
      if (tool.render) {
        unsubscribes.push(setToolUI(toolName, tool.render));
      }
    }
    const toolsWithoutRender = Object.entries(toolkit).reduce(
      (acc, [name, tool]) => {
        const { render, ...rest } = tool;
        acc[name] = rest;
        return acc;
      },
      {}
    );
    const modelContextProvider = {
      getModelContext: () => ({
        tools: toolsWithoutRender
      })
    };
    unsubscribes.push(modelContext.register(modelContextProvider));
    return () => {
      unsubscribes.forEach((fn) => fn());
    };
  }, [toolkit, modelContext]);
  const setToolUI = (toolName, render) => {
    setState((prev) => {
      return {
        ...prev,
        tools: {
          ...prev.tools,
          [toolName]: [...prev.tools[toolName] ?? [], render]
        }
      };
    });
    return () => {
      setState((prev) => {
        return {
          ...prev,
          tools: {
            ...prev.tools,
            [toolName]: prev.tools[toolName]?.filter((r) => r !== render) ?? []
          }
        };
      });
    };
  };
  return tapApi({
    getState: () => state,
    setToolUI
  });
});
export {
  Tools
};
//# sourceMappingURL=Tools.js.map