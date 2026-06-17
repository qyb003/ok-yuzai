"use client";

// src/legacy-runtime/hooks/ComposerContext.ts
import { useAssistantApi, useAssistantState } from "../../context/react/index.js";
import { createStateHookForRuntime } from "../../context/react/utils/createStateHookForRuntime.js";
function useComposerRuntime(options) {
  const api = useAssistantApi();
  const runtime = useAssistantState(
    () => api.composer.source ? api.composer().__internal_getRuntime?.() ?? null : null
  );
  if (!runtime && !options?.optional) {
    throw new Error("ComposerRuntime is not available");
  }
  return runtime;
}
var useComposer = createStateHookForRuntime(useComposerRuntime);
export {
  useComposer,
  useComposerRuntime
};
//# sourceMappingURL=ComposerContext.js.map