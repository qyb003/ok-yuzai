// src/legacy-runtime/client/MessageRuntimeClient.ts
import {
  resource,
  tapInlineResource,
  tapMemo,
  tapState
} from "@assistant-ui/tap";
import { tapApi } from "../../utils/tap-store/index.js";
import { tapSubscribable } from "../util-hooks/tapSubscribable.js";
import { ComposerClient } from "./ComposerRuntimeClient.js";
import { MessagePartClient } from "./MessagePartRuntimeClient.js";
import { tapLookupResources } from "../../client/util-hooks/tapLookupResources.js";
import { AttachmentRuntimeClient } from "./AttachmentRuntimeClient.js";
var MessageAttachmentClientByIndex = resource(
  ({ runtime, index }) => {
    const attachmentRuntime = tapMemo(
      () => runtime.getAttachmentByIndex(index),
      [runtime, index]
    );
    return tapInlineResource(
      AttachmentRuntimeClient({ runtime: attachmentRuntime })
    );
  }
);
var MessagePartByIndex = resource(
  ({ runtime, index }) => {
    const partRuntime = tapMemo(
      () => runtime.getMessagePartByIndex(index),
      [runtime, index]
    );
    return tapInlineResource(MessagePartClient({ runtime: partRuntime }));
  }
);
var MessageClient = resource(
  ({
    runtime,
    threadIdRef
  }) => {
    const runtimeState = tapSubscribable(runtime);
    const [isCopiedState, setIsCopied] = tapState(false);
    const [isHoveringState, setIsHovering] = tapState(false);
    const messageIdRef = tapMemo(
      () => ({
        get current() {
          return runtime.getState().id;
        }
      }),
      [runtime]
    );
    const composer = tapInlineResource(
      ComposerClient({
        runtime: runtime.composer,
        threadIdRef,
        messageIdRef
      })
    );
    const parts = tapLookupResources(
      runtimeState.content.map(
        (_, idx) => MessagePartByIndex({ runtime, index: idx }, { key: idx })
      )
    );
    const attachments = tapLookupResources(
      runtimeState.attachments?.map(
        (_, idx) => MessageAttachmentClientByIndex({ runtime, index: idx }, { key: idx })
      ) ?? []
    );
    const state = tapMemo(() => {
      return {
        ...runtimeState,
        parts: parts.state,
        composer: composer.state,
        isCopied: isCopiedState,
        isHovering: isHoveringState
      };
    }, [
      runtimeState,
      parts.state,
      composer.state,
      isCopiedState,
      isHoveringState
    ]);
    return tapApi(
      {
        getState: () => state,
        composer: composer.api,
        reload: (config) => runtime.reload(config),
        speak: () => runtime.speak(),
        stopSpeaking: () => runtime.stopSpeaking(),
        submitFeedback: (feedback) => runtime.submitFeedback(feedback),
        switchToBranch: (options) => runtime.switchToBranch(options),
        getCopyText: () => runtime.unstable_getCopyText(),
        part: (selector) => {
          if ("index" in selector) {
            return parts.api({ index: selector.index });
          } else {
            return parts.api({ key: "toolCallId-" + selector.toolCallId });
          }
        },
        attachment: (selector) => {
          if ("id" in selector) {
            return attachments.api({ key: selector.id });
          } else {
            return attachments.api(selector);
          }
        },
        setIsCopied,
        setIsHovering,
        __internal_getRuntime: () => runtime
      },
      {
        key: runtimeState.id
      }
    );
  }
);
export {
  MessageClient
};
//# sourceMappingURL=MessageRuntimeClient.js.map