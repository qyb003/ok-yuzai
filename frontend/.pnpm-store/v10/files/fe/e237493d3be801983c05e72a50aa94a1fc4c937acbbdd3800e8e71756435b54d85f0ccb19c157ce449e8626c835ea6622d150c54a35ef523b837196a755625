// src/client/ModelContextClient.ts
import { resource, tapState } from "@assistant-ui/tap";
import { tapApi } from "../utils/tap-store/index.js";
import { CompositeContextProvider } from "../utils/CompositeContextProvider.js";
var ModelContext = resource(() => {
  const [state] = tapState(() => ({}));
  const composite = new CompositeContextProvider();
  return tapApi({
    getState: () => state,
    getModelContext: () => composite.getModelContext(),
    subscribe: (callback) => composite.subscribe(callback),
    register: (provider) => composite.registerModelContextProvider(provider)
  });
});
export {
  ModelContext
};
//# sourceMappingURL=ModelContextClient.js.map