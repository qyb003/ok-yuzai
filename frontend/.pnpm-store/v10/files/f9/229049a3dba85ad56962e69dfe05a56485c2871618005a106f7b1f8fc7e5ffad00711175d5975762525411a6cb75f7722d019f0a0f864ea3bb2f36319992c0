"use client";

// src/primitives/message/MessageIf.tsx
import { useAssistantState } from "../../context/index.js";
var useMessageIf = (props) => {
  return useAssistantState(({ message }) => {
    const {
      role,
      attachments,
      parts,
      branchCount,
      isLast,
      speech,
      isCopied,
      isHovering
    } = message;
    if (props.hasBranches === true && branchCount < 2) return false;
    if (props.user && role !== "user") return false;
    if (props.assistant && role !== "assistant") return false;
    if (props.system && role !== "system") return false;
    if (props.lastOrHover === true && !isHovering && !isLast) return false;
    if (props.last !== void 0 && props.last !== isLast) return false;
    if (props.copied === true && !isCopied) return false;
    if (props.copied === false && isCopied) return false;
    if (props.speaking === true && speech == null) return false;
    if (props.speaking === false && speech != null) return false;
    if (props.hasAttachments === true && (role !== "user" || !attachments?.length))
      return false;
    if (props.hasAttachments === false && role === "user" && !!attachments?.length)
      return false;
    if (props.hasContent === true && parts.length === 0) return false;
    if (props.hasContent === false && parts.length > 0) return false;
    if (props.submittedFeedback !== void 0 && (message.metadata.submittedFeedback?.type ?? null) !== props.submittedFeedback)
      return false;
    return true;
  });
};
var MessagePrimitiveIf = ({
  children,
  ...query
}) => {
  const result = useMessageIf(query);
  return result ? children : null;
};
MessagePrimitiveIf.displayName = "MessagePrimitive.If";
export {
  MessagePrimitiveIf
};
//# sourceMappingURL=MessageIf.js.map