// src/types/EventTypes.ts
var normalizeEventSelector = (selector) => {
  if (typeof selector === "string") {
    const source = selector.split(".")[0];
    return {
      scope: source,
      event: selector
    };
  }
  return {
    scope: selector.scope,
    event: selector.event
  };
};
var checkEventScope = (expectedScope, scope, _event) => {
  return scope === expectedScope;
};
export {
  checkEventScope,
  normalizeEventSelector
};
//# sourceMappingURL=EventTypes.js.map