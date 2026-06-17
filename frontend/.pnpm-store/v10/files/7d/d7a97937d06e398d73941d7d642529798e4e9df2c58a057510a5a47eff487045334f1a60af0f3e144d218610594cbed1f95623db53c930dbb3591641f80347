"use client";

// src/legacy-runtime/hooks/MessagePartContext.ts
import { createStateHookForRuntime } from "../../context/react/utils/createStateHookForRuntime.js";
import { useAssistantApi, useAssistantState } from "../../context/react/index.js";
function useMessagePartRuntime(options) {
  const api = useAssistantApi();
  const runtime = useAssistantState(
    () => api.part.source ? api.part().__internal_getRuntime?.() ?? null : null
  );
  if (!runtime && !options?.optional) {
    throw new Error("MessagePartRuntime is not available");
  }
  return runtime;
}
var useMessagePart = createStateHookForRuntime(useMessagePartRuntime);
export {
  useMessagePart,
  useMessagePartRuntime
};
//# sourceMappingURL=MessagePartContext.js.map