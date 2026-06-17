// src/legacy-runtime/client/ComposerRuntimeClient.ts
import {
  resource,
  tapMemo,
  tapEffect,
  tapInlineResource
} from "@assistant-ui/tap";
import { tapApi } from "../../utils/tap-store/index.js";
import { tapEvents } from "../../client/EventContext.js";
import { tapLookupResources } from "../../client/util-hooks/tapLookupResources.js";
import { AttachmentRuntimeClient } from "./AttachmentRuntimeClient.js";
import { tapSubscribable } from "../util-hooks/tapSubscribable.js";
var ComposerAttachmentClientByIndex = resource(
  ({ runtime, index }) => {
    const attachmentRuntime = tapMemo(
      () => runtime.getAttachmentByIndex(index),
      [runtime, index]
    );
    return tapInlineResource(
      AttachmentRuntimeClient({
        runtime: attachmentRuntime
      })
    );
  }
);
var ComposerClient = resource(
  ({
    threadIdRef,
    messageIdRef,
    runtime
  }) => {
    const runtimeState = tapSubscribable(runtime);
    const events = tapEvents();
    tapEffect(() => {
      const unsubscribers = [];
      const composerEvents = [
        "send",
        "attachment-add"
      ];
      for (const event of composerEvents) {
        const unsubscribe = runtime.unstable_on(event, () => {
          events.emit(`composer.${event}`, {
            threadId: threadIdRef.current,
            ...messageIdRef && { messageId: messageIdRef.current }
          });
        });
        unsubscribers.push(unsubscribe);
      }
      return () => {
        for (const unsub of unsubscribers) unsub();
      };
    }, [runtime, events, threadIdRef, messageIdRef]);
    const attachments = tapLookupResources(
      runtimeState.attachments.map(
        (_, idx) => ComposerAttachmentClientByIndex(
          { runtime, index: idx },
          { key: idx }
        )
      )
    );
    const state = tapMemo(() => {
      return {
        text: runtimeState.text,
        role: runtimeState.role,
        attachments: attachments.state,
        runConfig: runtimeState.runConfig,
        isEditing: runtimeState.isEditing,
        canCancel: runtimeState.canCancel,
        attachmentAccept: runtimeState.attachmentAccept,
        isEmpty: runtimeState.isEmpty,
        type: runtimeState.type ?? "thread"
      };
    }, [runtimeState, attachments.state]);
    return tapApi({
      getState: () => state,
      setText: runtime.setText,
      setRole: runtime.setRole,
      setRunConfig: runtime.setRunConfig,
      addAttachment: runtime.addAttachment,
      reset: runtime.reset,
      clearAttachments: runtime.clearAttachments,
      send: runtime.send,
      cancel: runtime.cancel,
      beginEdit: runtime.beginEdit ?? (() => {
        throw new Error("beginEdit is not supported in this runtime");
      }),
      attachment: (selector) => {
        if ("id" in selector) {
          return attachments.api({ key: selector.id });
        } else {
          return attachments.api(selector);
        }
      },
      __internal_getRuntime: () => runtime
    });
  }
);
export {
  ComposerClient
};
//# sourceMappingURL=ComposerRuntimeClient.js.map