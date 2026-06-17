// src/legacy-runtime/client/ThreadRuntimeClient.ts
import {
  resource,
  tapInlineResource,
  tapMemo,
  tapEffect
} from "@assistant-ui/tap";
import { ComposerClient } from "./ComposerRuntimeClient.js";
import { MessageClient } from "./MessageRuntimeClient.js";
import { tapSubscribable } from "../util-hooks/tapSubscribable.js";
import { tapApi } from "../../utils/tap-store/index.js";
import { tapLookupResources } from "../../client/util-hooks/tapLookupResources.js";
import { tapEvents } from "../../client/EventContext.js";
var MessageClientById = resource(
  ({
    runtime,
    id,
    threadIdRef
  }) => {
    const messageRuntime = tapMemo(
      () => runtime.getMessageById(id),
      [runtime, id]
    );
    return tapInlineResource(
      MessageClient({ runtime: messageRuntime, threadIdRef })
    );
  }
);
var ThreadClient = resource(
  ({ runtime }) => {
    const runtimeState = tapSubscribable(runtime);
    const events = tapEvents();
    tapEffect(() => {
      const unsubscribers = [];
      const threadEvents = [
        "run-start",
        "run-end",
        "initialize",
        "model-context-update"
      ];
      for (const event of threadEvents) {
        const unsubscribe = runtime.unstable_on(event, () => {
          const threadId = runtime.getState()?.threadId || "unknown";
          events.emit(`thread.${event}`, {
            threadId
          });
        });
        unsubscribers.push(unsubscribe);
      }
      return () => {
        for (const unsub of unsubscribers) unsub();
      };
    }, [runtime]);
    const threadIdRef = tapMemo(
      () => ({
        get current() {
          return runtime.getState().threadId;
        }
      }),
      [runtime]
    );
    const composer = tapInlineResource(
      ComposerClient({
        runtime: runtime.composer,
        threadIdRef
      })
    );
    const messages = tapLookupResources(
      runtimeState.messages.map(
        (m) => MessageClientById(
          { runtime, id: m.id, threadIdRef },
          { key: m.id }
        )
      )
    );
    const state = tapMemo(() => {
      return {
        isDisabled: runtimeState.isDisabled,
        isLoading: runtimeState.isLoading,
        isRunning: runtimeState.isRunning,
        capabilities: runtimeState.capabilities,
        state: runtimeState.state,
        suggestions: runtimeState.suggestions,
        extras: runtimeState.extras,
        speech: runtimeState.speech,
        composer: composer.state,
        messages: messages.state
      };
    }, [runtimeState, messages, composer.state]);
    return tapApi({
      getState: () => state,
      composer: composer.api,
      append: runtime.append,
      startRun: runtime.startRun,
      unstable_resumeRun: runtime.unstable_resumeRun,
      cancelRun: runtime.cancelRun,
      getModelContext: runtime.getModelContext,
      export: runtime.export,
      import: runtime.import,
      reset: runtime.reset,
      stopSpeaking: runtime.stopSpeaking,
      startVoice: async () => {
        throw new Error("startVoice is not supported in this runtime");
      },
      stopVoice: async () => {
        throw new Error("stopVoice is not supported in this runtime");
      },
      message: (selector) => {
        if ("id" in selector) {
          return messages.api({ key: selector.id });
        } else {
          return messages.api(selector);
        }
      },
      __internal_getRuntime: () => runtime
    });
  }
);
export {
  ThreadClient
};
//# sourceMappingURL=ThreadRuntimeClient.js.map