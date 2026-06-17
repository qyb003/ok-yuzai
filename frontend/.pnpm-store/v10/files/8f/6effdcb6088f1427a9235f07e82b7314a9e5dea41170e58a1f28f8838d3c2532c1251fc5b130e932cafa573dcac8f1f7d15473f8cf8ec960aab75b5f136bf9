import { tapEffect } from "./tap-effect.js";
import { tapMemo } from "./tap-memo.js";
import { tapState } from "./tap-state.js";
import { tapCallback } from "./tap-callback.js";
import { createResourceFiber, unmountResourceFiber, renderResourceFiber, commitResourceFiber, } from "../core/ResourceFiber.js";
export function tapResources(map, getElement, getElementDeps) {
    const [version, setVersion] = tapState(0);
    const rerender = tapCallback(() => setVersion((v) => v + 1), []);
    const [fibers] = tapState(() => new Map());
    const getElementMemo = tapMemo(() => getElement, getElementDeps);
    // Process each element
    const results = tapMemo(() => {
        const results = {
            remove: [],
            add: [],
            commit: [],
            return: {},
        };
        // Create/update fibers and render
        for (const key in map) {
            const value = map[key];
            const element = getElementMemo(value, key);
            let fiber = fibers.get(key);
            // Create new fiber if needed or type changed
            if (!fiber || fiber.resource !== element.type) {
                if (fiber)
                    results.remove.push(key);
                fiber = createResourceFiber(element.type, rerender);
                results.add.push([key, fiber]);
            }
            // Render with current props
            const renderResult = renderResourceFiber(fiber, element.props);
            results.commit.push([key, renderResult]);
            results.return[key] = renderResult.state;
        }
        // Clean up removed fibers (only if there might be stale ones)
        if (fibers.size >
            results.commit.length - results.add.length + results.remove.length) {
            for (const key of fibers.keys()) {
                if (!(key in map)) {
                    results.remove.push(key);
                }
            }
        }
        return results;
    }, [map, getElementMemo, version]);
    // Cleanup on unmount
    tapEffect(() => {
        return () => {
            for (const key of fibers.keys()) {
                unmountResourceFiber(fibers.get(key));
                fibers.delete(key);
            }
        };
    }, []);
    tapEffect(() => {
        for (const key of results.remove) {
            unmountResourceFiber(fibers.get(key));
            fibers.delete(key);
        }
        for (const [key, fiber] of results.add) {
            fibers.set(key, fiber);
        }
        for (const [key, result] of results.commit) {
            commitResourceFiber(fibers.get(key), result);
        }
    }, [results]);
    return results.return;
}
//# sourceMappingURL=tap-resources.js.map