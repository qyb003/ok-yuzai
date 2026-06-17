// src/legacy-runtime/runtime-cores/assistant-transport/utils.ts
import { z } from "zod";
var toAISDKTools = (tools) => {
  return Object.fromEntries(
    Object.entries(tools).map(([name, tool]) => [
      name,
      {
        ...tool.description ? { description: tool.description } : void 0,
        parameters: tool.parameters instanceof z.ZodType ? z.toJSONSchema(tool.parameters) : tool.parameters
      }
    ])
  );
};
var getEnabledTools = (tools) => {
  return Object.fromEntries(
    Object.entries(tools).filter(
      ([, tool]) => !tool.disabled && tool.type !== "backend"
    )
  );
};
var createRequestHeaders = async (headersValue) => {
  const resolvedHeaders = typeof headersValue === "function" ? await headersValue() : headersValue;
  const headers = new Headers(resolvedHeaders);
  headers.set("Content-Type", "application/json");
  return headers;
};
export {
  createRequestHeaders,
  getEnabledTools,
  toAISDKTools
};
//# sourceMappingURL=utils.js.map