"use client";

// src/primitives/threadListItem/ThreadListItemUnarchive.ts
import {
  createActionButton
} from "../../utils/createActionButton.js";
import { useAssistantApi } from "../../context/index.js";
import { useCallback } from "react";
var useThreadListItemUnarchive = () => {
  const api = useAssistantApi();
  return useCallback(() => {
    api.threadListItem().unarchive();
  }, [api]);
};
var ThreadListItemPrimitiveUnarchive = createActionButton(
  "ThreadListItemPrimitive.Unarchive",
  useThreadListItemUnarchive
);
export {
  ThreadListItemPrimitiveUnarchive
};
//# sourceMappingURL=ThreadListItemUnarchive.js.map