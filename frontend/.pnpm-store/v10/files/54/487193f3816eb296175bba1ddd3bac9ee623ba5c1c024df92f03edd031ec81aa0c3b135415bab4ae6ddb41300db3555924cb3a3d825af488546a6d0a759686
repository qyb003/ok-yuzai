// src/devtools/DevToolsHooks.ts
var cachedHook;
var getHook = () => {
  if (cachedHook) {
    return cachedHook;
  }
  const createHook = () => ({
    apis: /* @__PURE__ */ new Map(),
    nextId: 0,
    listeners: /* @__PURE__ */ new Set()
  });
  if (typeof window === "undefined") {
    cachedHook = createHook();
    return cachedHook;
  }
  const existingHook = window.__ASSISTANT_UI_DEVTOOLS_HOOK__;
  if (existingHook) {
    cachedHook = existingHook;
    return existingHook;
  }
  const newHook = createHook();
  window.__ASSISTANT_UI_DEVTOOLS_HOOK__ = newHook;
  cachedHook = newHook;
  return newHook;
};
var DevToolsHooks = class _DevToolsHooks {
  static subscribe(listener) {
    const hook = getHook();
    hook.listeners.add(listener);
    return () => {
      hook.listeners.delete(listener);
    };
  }
  static clearEventLogs(apiId) {
    const hook = getHook();
    const entry = hook.apis.get(apiId);
    if (!entry) return;
    entry.logs = [];
    _DevToolsHooks.notifyListeners(apiId);
  }
  static getApis() {
    return getHook().apis;
  }
  static notifyListeners(apiId) {
    const hook = getHook();
    hook.listeners.forEach((listener) => listener(apiId));
  }
};
var DevToolsProviderApi = class _DevToolsProviderApi {
  static MAX_EVENT_LOGS_PER_API = 200;
  static register(api) {
    const hook = getHook();
    for (const entry2 of hook.apis.values()) {
      if (entry2.api === api) {
        return () => {
        };
      }
    }
    const apiId = hook.nextId++;
    const entry = {
      api,
      logs: []
    };
    const eventUnsubscribe = api.on?.("*", (e) => {
      const entry2 = hook.apis.get(apiId);
      if (!entry2) return;
      entry2.logs.push({
        time: /* @__PURE__ */ new Date(),
        event: e.event,
        data: e.payload
      });
      if (entry2.logs.length > _DevToolsProviderApi.MAX_EVENT_LOGS_PER_API) {
        entry2.logs = entry2.logs.slice(
          -_DevToolsProviderApi.MAX_EVENT_LOGS_PER_API
        );
      }
      _DevToolsProviderApi.notifyListeners(apiId);
    });
    const stateUnsubscribe = api.subscribe?.(() => {
      _DevToolsProviderApi.notifyListeners(apiId);
    });
    hook.apis.set(apiId, entry);
    _DevToolsProviderApi.notifyListeners(apiId);
    return () => {
      const hook2 = getHook();
      const entry2 = hook2.apis.get(apiId);
      if (!entry2) return;
      eventUnsubscribe?.();
      stateUnsubscribe?.();
      hook2.apis.delete(apiId);
      _DevToolsProviderApi.notifyListeners(apiId);
    };
  }
  static notifyListeners(apiId) {
    const hook = getHook();
    hook.listeners.forEach((listener) => listener(apiId));
  }
};
export {
  DevToolsHooks,
  DevToolsProviderApi
};
//# sourceMappingURL=DevToolsHooks.js.map