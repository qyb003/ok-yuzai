// src/context/react/hooks/useAssistantState.tsx
import { useMemo, useSyncExternalStore, useDebugValue } from "react";
import {
  useAssistantApi
} from "../AssistantApiContext.js";
var ProxiedAssistantState = class {
  #api;
  constructor(api) {
    this.#api = api;
  }
  get threads() {
    return this.#api.threads().getState();
  }
  get tools() {
    return this.#api.tools().getState();
  }
  get threadListItem() {
    return this.#api.threadListItem().getState();
  }
  get thread() {
    return this.#api.thread().getState();
  }
  get composer() {
    return this.#api.composer().getState();
  }
  get message() {
    return this.#api.message().getState();
  }
  get part() {
    return this.#api.part().getState();
  }
  get attachment() {
    return this.#api.attachment().getState();
  }
};
var useAssistantState = (selector) => {
  const api = useAssistantApi();
  const proxiedState = useMemo(() => new ProxiedAssistantState(api), [api]);
  const slice = useSyncExternalStore(
    api.subscribe,
    () => selector(proxiedState),
    () => selector(proxiedState)
  );
  useDebugValue(slice);
  if (slice instanceof ProxiedAssistantState)
    throw new Error(
      "You tried to return the entire AssistantState. This is not supported due to technical limitations."
    );
  return slice;
};
export {
  useAssistantState
};
//# sourceMappingURL=useAssistantState.js.map