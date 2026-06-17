"use client";

// src/primitives/attachment/AttachmentThumb.tsx
import { forwardRef } from "react";
import { useAssistantState } from "../../context/index.js";
import { Primitive } from "@radix-ui/react-primitive";
import { jsxs } from "react/jsx-runtime";
var AttachmentPrimitiveThumb = forwardRef((props, ref) => {
  const ext = useAssistantState(({ attachment }) => {
    const parts = attachment.name.split(".");
    return parts.length > 1 ? parts.pop() : "";
  });
  return /* @__PURE__ */ jsxs(Primitive.div, { ...props, ref, children: [
    ".",
    ext
  ] });
});
AttachmentPrimitiveThumb.displayName = "AttachmentPrimitive.Thumb";
export {
  AttachmentPrimitiveThumb
};
//# sourceMappingURL=AttachmentThumb.js.map