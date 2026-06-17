import { tapEffect } from "./tap-effect.js";
import { createResourceFiber, unmountResourceFiber, renderResourceFiber, commitResourceFiber, } from "../core/ResourceFiber.js";
import { tapMemo } from "./tap-memo.js";
import { tapState } from "./tap-state.js";
export function tapResource(element, deps) {
    const [stateVersion, rerender] = tapState({});
    const fiber = tapMemo(() => createResourceFiber(element.type, () => rerender({})), [element.type]);
    const props = deps ? tapMemo(() => element.props, deps) : element.props;
    const result = tapMemo(() => renderResourceFiber(fiber, props), [fiber, props, stateVersion]);
    tapEffect(() => {
        return () => unmountResourceFiber(fiber);
    }, [fiber]);
    tapEffect(() => {
        commitResourceFiber(fiber, result);
    }, [fiber, result]);
    return result.state;
}
//# sourceMappingURL=tap-resource.js.map