"use client";

// src/primitives/composer/ComposerAddAttachment.tsx
import {
  createActionButton
} from "../../utils/createActionButton.js";
import { useCallback } from "react";
import { useAssistantState, useAssistantApi } from "../../context/index.js";
var useComposerAddAttachment = ({
  multiple = true
} = {}) => {
  const disabled = useAssistantState(({ composer }) => !composer.isEditing);
  const api = useAssistantApi();
  const callback = useCallback(() => {
    const input = document.createElement("input");
    input.type = "file";
    input.multiple = multiple;
    input.hidden = true;
    const attachmentAccept = api.composer().getState().attachmentAccept;
    if (attachmentAccept !== "*") {
      input.accept = attachmentAccept;
    }
    document.body.appendChild(input);
    input.onchange = (e) => {
      const fileList = e.target.files;
      if (!fileList) return;
      for (const file of fileList) {
        api.composer().addAttachment(file);
      }
      document.body.removeChild(input);
    };
    input.oncancel = () => {
      if (!input.files || input.files.length === 0) {
        document.body.removeChild(input);
      }
    };
    input.click();
  }, [api, multiple]);
  if (disabled) return null;
  return callback;
};
var ComposerPrimitiveAddAttachment = createActionButton(
  "ComposerPrimitive.AddAttachment",
  useComposerAddAttachment,
  ["multiple"]
);
export {
  ComposerPrimitiveAddAttachment
};
//# sourceMappingURL=ComposerAddAttachment.js.map