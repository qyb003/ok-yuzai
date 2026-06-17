"use client";

// src/client/NoOpComposerClient.tsx
import { resource, tapMemo } from "@assistant-ui/tap";
import { tapApi } from "../utils/tap-store/index.js";
var NoOpComposerClient = resource(
  ({ type }) => {
    const state = tapMemo(() => {
      return {
        isEditing: false,
        isEmpty: true,
        text: "",
        attachmentAccept: "*",
        attachments: [],
        role: "user",
        runConfig: {},
        canCancel: false,
        type
      };
    }, [type]);
    return tapApi({
      getState: () => state,
      setText: () => {
        throw new Error("Not supported");
      },
      setRole: () => {
        throw new Error("Not supported");
      },
      setRunConfig: () => {
        throw new Error("Not supported");
      },
      addAttachment: () => {
        throw new Error("Not supported");
      },
      clearAttachments: () => {
        throw new Error("Not supported");
      },
      attachment: () => {
        throw new Error("Not supported");
      },
      reset: () => {
        throw new Error("Not supported");
      },
      send: () => {
        throw new Error("Not supported");
      },
      cancel: () => {
        throw new Error("Not supported");
      },
      beginEdit: () => {
        throw new Error("Not supported");
      }
    });
  }
);
export {
  NoOpComposerClient
};
//# sourceMappingURL=NoOpComposerClient.js.map