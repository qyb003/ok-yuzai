"use client";

// src/primitives/composer/ComposerAttachments.tsx
import { memo, useMemo } from "react";
import {
  useAssistantState,
  ComposerAttachmentByIndexProvider
} from "../../context/index.js";
import { jsx } from "react/jsx-runtime";
var getComponent = (components, attachment) => {
  const type = attachment.type;
  switch (type) {
    case "image":
      return components?.Image ?? components?.Attachment;
    case "document":
      return components?.Document ?? components?.Attachment;
    case "file":
      return components?.File ?? components?.Attachment;
    default:
      const _exhaustiveCheck = type;
      throw new Error(`Unknown attachment type: ${_exhaustiveCheck}`);
  }
};
var AttachmentComponent = ({ components }) => {
  const attachment = useAssistantState(({ attachment: attachment2 }) => attachment2);
  if (!attachment) return null;
  const Component = getComponent(components, attachment);
  if (!Component) return null;
  return /* @__PURE__ */ jsx(Component, {});
};
var ComposerPrimitiveAttachmentByIndex = memo(
  ({ index, components }) => {
    return /* @__PURE__ */ jsx(ComposerAttachmentByIndexProvider, { index, children: /* @__PURE__ */ jsx(AttachmentComponent, { components }) });
  },
  (prev, next) => prev.index === next.index && prev.components?.Image === next.components?.Image && prev.components?.Document === next.components?.Document && prev.components?.File === next.components?.File && prev.components?.Attachment === next.components?.Attachment
);
ComposerPrimitiveAttachmentByIndex.displayName = "ComposerPrimitive.AttachmentByIndex";
var ComposerPrimitiveAttachments = ({ components }) => {
  const attachmentsCount = useAssistantState(
    (s) => s.composer.attachments.length
  );
  const attachmentElements = useMemo(() => {
    return Array.from({ length: attachmentsCount }, (_, index) => /* @__PURE__ */ jsx(
      ComposerPrimitiveAttachmentByIndex,
      {
        index,
        components
      },
      index
    ));
  }, [attachmentsCount, components]);
  return attachmentElements;
};
ComposerPrimitiveAttachments.displayName = "ComposerPrimitive.Attachments";
export {
  ComposerPrimitiveAttachmentByIndex,
  ComposerPrimitiveAttachments
};
//# sourceMappingURL=ComposerAttachments.js.map