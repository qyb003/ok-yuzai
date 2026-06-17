// src/utils/tap-store/store.ts
import {
  tapMemo,
  tapEffect,
  resource,
  createResource
} from "@assistant-ui/tap";
var asStore = resource(
  (element) => {
    const resource2 = tapMemo(
      () => createResource(element, true),
      [element.type]
    );
    tapEffect(() => {
      resource2.updateInput(element.props);
    });
    return resource2;
  }
);
export {
  asStore
};
//# sourceMappingURL=store.js.map