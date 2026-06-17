"use client";

// src/primitives/message/MessageParts.tsx
import {
  memo,
  useMemo
} from "react";
import {
  useAssistantState,
  useAssistantApi,
  PartByIndexProvider,
  TextMessagePartProvider
} from "../../context/index.js";
import { MessagePartPrimitiveText } from "../messagePart/MessagePartText.js";
import { MessagePartPrimitiveImage } from "../messagePart/MessagePartImage.js";
import { MessagePartPrimitiveInProgress } from "../messagePart/MessagePartInProgress.js";
import { useShallow } from "zustand/shallow";
import { Fragment, jsx, jsxs } from "react/jsx-runtime";
var createGroupState = (groupType) => {
  let start = -1;
  return {
    startGroup: (index) => {
      if (start === -1) {
        start = index;
      }
    },
    endGroup: (endIndex, ranges) => {
      if (start !== -1) {
        ranges.push({
          type: groupType,
          startIndex: start,
          endIndex
        });
        start = -1;
      }
    },
    finalize: (endIndex, ranges) => {
      if (start !== -1) {
        ranges.push({
          type: groupType,
          startIndex: start,
          endIndex
        });
      }
    }
  };
};
var groupMessageParts = (messageTypes) => {
  const ranges = [];
  const toolGroup = createGroupState("toolGroup");
  const reasoningGroup = createGroupState("reasoningGroup");
  for (let i = 0; i < messageTypes.length; i++) {
    const type = messageTypes[i];
    if (type === "tool-call") {
      reasoningGroup.endGroup(i - 1, ranges);
      toolGroup.startGroup(i);
    } else if (type === "reasoning") {
      toolGroup.endGroup(i - 1, ranges);
      reasoningGroup.startGroup(i);
    } else {
      toolGroup.endGroup(i - 1, ranges);
      reasoningGroup.endGroup(i - 1, ranges);
      ranges.push({ type: "single", index: i });
    }
  }
  toolGroup.finalize(messageTypes.length - 1, ranges);
  reasoningGroup.finalize(messageTypes.length - 1, ranges);
  return ranges;
};
var useMessagePartsGroups = () => {
  const messageTypes = useAssistantState(
    useShallow((s) => s.message.parts.map((c) => c.type))
  );
  return useMemo(() => {
    if (messageTypes.length === 0) {
      return [];
    }
    return groupMessageParts(messageTypes);
  }, [messageTypes]);
};
var ToolUIDisplay = ({
  Fallback,
  ...props
}) => {
  const Render = useAssistantState(({ tools }) => {
    const Render2 = tools.tools[props.toolName] ?? Fallback;
    if (Array.isArray(Render2)) return Render2[0] ?? Fallback;
    return Render2;
  });
  if (!Render) return null;
  return /* @__PURE__ */ jsx(Render, { ...props });
};
var defaultComponents = {
  Text: () => /* @__PURE__ */ jsxs("p", { style: { whiteSpace: "pre-line" }, children: [
    /* @__PURE__ */ jsx(MessagePartPrimitiveText, {}),
    /* @__PURE__ */ jsx(MessagePartPrimitiveInProgress, { children: /* @__PURE__ */ jsx("span", { style: { fontFamily: "revert" }, children: " \u25CF" }) })
  ] }),
  Reasoning: () => null,
  Source: () => null,
  Image: () => /* @__PURE__ */ jsx(MessagePartPrimitiveImage, {}),
  File: () => null,
  Unstable_Audio: () => null,
  ToolGroup: ({ children }) => children,
  ReasoningGroup: ({ children }) => children
};
var MessagePartComponent = ({
  components: {
    Text = defaultComponents.Text,
    Reasoning = defaultComponents.Reasoning,
    Image = defaultComponents.Image,
    Source = defaultComponents.Source,
    File = defaultComponents.File,
    Unstable_Audio: Audio = defaultComponents.Unstable_Audio,
    tools = {}
  } = {}
}) => {
  const api = useAssistantApi();
  const part = useAssistantState(({ part: part2 }) => part2);
  const type = part.type;
  if (type === "tool-call") {
    const addResult = api.part().addToolResult;
    const resume = api.part().resumeToolCall;
    if ("Override" in tools)
      return /* @__PURE__ */ jsx(tools.Override, { ...part, addResult, resume });
    const Tool = tools.by_name?.[part.toolName] ?? tools.Fallback;
    return /* @__PURE__ */ jsx(
      ToolUIDisplay,
      {
        ...part,
        Fallback: Tool,
        addResult,
        resume
      }
    );
  }
  if (part.status?.type === "requires-action")
    throw new Error("Encountered unexpected requires-action status");
  switch (type) {
    case "text":
      return /* @__PURE__ */ jsx(Text, { ...part });
    case "reasoning":
      return /* @__PURE__ */ jsx(Reasoning, { ...part });
    case "source":
      return /* @__PURE__ */ jsx(Source, { ...part });
    case "image":
      return /* @__PURE__ */ jsx(Image, { ...part });
    case "file":
      return /* @__PURE__ */ jsx(File, { ...part });
    case "audio":
      return /* @__PURE__ */ jsx(Audio, { ...part });
    case "data":
      return null;
    default:
      const unhandledType = type;
      throw new Error(`Unknown message part type: ${unhandledType}`);
  }
};
var MessagePrimitivePartByIndex = memo(
  ({ index, components }) => {
    return /* @__PURE__ */ jsx(PartByIndexProvider, { index, children: /* @__PURE__ */ jsx(MessagePartComponent, { components }) });
  },
  (prev, next) => prev.index === next.index && prev.components?.Text === next.components?.Text && prev.components?.Reasoning === next.components?.Reasoning && prev.components?.Source === next.components?.Source && prev.components?.Image === next.components?.Image && prev.components?.File === next.components?.File && prev.components?.Unstable_Audio === next.components?.Unstable_Audio && prev.components?.tools === next.components?.tools && prev.components?.ToolGroup === next.components?.ToolGroup && prev.components?.ReasoningGroup === next.components?.ReasoningGroup
);
MessagePrimitivePartByIndex.displayName = "MessagePrimitive.PartByIndex";
var EmptyPartFallback = ({ status, component: Component }) => {
  return /* @__PURE__ */ jsx(TextMessagePartProvider, { text: "", isRunning: status.type === "running", children: /* @__PURE__ */ jsx(Component, { type: "text", text: "", status }) });
};
var COMPLETE_STATUS = Object.freeze({
  type: "complete"
});
var EmptyPartsImpl = ({ components }) => {
  const status = useAssistantState(
    (s) => s.message.status ?? COMPLETE_STATUS
  );
  if (components?.Empty) return /* @__PURE__ */ jsx(components.Empty, { status });
  return /* @__PURE__ */ jsx(
    EmptyPartFallback,
    {
      status,
      component: components?.Text ?? defaultComponents.Text
    }
  );
};
var EmptyParts = memo(
  EmptyPartsImpl,
  (prev, next) => prev.components?.Empty === next.components?.Empty && prev.components?.Text === next.components?.Text
);
var MessagePrimitiveParts = ({
  components
}) => {
  const contentLength = useAssistantState(
    ({ message }) => message.parts.length
  );
  const messageRanges = useMessagePartsGroups();
  const partsElements = useMemo(() => {
    if (contentLength === 0) {
      return /* @__PURE__ */ jsx(EmptyParts, { components });
    }
    return messageRanges.map((range) => {
      if (range.type === "single") {
        return /* @__PURE__ */ jsx(
          MessagePrimitivePartByIndex,
          {
            index: range.index,
            components
          },
          range.index
        );
      } else if (range.type === "toolGroup") {
        const ToolGroupComponent = components.ToolGroup ?? defaultComponents.ToolGroup;
        return /* @__PURE__ */ jsx(
          ToolGroupComponent,
          {
            startIndex: range.startIndex,
            endIndex: range.endIndex,
            children: Array.from(
              { length: range.endIndex - range.startIndex + 1 },
              (_, i) => /* @__PURE__ */ jsx(
                MessagePrimitivePartByIndex,
                {
                  index: range.startIndex + i,
                  components
                },
                i
              )
            )
          },
          `tool-${range.startIndex}`
        );
      } else {
        const ReasoningGroupComponent = components.ReasoningGroup ?? defaultComponents.ReasoningGroup;
        return /* @__PURE__ */ jsx(
          ReasoningGroupComponent,
          {
            startIndex: range.startIndex,
            endIndex: range.endIndex,
            children: Array.from(
              { length: range.endIndex - range.startIndex + 1 },
              (_, i) => /* @__PURE__ */ jsx(
                MessagePrimitivePartByIndex,
                {
                  index: range.startIndex + i,
                  components
                },
                i
              )
            )
          },
          `reasoning-${range.startIndex}`
        );
      }
    });
  }, [messageRanges, components, contentLength]);
  return /* @__PURE__ */ jsx(Fragment, { children: partsElements });
};
MessagePrimitiveParts.displayName = "MessagePrimitive.Parts";
export {
  MessagePrimitivePartByIndex,
  MessagePrimitiveParts
};
//# sourceMappingURL=MessageParts.js.map