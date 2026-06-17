"use client";

// src/context/providers/ThreadListItemProvider.tsx
import {
  AssistantProvider,
  useAssistantApi,
  useExtendedAssistantApi
} from "../react/AssistantApiContext.js";
import {
  checkEventScope,
  normalizeEventSelector
} from "../../types/EventTypes.js";
import { DerivedScope } from "../../utils/tap-store/derived-scopes.js";
import { jsx } from "react/jsx-runtime";
var ThreadListItemByIndexProvider = ({ index, archived, children }) => {
  const baseApi = useAssistantApi();
  const api = useExtendedAssistantApi({
    threadListItem: DerivedScope({
      source: "threads",
      query: { type: "index", index, archived },
      get: () => baseApi.threads().item({ index, archived })
    }),
    on(selector, callback) {
      const getItem = () => baseApi.threads().item({ index, archived });
      const { event, scope } = normalizeEventSelector(selector);
      if (!checkEventScope("thread-list-item", scope, event))
        return baseApi.on(selector, callback);
      return baseApi.on({ scope: "*", event }, (e) => {
        if (e.threadId === getItem().getState().id) {
          callback(e);
        }
      });
    }
  });
  return /* @__PURE__ */ jsx(AssistantProvider, { api, children });
};
var ThreadListItemByIdProvider = ({ id, children }) => {
  const baseApi = useAssistantApi();
  const api = useExtendedAssistantApi({
    threadListItem: DerivedScope({
      source: "threads",
      query: { type: "id", id },
      get: () => baseApi.threads().item({ id })
    }),
    on(selector, callback) {
      const getItem = () => baseApi.threads().item({ id });
      const { event, scope } = normalizeEventSelector(selector);
      if (!checkEventScope("thread-list-item", scope, event))
        return baseApi.on(selector, callback);
      return baseApi.on({ scope: "*", event }, (e) => {
        if (e.threadId !== getItem().getState().id) return;
        callback(e);
      });
    }
  });
  return /* @__PURE__ */ jsx(AssistantProvider, { api, children });
};
export {
  ThreadListItemByIdProvider,
  ThreadListItemByIndexProvider
};
//# sourceMappingURL=ThreadListItemProvider.js.map