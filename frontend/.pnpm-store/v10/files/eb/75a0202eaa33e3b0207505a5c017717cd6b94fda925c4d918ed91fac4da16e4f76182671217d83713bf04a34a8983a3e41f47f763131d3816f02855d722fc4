"use client";

// src/primitives/actionBar/ActionBarStopSpeaking.tsx
import { forwardRef } from "react";
import { useEscapeKeydown } from "@radix-ui/react-use-escape-keydown";
import { Primitive } from "@radix-ui/react-primitive";
import { composeEventHandlers } from "@radix-ui/primitive";
import { useCallback } from "react";
import { useAssistantState, useAssistantApi } from "../../context/index.js";
import { jsx } from "react/jsx-runtime";
var useActionBarStopSpeaking = () => {
  const api = useAssistantApi();
  const isSpeaking = useAssistantState(({ message }) => message.speech != null);
  const callback = useCallback(() => {
    api.message().stopSpeaking();
  }, [api]);
  if (!isSpeaking) return null;
  return callback;
};
var ActionBarPrimitiveStopSpeaking = forwardRef((props, ref) => {
  const callback = useActionBarStopSpeaking();
  useEscapeKeydown((e) => {
    if (callback) {
      e.preventDefault();
      callback();
    }
  });
  return /* @__PURE__ */ jsx(
    Primitive.button,
    {
      type: "button",
      disabled: !callback,
      ...props,
      ref,
      onClick: composeEventHandlers(props.onClick, () => {
        callback?.();
      })
    }
  );
});
ActionBarPrimitiveStopSpeaking.displayName = "ActionBarPrimitive.StopSpeaking";
export {
  ActionBarPrimitiveStopSpeaking
};
//# sourceMappingURL=ActionBarStopSpeaking.js.map