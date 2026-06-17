"use client";

// src/primitives/composer/ComposerInput.tsx
import { composeEventHandlers } from "@radix-ui/primitive";
import { useComposedRefs } from "@radix-ui/react-compose-refs";
import { Slot } from "@radix-ui/react-slot";
import {
  forwardRef,
  useCallback,
  useEffect,
  useRef
} from "react";
import TextareaAutosize from "react-textarea-autosize";
import { useEscapeKeydown } from "@radix-ui/react-use-escape-keydown";
import { useOnScrollToBottom } from "../../utils/hooks/useOnScrollToBottom.js";
import { useAssistantState, useAssistantApi } from "../../context/index.js";
import { jsx } from "react/jsx-runtime";
var ComposerPrimitiveInput = forwardRef(
  ({
    autoFocus = false,
    asChild,
    disabled: disabledProp,
    onChange,
    onKeyDown,
    onPaste,
    submitOnEnter = true,
    cancelOnEscape = true,
    unstable_focusOnRunStart = true,
    unstable_focusOnScrollToBottom = true,
    unstable_focusOnThreadSwitched = true,
    addAttachmentOnPaste = true,
    ...rest
  }, forwardedRef) => {
    const api = useAssistantApi();
    const value = useAssistantState(({ composer }) => {
      if (!composer.isEditing) return "";
      return composer.text;
    });
    const Component = asChild ? Slot : TextareaAutosize;
    const isDisabled = useAssistantState(({ thread }) => thread.isDisabled) || disabledProp;
    const textareaRef = useRef(null);
    const ref = useComposedRefs(forwardedRef, textareaRef);
    useEscapeKeydown((e) => {
      if (!cancelOnEscape) return;
      const composer = api.composer();
      if (composer.getState().canCancel) {
        composer.cancel();
        e.preventDefault();
      }
    });
    const handleKeyPress = (e) => {
      if (isDisabled || !submitOnEnter) return;
      if (e.nativeEvent.isComposing) return;
      if (e.key === "Enter" && e.shiftKey === false) {
        const isRunning = api.thread().getState().isRunning;
        if (!isRunning) {
          e.preventDefault();
          textareaRef.current?.closest("form")?.requestSubmit();
        }
      }
    };
    const handlePaste = async (e) => {
      if (!addAttachmentOnPaste) return;
      const threadCapabilities = api.thread().getState().capabilities;
      const files = Array.from(e.clipboardData?.files || []);
      if (threadCapabilities.attachments && files.length > 0) {
        try {
          e.preventDefault();
          await Promise.all(
            files.map((file) => api.composer().addAttachment(file))
          );
        } catch (error) {
          console.error("Error adding attachment:", error);
        }
      }
    };
    const autoFocusEnabled = autoFocus && !isDisabled;
    const focus = useCallback(() => {
      const textarea = textareaRef.current;
      if (!textarea || !autoFocusEnabled) return;
      textarea.focus({ preventScroll: true });
      textarea.setSelectionRange(textarea.value.length, textarea.value.length);
    }, [autoFocusEnabled]);
    useEffect(() => focus(), [focus]);
    useOnScrollToBottom(() => {
      if (api.composer().getState().type === "thread" && unstable_focusOnScrollToBottom) {
        focus();
      }
    });
    useEffect(() => {
      if (api.composer().getState().type !== "thread" || !unstable_focusOnRunStart)
        return void 0;
      return api.on("thread.run-start", focus);
    }, [unstable_focusOnRunStart, focus, api]);
    useEffect(() => {
      if (api.composer().getState().type !== "thread" || !unstable_focusOnThreadSwitched)
        return void 0;
      return api.on("thread-list-item.switched-to", focus);
    }, [unstable_focusOnThreadSwitched, focus, api]);
    return /* @__PURE__ */ jsx(
      Component,
      {
        name: "input",
        value,
        ...rest,
        ref,
        disabled: isDisabled,
        onChange: composeEventHandlers(onChange, (e) => {
          if (!api.composer().getState().isEditing) return;
          api.composer().setText(e.target.value);
          api.flushSync();
        }),
        onKeyDown: composeEventHandlers(onKeyDown, handleKeyPress),
        onPaste: composeEventHandlers(onPaste, handlePaste)
      }
    );
  }
);
ComposerPrimitiveInput.displayName = "ComposerPrimitive.Input";
export {
  ComposerPrimitiveInput
};
//# sourceMappingURL=ComposerInput.js.map