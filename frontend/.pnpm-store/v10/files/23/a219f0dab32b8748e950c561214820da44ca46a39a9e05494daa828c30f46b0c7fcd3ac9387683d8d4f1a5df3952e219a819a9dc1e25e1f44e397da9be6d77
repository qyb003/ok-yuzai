"use client";

// src/model-context/makeAssistantVisible.tsx
import {
  useEffect,
  useRef,
  forwardRef,
  useId,
  createContext,
  useContext
} from "react";
import { useAssistantApi } from "../context/react/AssistantApiContext.js";
import { useComposedRefs } from "@radix-ui/react-compose-refs";
import { tool } from "./tool.js";
import { jsx } from "react/jsx-runtime";
var click = tool({
  parameters: {
    type: "object",
    properties: {
      clickId: {
        type: "string"
      }
    },
    required: ["clickId"]
  },
  execute: async ({ clickId }) => {
    const escapedClickId = CSS.escape(clickId);
    const el = document.querySelector(`[data-click-id='${escapedClickId}']`);
    if (el instanceof HTMLElement) {
      el.click();
      await new Promise((resolve) => setTimeout(resolve, 2e3));
      return {};
    } else {
      return "Element not found";
    }
  }
});
var edit = tool({
  parameters: {
    type: "object",
    properties: {
      editId: {
        type: "string"
      },
      value: {
        type: "string"
      }
    },
    required: ["editId", "value"]
  },
  execute: async ({ editId, value }) => {
    const escapedEditId = CSS.escape(editId);
    const el = document.querySelector(`[data-edit-id='${escapedEditId}']`);
    if (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement) {
      el.value = value;
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
      await new Promise((resolve) => setTimeout(resolve, 2e3));
      return {};
    } else {
      return "Element not found";
    }
  }
});
var ReadableContext = createContext(false);
var makeAssistantVisible = (Component, config) => {
  const ReadableComponent = forwardRef(
    (props, outerRef) => {
      const isNestedReadable = useContext(ReadableContext);
      const clickId = useId();
      const componentRef = useRef(null);
      const api = useAssistantApi();
      const { clickable, editable } = config ?? {};
      useEffect(() => {
        return api.modelContext().register({
          getModelContext: () => {
            return {
              tools: {
                ...clickable ? { click } : {},
                ...editable ? { edit } : {}
              },
              system: !isNestedReadable ? componentRef.current?.outerHTML : void 0
            };
          }
        });
      }, [isNestedReadable, api, clickable, editable]);
      const ref = useComposedRefs(componentRef, outerRef);
      return /* @__PURE__ */ jsx(ReadableContext.Provider, { value: true, children: /* @__PURE__ */ jsx(
        Component,
        {
          ...props,
          ...config?.clickable ? { "data-click-id": clickId } : {},
          ...config?.editable ? { "data-edit-id": clickId } : {},
          ref
        }
      ) });
    }
  );
  ReadableComponent.displayName = Component.displayName;
  return ReadableComponent;
};
var makeAssistantVisible_default = makeAssistantVisible;
export {
  makeAssistantVisible_default as default,
  makeAssistantVisible
};
//# sourceMappingURL=makeAssistantVisible.js.map