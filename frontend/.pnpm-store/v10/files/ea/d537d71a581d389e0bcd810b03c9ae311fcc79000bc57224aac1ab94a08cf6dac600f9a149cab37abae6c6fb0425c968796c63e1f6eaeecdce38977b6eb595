"use client";

// src/legacy-runtime/hooks/ThreadListItemContext.ts
import { createStateHookForRuntime } from "../../context/react/utils/createStateHookForRuntime.js";
import { useAssistantApi, useAssistantState } from "../../context/react/index.js";
function useThreadListItemRuntime(options) {
  const api = useAssistantApi();
  const runtime = useAssistantState(
    () => api.threadListItem.source ? api.threadListItem().__internal_getRuntime?.() ?? null : null
  );
  if (!runtime && !options?.optional) {
    throw new Error("ThreadListItemRuntime is not available");
  }
  return runtime;
}
var useThreadListItem = createStateHookForRuntime(
  useThreadListItemRuntime
);
export {
  useThreadListItem,
  useThreadListItemRuntime
};
//# sourceMappingURL=ThreadListItemContext.js.map