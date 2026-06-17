"use client";

// src/primitives/threadListItem/ThreadListItemArchive.ts
import {
  createActionButton
} from "../../utils/createActionButton.js";
import { useAssistantApi } from "../../context/index.js";
import { useCallback } from "react";
var useThreadListItemArchive = () => {
  const api = useAssistantApi();
  return useCallback(() => {
    api.threadListItem().archive();
  }, [api]);
};
var ThreadListItemPrimitiveArchive = createActionButton(
  "ThreadListItemPrimitive.Archive",
  useThreadListItemArchive
);
export {
  ThreadListItemPrimitiveArchive
};
//# sourceMappingURL=ThreadListItemArchive.js.map