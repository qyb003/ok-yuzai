"use client";

// src/primitives/attachment/AttachmentRemove.tsx
import {
  createActionButton
} from "../../utils/createActionButton.js";
import { useCallback } from "react";
import { useAssistantApi } from "../../context/index.js";
var useAttachmentRemove = () => {
  const api = useAssistantApi();
  const handleRemoveAttachment = useCallback(() => {
    api.attachment().remove();
  }, [api]);
  return handleRemoveAttachment;
};
var AttachmentPrimitiveRemove = createActionButton(
  "AttachmentPrimitive.Remove",
  useAttachmentRemove
);
export {
  AttachmentPrimitiveRemove
};
//# sourceMappingURL=AttachmentRemove.js.map