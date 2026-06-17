"use client";

// src/context/providers/PartByIndexProvider.tsx
import {
  AssistantProvider,
  useAssistantApi,
  useExtendedAssistantApi
} from "../react/AssistantApiContext.js";
import { DerivedScope } from "../../utils/tap-store/derived-scopes.js";
import { jsx } from "react/jsx-runtime";
var PartByIndexProvider = ({ index, children }) => {
  const baseApi = useAssistantApi();
  const api = useExtendedAssistantApi({
    part: DerivedScope({
      source: "message",
      query: { type: "index", index },
      get: () => baseApi.message().part({ index })
    })
  });
  return /* @__PURE__ */ jsx(AssistantProvider, { api, children });
};
export {
  PartByIndexProvider
};
//# sourceMappingURL=PartByIndexProvider.js.map