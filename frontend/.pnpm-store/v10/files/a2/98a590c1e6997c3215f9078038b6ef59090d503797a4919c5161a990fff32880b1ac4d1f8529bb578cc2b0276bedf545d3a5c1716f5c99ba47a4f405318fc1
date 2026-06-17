"use client";

// src/legacy-runtime/hooks/AssistantContext.ts
import { useAssistantApi } from "../../context/react/AssistantApiContext.js";
import { createStateHookForRuntime } from "../../context/react/utils/createStateHookForRuntime.js";
function useAssistantRuntime(options) {
  const api = useAssistantApi();
  const runtime = api.threads().__internal_getAssistantRuntime?.() ?? null;
  if (!runtime && !options?.optional) {
    throw new Error("AssistantRuntime is not available");
  }
  return runtime;
}
var useThreadListRuntime = (opt) => useAssistantRuntime(opt)?.threads ?? null;
var useThreadList = createStateHookForRuntime(useThreadListRuntime);
export {
  useAssistantRuntime,
  useThreadList
};
//# sourceMappingURL=AssistantContext.js.map