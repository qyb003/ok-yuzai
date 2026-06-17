// src/legacy-runtime/client/ThreadListRuntimeClient.ts
import { tapApi } from "../../utils/tap-store/index.js";
import { resource, tapInlineResource, tapMemo } from "@assistant-ui/tap";
import { tapSubscribable } from "../util-hooks/tapSubscribable.js";
import { ThreadListItemClient } from "./ThreadListItemRuntimeClient.js";
import { ThreadClient } from "./ThreadRuntimeClient.js";
import { tapLookupResources } from "../../client/util-hooks/tapLookupResources.js";
var ThreadListItemClientById = resource(
  ({ runtime, id }) => {
    const threadListItemRuntime = tapMemo(
      () => runtime.getItemById(id),
      [runtime, id]
    );
    return tapInlineResource(
      ThreadListItemClient({
        runtime: threadListItemRuntime
      })
    );
  }
);
var ThreadListClient = resource(
  ({
    runtime,
    __internal_assistantRuntime
  }) => {
    const runtimeState = tapSubscribable(runtime);
    const main = tapInlineResource(
      ThreadClient({
        runtime: runtime.main
      })
    );
    const threadItems = tapLookupResources(
      Object.keys(runtimeState.threadItems).map(
        (id) => ThreadListItemClientById({ runtime, id }, { key: id })
      )
    );
    const state = tapMemo(() => {
      return {
        mainThreadId: runtimeState.mainThreadId,
        newThreadId: runtimeState.newThread ?? null,
        isLoading: runtimeState.isLoading,
        threadIds: runtimeState.threads,
        archivedThreadIds: runtimeState.archivedThreads,
        threadItems: threadItems.state,
        main: main.state
      };
    }, [runtimeState, threadItems.state, main.state]);
    return tapApi({
      getState: () => state,
      thread: () => main.api,
      item: (threadIdOrOptions) => {
        if (threadIdOrOptions === "main") {
          return threadItems.api({ key: state.mainThreadId });
        }
        if ("id" in threadIdOrOptions) {
          return threadItems.api({ key: threadIdOrOptions.id });
        }
        const { index, archived = false } = threadIdOrOptions;
        const id = archived ? state.archivedThreadIds[index] : state.threadIds[index];
        return threadItems.api({ key: id });
      },
      switchToThread: (threadId) => {
        runtime.switchToThread(threadId);
      },
      switchToNewThread: () => {
        runtime.switchToNewThread();
      },
      __internal_getAssistantRuntime: () => __internal_assistantRuntime
    });
  }
);
export {
  ThreadListClient
};
//# sourceMappingURL=ThreadListRuntimeClient.js.map