import { tapRef } from "./tap-ref.js";
import { depsShallowEqual } from "./depsShallowEqual.js";
export const tapMemo = (fn, deps) => {
    const dataRef = tapRef();
    if (!dataRef.current) {
        dataRef.current = { value: fn(), deps };
    }
    if (!depsShallowEqual(dataRef.current.deps, deps)) {
        dataRef.current.value = fn();
        dataRef.current.deps = deps;
    }
    return dataRef.current.value;
};
//# sourceMappingURL=tap-memo.js.map