"use client";

// src/context/providers/MessageProvider.tsx
import {
  AssistantProvider,
  useExtendedAssistantApi
} from "../react/AssistantApiContext.js";
import { useResource } from "@assistant-ui/tap/react";
import { asStore } from "../../utils/tap-store/index.js";
import {
  ThreadMessageClient
} from "../../client/ThreadMessageClient.js";
import { DerivedScope } from "../../utils/tap-store/derived-scopes.js";
import { jsx } from "react/jsx-runtime";
var MessageProvider = ({ children, ...props }) => {
  const store = useResource(asStore(ThreadMessageClient(props)));
  const api = useExtendedAssistantApi({
    message: DerivedScope({
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
  MessageProvider
};
//# sourceMappingURL=MessageProvider.js.map