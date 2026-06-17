// src/legacy-runtime/client/EventManagerRuntimeClient.ts
import { resource, tapMemo } from "@assistant-ui/tap";
var EventManager = resource(() => {
  const events = tapMemo(() => {
    const listeners = /* @__PURE__ */ new Map();
    return {
      on: (event, callback) => {
        if (!listeners.has(event)) {
          listeners.set(event, /* @__PURE__ */ new Set());
        }
        const eventListeners = listeners.get(event);
        eventListeners.add(callback);
        return () => {
          eventListeners.delete(callback);
          if (eventListeners.size === 0) {
            listeners.delete(event);
          }
        };
      },
      emit: (event, payload) => {
        const eventListeners = listeners.get(event);
        const wildcardListeners = listeners.get("*");
        if (!eventListeners && !wildcardListeners) return;
        queueMicrotask(() => {
          if (eventListeners) {
            for (const callback of eventListeners) {
              callback(payload);
            }
          }
          if (wildcardListeners) {
            for (const callback of wildcardListeners) {
              callback({ event, payload });
            }
          }
        });
      }
    };
  }, []);
  return events;
});
export {
  EventManager
};
//# sourceMappingURL=EventManagerRuntimeClient.js.map