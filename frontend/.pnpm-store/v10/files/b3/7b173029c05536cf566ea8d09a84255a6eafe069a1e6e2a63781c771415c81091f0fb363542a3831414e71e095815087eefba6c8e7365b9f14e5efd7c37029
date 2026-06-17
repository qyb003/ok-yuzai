"use client";

// src/legacy-runtime/hooks/ThreadContext.ts
import { useState } from "react";
import { createStateHookForRuntime } from "../../context/react/utils/createStateHookForRuntime.js";
import {
  useAssistantApi,
  useAssistantEvent,
  useAssistantState
} from "../../context/react/index.js";
function useThreadRuntime(options) {
  const api = useAssistantApi();
  const runtime = useAssistantState(
    () => api.thread.source ? api.thread().__internal_getRuntime?.() ?? null : null
  );
  if (!runtime && !options?.optional) {
    throw new Error("ThreadRuntime is not available");
  }
  return runtime;
}
var useThread = createStateHookForRuntime(useThreadRuntime);
var useThreadComposerRuntime = (opt) => useThreadRuntime(opt)?.composer ?? null;
var useThreadComposer = createStateHookForRuntime(
  useThreadComposerRuntime
);
function useThreadModelContext(options) {
  const [, rerender] = useState({});
  const runtime = useThreadRuntime(options);
  useAssistantEvent("thread.model-context-update", () => rerender({}));
  if (!runtime) return null;
  return runtime?.getModelContext();
}
export {
  useThread,
  useThreadComposer,
  useThreadModelContext,
  useThreadRuntime
};
//# sourceMappingURL=ThreadContext.js.map