"use client";

// src/legacy-runtime/runtime-cores/external-store/createMessageConverter.tsx
import { useAssistantApi, useAssistantState } from "../../../context/index.js";
import {
  useExternalMessageConverter,
  convertExternalMessages
} from "./external-message-converter.js";
import { getExternalStoreMessages } from "./getExternalStoreMessage.js";
var createMessageConverter = (callback) => {
  const result = {
    useThreadMessages: ({
      messages,
      isRunning,
      joinStrategy,
      metadata
    }) => {
      return useExternalMessageConverter({
        callback,
        messages,
        isRunning,
        joinStrategy,
        metadata
      });
    },
    toThreadMessages: (messages, isRunning = false, metadata = {}) => {
      return convertExternalMessages(messages, callback, isRunning, metadata);
    },
    toOriginalMessages: (input) => {
      const messages = getExternalStoreMessages(input);
      if (messages.length === 0) throw new Error("No original messages found");
      return messages;
    },
    toOriginalMessage: (input) => {
      const messages = result.toOriginalMessages(input);
      return messages[0];
    },
    useOriginalMessage: () => {
      const messageMessages = result.useOriginalMessages();
      const first = messageMessages[0];
      return first;
    },
    useOriginalMessages: () => {
      const api = useAssistantApi();
      const partMessages = useAssistantState((s) => {
        if (api.part.source) return getExternalStoreMessages(s.part);
        return void 0;
      });
      const messageMessages = useAssistantState(
        ({ message }) => getExternalStoreMessages(message)
      );
      const messages = partMessages ?? messageMessages;
      if (messages.length === 0) throw new Error("No original messages found");
      return messages;
    }
  };
  return result;
};
export {
  createMessageConverter
};
//# sourceMappingURL=createMessageConverter.js.map