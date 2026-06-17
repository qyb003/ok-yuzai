// src/utils/tap-store/tap-api.ts
import { tapEffect, tapMemo, tapRef } from "@assistant-ui/tap";
var ReadonlyApiHandler = class {
  constructor(getApi) {
    this.getApi = getApi;
  }
  get(_, prop) {
    return this.getApi()[prop];
  }
  ownKeys() {
    return Object.keys(this.getApi());
  }
  has(_, prop) {
    return prop in this.getApi();
  }
  getOwnPropertyDescriptor(_, prop) {
    return Object.getOwnPropertyDescriptor(this.getApi(), prop);
  }
  set() {
    return false;
  }
  defineProperty() {
    return false;
  }
  deleteProperty() {
    return false;
  }
};
var tapApi = (api, options) => {
  const ref = tapRef(api);
  tapEffect(() => {
    ref.current = api;
  });
  const apiProxy = tapMemo(
    () => new Proxy({}, new ReadonlyApiHandler(() => ref.current)),
    []
  );
  const key = options?.key;
  const state = api.getState();
  return tapMemo(
    () => ({
      key,
      state,
      api: apiProxy
    }),
    [state, key]
  );
};
export {
  tapApi
};
//# sourceMappingURL=tap-api.js.map