// src/client/AssistantClient.ts
import {
  tapMemo,
  resource,
  tapInlineResource,
  tapResource
} from "@assistant-ui/tap";
import { Tools } from "../model-context/index.js";
import { asStore, tapApi } from "../utils/tap-store/index.js";
import { useResource } from "@assistant-ui/tap/react";
import { useMemo } from "react";
import {
  checkEventScope,
  normalizeEventSelector
} from "../types/EventTypes.js";
import { EventManager } from "../legacy-runtime/client/EventManagerRuntimeClient.js";
import {
  createAssistantApiField,
  useAssistantApiImpl,
  extendApi
} from "../context/react/AssistantApiContext.js";
import { withEventsProvider } from "./EventContext.js";
import { withModelContextProvider } from "./ModelContext.js";
import { ModelContext as ModelContextResource } from "./ModelContextClient.js";
var AssistantStore = resource(
  ({
    threads: threadsEl,
    modelContext: modelContextEl,
    tools: toolsEl
  }) => {
    const events = tapInlineResource(EventManager());
    const { threads, tools, modelContext } = withEventsProvider(events, () => {
      const modelContextResource = tapResource(
        modelContextEl ?? ModelContextResource(),
        [modelContextEl]
      );
      return withModelContextProvider(modelContextResource.api, () => {
        return {
          modelContext: modelContextResource,
          tools: tapResource(toolsEl ?? Tools({}), [toolsEl]),
          threads: tapResource(threadsEl, [threadsEl])
        };
      });
    });
    const state = tapMemo(
      () => ({
        threads: threads.state,
        tools: tools.state,
        modelContext: modelContext.state
      }),
      [threads.state, tools.state, modelContext.state]
    );
    return tapApi({
      getState: () => state,
      threads: threads.api,
      tools: tools.api,
      modelContext: modelContext.api,
      on: events.on
    });
  }
);
var getClientFromStore = (client) => {
  const getItem = () => {
    return client.getState().api.threads.item("main");
  };
  return {
    threads: createAssistantApiField({
      source: "root",
      query: {},
      get: () => client.getState().api.threads
    }),
    tools: createAssistantApiField({
      source: "root",
      query: {},
      get: () => client.getState().api.tools
    }),
    modelContext: createAssistantApiField({
      source: "root",
      query: {},
      get: () => client.getState().api.modelContext
    }),
    thread: createAssistantApiField({
      source: "threads",
      query: { type: "main" },
      get: () => client.getState().api.threads.thread("main")
    }),
    threadListItem: createAssistantApiField({
      source: "threads",
      query: { type: "main" },
      get: () => getItem()
    }),
    composer: createAssistantApiField({
      source: "thread",
      query: {},
      get: () => client.getState().api.threads.thread("main").composer
    }),
    on(selector, callback) {
      const { event, scope } = normalizeEventSelector(selector);
      if (scope === "*") return client.getState().api.on(event, callback);
      if (checkEventScope("thread", scope, event) || checkEventScope("thread-list-item", scope, event) || checkEventScope("composer", scope, event)) {
        return client.getState().api.on(event, (e) => {
          if (e.threadId !== getItem().getState().id) return;
          callback(e);
        });
      }
      throw new Error(
        `Event scope is not available in this component: ${scope}`
      );
    },
    subscribe: client.subscribe,
    flushSync: client.flushSync
  };
};
var useAssistantClient = (props) => {
  const api = useAssistantApiImpl();
  const client = useResource(asStore(AssistantStore(props)));
  const clientApi = useMemo(() => getClientFromStore(client), [client]);
  return useMemo(() => extendApi(api, clientApi), [api, clientApi]);
};
export {
  useAssistantClient
};
//# sourceMappingURL=AssistantClient.js.map