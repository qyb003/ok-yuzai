// src/client/ModelContext.ts
import {
  createContext,
  tapContext,
  withContextProvider
} from "@assistant-ui/tap";
var ModelContextContext = createContext(null);
var withModelContextProvider = (modelContext, fn) => {
  return withContextProvider(ModelContextContext, modelContext, fn);
};
var tapModelContext = () => {
  const modelContext = tapContext(ModelContextContext);
  if (!modelContext)
    throw new Error("Model context is not available in this context");
  return modelContext;
};
export {
  tapModelContext,
  withModelContextProvider
};
//# sourceMappingURL=ModelContext.js.map