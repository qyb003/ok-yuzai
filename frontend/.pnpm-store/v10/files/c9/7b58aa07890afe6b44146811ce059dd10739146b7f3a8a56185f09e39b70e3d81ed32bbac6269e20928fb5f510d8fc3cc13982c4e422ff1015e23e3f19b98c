"use client";

// src/legacy-runtime/hooks/AttachmentContext.ts
import { createStateHookForRuntime } from "../../context/react/utils/createStateHookForRuntime.js";
import { useAssistantApi, useAssistantState } from "../../context/react/index.js";
function useAttachmentRuntime(options) {
  const api = useAssistantApi();
  const runtime = useAssistantState(
    () => api.attachment.source ? api.attachment().__internal_getRuntime?.() ?? null : null
  );
  if (!runtime && !options?.optional) {
    throw new Error("AttachmentRuntime is not available");
  }
  return runtime;
}
function useThreadComposerAttachmentRuntime(options) {
  const attachmentRuntime = useAttachmentRuntime(options);
  if (!attachmentRuntime) return null;
  if (attachmentRuntime.source !== "thread-composer")
    throw new Error(
      "This component must be used within a thread's ComposerPrimitive.Attachments component."
    );
  return attachmentRuntime;
}
function useEditComposerAttachmentRuntime(options) {
  const attachmentRuntime = useAttachmentRuntime(options);
  if (!attachmentRuntime) return null;
  if (attachmentRuntime.source !== "edit-composer")
    throw new Error(
      "This component must be used within a message's ComposerPrimitive.Attachments component."
    );
  return attachmentRuntime;
}
function useMessageAttachmentRuntime(options) {
  const attachmentRuntime = useAttachmentRuntime(options);
  if (!attachmentRuntime) return null;
  if (attachmentRuntime.source !== "message")
    throw new Error(
      "This component must be used within a MessagePrimitive.Attachments component."
    );
  return attachmentRuntime;
}
var useAttachment = createStateHookForRuntime(useAttachmentRuntime);
var useThreadComposerAttachment = createStateHookForRuntime(
  useThreadComposerAttachmentRuntime
);
var useEditComposerAttachment = createStateHookForRuntime(
  useEditComposerAttachmentRuntime
);
var useMessageAttachment = createStateHookForRuntime(
  useMessageAttachmentRuntime
);
export {
  useAttachment,
  useAttachmentRuntime,
  useEditComposerAttachment,
  useEditComposerAttachmentRuntime,
  useMessageAttachment,
  useMessageAttachmentRuntime,
  useThreadComposerAttachment,
  useThreadComposerAttachmentRuntime
};
//# sourceMappingURL=AttachmentContext.js.map