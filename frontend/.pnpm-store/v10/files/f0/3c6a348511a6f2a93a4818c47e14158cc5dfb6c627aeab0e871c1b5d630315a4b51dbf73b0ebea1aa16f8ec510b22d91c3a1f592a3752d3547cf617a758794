"use client";

// src/context/providers/AttachmentByIndexProvider.tsx
import {
  AssistantProvider,
  useAssistantApi,
  useExtendedAssistantApi
} from "../react/AssistantApiContext.js";
import { DerivedScope } from "../../utils/tap-store/derived-scopes.js";
import { jsx } from "react/jsx-runtime";
var MessageAttachmentByIndexProvider = ({ index, children }) => {
  const baseApi = useAssistantApi();
  const api = useExtendedAssistantApi({
    attachment: DerivedScope({
      source: "message",
      query: { type: "index", index },
      get: () => baseApi.message().attachment({ index })
    })
  });
  return /* @__PURE__ */ jsx(AssistantProvider, { api, children });
};
var ComposerAttachmentByIndexProvider = ({ index, children }) => {
  const baseApi = useAssistantApi();
  const api = useExtendedAssistantApi({
    attachment: DerivedScope({
      source: "composer",
      query: { type: "index", index },
      get: () => baseApi.composer().attachment({ index })
    })
  });
  return /* @__PURE__ */ jsx(AssistantProvider, { api, children });
};
export {
  ComposerAttachmentByIndexProvider,
  MessageAttachmentByIndexProvider
};
//# sourceMappingURL=AttachmentByIndexProvider.js.map