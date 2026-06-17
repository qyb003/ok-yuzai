"use client";

// src/primitives/threadListItem/ThreadListItemDelete.ts
import {
  createActionButton
} from "../../utils/createActionButton.js";
import { useAssistantApi } from "../../context/index.js";
import { useCallback } from "react";
var useThreadListItemDelete = () => {
  const api = useAssistantApi();
  return useCallback(() => {
    api.threadListItem().delete();
  }, [api]);
};
var ThreadListItemPrimitiveDelete = createActionButton(
  "ThreadListItemPrimitive.Delete",
  useThreadListItemDelete
);
export {
  ThreadListItemPrimitiveDelete
};
//# sourceMappingURL=ThreadListItemDelete.js.map