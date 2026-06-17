"use client";

// src/primitives/actionBar/ActionBarCopy.tsx
import { forwardRef } from "react";
import { composeEventHandlers } from "@radix-ui/primitive";
import { Primitive } from "@radix-ui/react-primitive";
import { useCallback } from "react";
import { useAssistantState, useAssistantApi } from "../../context/index.js";
import { jsx } from "react/jsx-runtime";
var useActionBarPrimitiveCopy = ({
  copiedDuration = 3e3
} = {}) => {
  const api = useAssistantApi();
  const hasCopyableContent = useAssistantState(({ message }) => {
    return (message.role !== "assistant" || message.status?.type !== "running") && message.parts.some((c) => c.type === "text" && c.text.length > 0);
  });
  const isEditing = useAssistantState(({ composer }) => composer.isEditing);
  const composerValue = useAssistantState(({ composer }) => composer.text);
  const callback = useCallback(() => {
    const valueToCopy = isEditing ? composerValue : api.message().getCopyText();
    if (!valueToCopy) return;
    navigator.clipboard.writeText(valueToCopy).then(() => {
      api.message().setIsCopied(true);
      setTimeout(() => api.message().setIsCopied(false), copiedDuration);
    });
  }, [api, isEditing, composerValue, copiedDuration]);
  if (!hasCopyableContent) return null;
  return callback;
};
var ActionBarPrimitiveCopy = forwardRef(({ copiedDuration, onClick, disabled, ...props }, forwardedRef) => {
  const isCopied = useAssistantState(({ message }) => message.isCopied);
  const callback = useActionBarPrimitiveCopy({ copiedDuration });
  return /* @__PURE__ */ jsx(
    Primitive.button,
    {
      type: "button",
      ...isCopied ? { "data-copied": "true" } : {},
      ...props,
      ref: forwardedRef,
      disabled: disabled || !callback,
      onClick: composeEventHandlers(onClick, () => {
        callback?.();
      })
    }
  );
});
ActionBarPrimitiveCopy.displayName = "ActionBarPrimitive.Copy";
export {
  ActionBarPrimitiveCopy
};
//# sourceMappingURL=ActionBarCopy.js.map