"use client";

// src/legacy-runtime/hooks/MessageContext.ts
import { useAssistantApi, useAssistantState } from "../../context/react/index.js";
import { createStateHookForRuntime } from "../../context/react/utils/createStateHookForRuntime.js";
function useMessageRuntime(options) {
  const api = useAssistantApi();
  const runtime = useAssistantState(
    () => api.message.source ? api.message().__internal_getRuntime?.() ?? null : null
  );
  if (!runtime && !options?.optional) {
    throw new Error("MessageRuntime is not available");
  }
  return runtime;
}
var useMessage = createStateHookForRuntime(useMessageRuntime);
var useEditComposerRuntime = (opt) => useMessageRuntime(opt)?.composer ?? null;
var useEditComposer = createStateHookForRuntime(
  useEditComposerRuntime
);
export {
  useEditComposer,
  useMessage,
  useMessageRuntime
};
//# sourceMappingURL=MessageContext.js.map