// src/client/util-hooks/tapLookupResources.ts
import { tapResources } from "@assistant-ui/tap";
var tapLookupResources = (elements) => {
  const resources = tapResources(elements);
  return {
    state: resources.map((r) => r.state),
    api: (lookup) => {
      const value = "index" in lookup ? resources[lookup.index]?.api : resources.find((r) => r.key === lookup.key)?.api;
      if (!value) {
        throw new Error(
          `tapLookupResources: Resource not found for lookup: ${JSON.stringify(lookup)}`
        );
      }
      return value;
    }
  };
};
export {
  tapLookupResources
};
//# sourceMappingURL=tapLookupResources.js.map