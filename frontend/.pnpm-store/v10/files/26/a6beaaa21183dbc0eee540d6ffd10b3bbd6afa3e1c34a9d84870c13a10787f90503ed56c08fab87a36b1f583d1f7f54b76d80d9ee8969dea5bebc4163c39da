import { useEffect, useLayoutEffect, useMemo, useState } from "react";
import { createResourceFiber, unmountResourceFiber, renderResourceFiber, commitResourceFiber, } from "../core/ResourceFiber.js";
const shouldAvoidLayoutEffect = globalThis.__ASSISTANT_UI_DISABLE_LAYOUT_EFFECT__ === true;
const useIsomorphicLayoutEffect = shouldAvoidLayoutEffect
    ? useEffect
    : useLayoutEffect;
export function useResource(element) {
    const [, rerender] = useState({});
    const fiber = useMemo(() => createResourceFiber(element.type, () => rerender({})), [element.type]);
    const result = renderResourceFiber(fiber, element.props);
    useIsomorphicLayoutEffect(() => {
        return () => unmountResourceFiber(fiber);
    }, [fiber]);
    useIsomorphicLayoutEffect(() => {
        commitResourceFiber(fiber, result);
    });
    return result.state;
}
//# sourceMappingURL=use-resource.js.map