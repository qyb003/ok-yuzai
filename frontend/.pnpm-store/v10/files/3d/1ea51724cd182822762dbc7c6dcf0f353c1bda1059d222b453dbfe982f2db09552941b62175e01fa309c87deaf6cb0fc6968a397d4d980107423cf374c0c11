// src/utils/tap-store/derived-scopes.ts
import { resource, tapEffect } from "@assistant-ui/tap";
import { tapMemo, tapRef, tapResource, tapResources } from "@assistant-ui/tap";
import { createAssistantApiField } from "../../context/react/AssistantApiContext.js";
var DerivedScope = resource(
  (config) => {
    const getRef = tapRef(config.get);
    tapEffect(() => {
      getRef.current = config.get;
    });
    return tapMemo(() => {
      return createAssistantApiField({
        source: config.source,
        query: config.query,
        get: () => getRef.current()
      });
    }, [config.source, JSON.stringify(config.query)]);
  }
);
var ScopeFieldWithNameResource = resource(
  (config) => {
    const field = tapResource(config.scopeElement);
    return tapMemo(
      () => [config.fieldName, field],
      [config.fieldName, field]
    );
  }
);
var DerivedScopes = resource(
  (scopes) => {
    const { on, subscribe, flushSync, ...scopeFields } = scopes;
    const callbacksRef = tapRef({ on, subscribe, flushSync });
    tapEffect(() => {
      callbacksRef.current = { on, subscribe, flushSync };
    });
    const results = tapResources(
      Object.entries(scopeFields).map(
        ([fieldName, scopeElement]) => ScopeFieldWithNameResource(
          {
            fieldName,
            scopeElement
          },
          { key: fieldName }
        )
      )
    );
    return tapMemo(() => {
      const result = Object.fromEntries(results);
      const {
        on: onCb,
        subscribe: subCb,
        flushSync: flushCb
      } = callbacksRef.current;
      if (onCb) {
        result.on = (selector, callback) => onCb(selector, callback);
      }
      if (subCb) result.subscribe = (listener) => subCb(listener);
      if (flushCb) result.flushSync = () => flushCb();
      return result;
    }, [...results]);
  }
);
export {
  DerivedScope,
  DerivedScopes
};
//# sourceMappingURL=derived-scopes.js.map