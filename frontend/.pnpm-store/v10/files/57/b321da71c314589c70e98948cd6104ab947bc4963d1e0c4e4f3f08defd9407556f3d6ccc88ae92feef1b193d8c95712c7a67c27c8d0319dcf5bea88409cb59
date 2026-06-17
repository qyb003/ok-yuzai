// src/legacy-runtime/util-hooks/tapSubscribable.ts
import { tapState, tapEffect } from "@assistant-ui/tap";
var tapSubscribable = (subscribable) => {
  const [, setState] = tapState(subscribable.getState);
  tapEffect(() => {
    setState(subscribable.getState());
    return subscribable.subscribe(() => {
      setState(subscribable.getState());
    });
  }, [subscribable]);
  return subscribable.getState();
};
export {
  tapSubscribable
};
//# sourceMappingURL=tapSubscribable.js.map