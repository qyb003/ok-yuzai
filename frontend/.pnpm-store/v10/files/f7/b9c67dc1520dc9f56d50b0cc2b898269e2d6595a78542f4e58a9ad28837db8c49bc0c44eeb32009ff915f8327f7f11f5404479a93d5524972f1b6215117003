"use client";

// src/primitives/threadList/ThreadListNew.tsx
import { forwardRef } from "react";
import { Primitive } from "@radix-ui/react-primitive";
import { composeEventHandlers } from "@radix-ui/primitive";
import { useAssistantState, useAssistantApi } from "../../context/index.js";
import { jsx } from "react/jsx-runtime";
var ThreadListPrimitiveNew = forwardRef(({ onClick, disabled, ...props }, forwardedRef) => {
  const isMain = useAssistantState(
    ({ threads }) => threads.newThreadId === threads.mainThreadId
  );
  const api = useAssistantApi();
  return /* @__PURE__ */ jsx(
    Primitive.button,
    {
      type: "button",
      ...isMain ? { "data-active": "true", "aria-current": "true" } : null,
      ...props,
      ref: forwardedRef,
      disabled,
      onClick: composeEventHandlers(onClick, () => {
        api.threads().switchToNewThread();
      })
    }
  );
});
ThreadListPrimitiveNew.displayName = "ThreadListPrimitive.New";
export {
  ThreadListPrimitiveNew
};
//# sourceMappingURL=ThreadListNew.js.map