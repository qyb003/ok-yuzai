"use client";

// src/primitives/threadList/ThreadListItems.tsx
import { memo, useMemo } from "react";
import {
  ThreadListItemByIndexProvider,
  useAssistantState
} from "../../context/index.js";
import { jsx } from "react/jsx-runtime";
var ThreadListPrimitiveItemByIndex = memo(
  ({ index, archived = false, components }) => {
    const ThreadListItemComponent = components.ThreadListItem;
    return /* @__PURE__ */ jsx(ThreadListItemByIndexProvider, { index, archived, children: /* @__PURE__ */ jsx(ThreadListItemComponent, {}) });
  },
  (prev, next) => prev.index === next.index && prev.archived === next.archived && prev.components.ThreadListItem === next.components.ThreadListItem
);
ThreadListPrimitiveItemByIndex.displayName = "ThreadListPrimitive.ItemByIndex";
var ThreadListPrimitiveItems = ({
  archived = false,
  components
}) => {
  const contentLength = useAssistantState(
    ({ threads }) => archived ? threads.archivedThreadIds.length : threads.threadIds.length
  );
  const listElements = useMemo(() => {
    return Array.from({ length: contentLength }, (_, index) => /* @__PURE__ */ jsx(
      ThreadListPrimitiveItemByIndex,
      {
        index,
        archived,
        components
      },
      index
    ));
  }, [contentLength, archived, components]);
  return listElements;
};
ThreadListPrimitiveItems.displayName = "ThreadListPrimitive.Items";
export {
  ThreadListPrimitiveItemByIndex,
  ThreadListPrimitiveItems
};
//# sourceMappingURL=ThreadListItems.js.map