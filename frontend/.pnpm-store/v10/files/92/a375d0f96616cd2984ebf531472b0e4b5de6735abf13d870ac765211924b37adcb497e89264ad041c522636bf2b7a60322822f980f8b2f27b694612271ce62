"use client";

// src/context/providers/TextMessagePartProvider.tsx
import {
  AssistantProvider,
  useExtendedAssistantApi
} from "../react/AssistantApiContext.js";
import { resource, tapMemo } from "@assistant-ui/tap";
import { useResource } from "@assistant-ui/tap/react";
import { asStore, tapApi } from "../../utils/tap-store/index.js";
import { DerivedScope } from "../../utils/tap-store/derived-scopes.js";
import { jsx } from "react/jsx-runtime";
var TextMessagePartClient = resource(
  ({ text, isRunning }) => {
    const state = tapMemo(
      () => ({
        type: "text",
        text,
        status: isRunning ? { type: "running" } : { type: "complete" }
      }),
      [text, isRunning]
    );
    return tapApi({
      getState: () => state,
      addToolResult: () => {
        throw new Error("Not supported");
      },
      resumeToolCall: () => {
        throw new Error("Not supported");
      }
    });
  }
);
var TextMessagePartProvider = ({ text, isRunning = false, children }) => {
  const store = useResource(
    asStore(TextMessagePartClient({ text, isRunning }))
  );
  const api = useExtendedAssistantApi({
    part: DerivedScope({
      source: "root",
      query: {},
      get: () => store.getState().api
    }),
    subscribe: store.subscribe,
    flushSync: store.flushSync
  });
  return /* @__PURE__ */ jsx(AssistantProvider, { api, children });
};
export {
  TextMessagePartProvider
};
//# sourceMappingURL=TextMessagePartProvider.js.map