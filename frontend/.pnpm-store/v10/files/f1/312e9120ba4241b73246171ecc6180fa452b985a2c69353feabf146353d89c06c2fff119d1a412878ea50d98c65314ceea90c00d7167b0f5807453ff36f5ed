// src/legacy-runtime/client/ThreadListItemRuntimeClient.ts
import { resource, tapEffect } from "@assistant-ui/tap";
import { tapApi } from "../../utils/tap-store/index.js";
import { tapSubscribable } from "../util-hooks/tapSubscribable.js";
import { tapEvents } from "../../client/EventContext.js";
var ThreadListItemClient = resource(
  ({ runtime }) => {
    const runtimeState = tapSubscribable(runtime);
    const events = tapEvents();
    tapEffect(() => {
      const unsubscribers = [];
      const threadListItemEvents = [
        "switched-to",
        "switched-away"
      ];
      for (const event of threadListItemEvents) {
        const unsubscribe = runtime.unstable_on(event, () => {
          events.emit(`thread-list-item.${event}`, {
            threadId: runtime.getState().id
          });
        });
        unsubscribers.push(unsubscribe);
      }
      return () => {
        for (const unsub of unsubscribers) unsub();
      };
    }, [runtime, events]);
    return tapApi(
      {
        getState: () => runtimeState,
        switchTo: runtime.switchTo,
        rename: runtime.rename,
        archive: runtime.archive,
        unarchive: runtime.unarchive,
        delete: runtime.delete,
        generateTitle: runtime.generateTitle,
        initialize: runtime.initialize,
        detach: runtime.detach,
        __internal_getRuntime: () => runtime
      },
      {
        key: runtimeState.id
      }
    );
  }
);
export {
  ThreadListItemClient
};
//# sourceMappingURL=ThreadListItemRuntimeClient.js.map