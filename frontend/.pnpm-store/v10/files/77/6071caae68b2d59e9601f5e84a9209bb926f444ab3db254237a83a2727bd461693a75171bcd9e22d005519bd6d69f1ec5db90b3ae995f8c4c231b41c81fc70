// src/legacy-runtime/client/AttachmentRuntimeClient.ts
import { resource } from "@assistant-ui/tap";
import { tapApi } from "../../utils/tap-store/index.js";
import { tapSubscribable } from "../util-hooks/tapSubscribable.js";
var AttachmentRuntimeClient = resource(
  ({ runtime }) => {
    const state = tapSubscribable(runtime);
    return tapApi(
      {
        getState: () => state,
        remove: runtime.remove,
        __internal_getRuntime: () => runtime
      },
      {
        key: state.id
      }
    );
  }
);
export {
  AttachmentRuntimeClient
};
//# sourceMappingURL=AttachmentRuntimeClient.js.map