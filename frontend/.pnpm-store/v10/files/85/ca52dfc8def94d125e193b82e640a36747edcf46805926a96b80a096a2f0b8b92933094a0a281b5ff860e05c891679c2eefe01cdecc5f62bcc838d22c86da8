"use client";

// src/primitives/threadListItem/ThreadListItemTrigger.ts
import {
  createActionButton
} from "../../utils/createActionButton.js";
import { useAssistantApi } from "../../context/index.js";
import { useCallback } from "react";
var useThreadListItemTrigger = () => {
  const api = useAssistantApi();
  return useCallback(() => {
    api.threadListItem().switchTo();
  }, [api]);
};
var ThreadListItemPrimitiveTrigger = createActionButton(
  "ThreadListItemPrimitive.Trigger",
  useThreadListItemTrigger
);
export {
  ThreadListItemPrimitiveTrigger
};
//# sourceMappingURL=ThreadListItemTrigger.js.map