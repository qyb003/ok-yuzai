import { commitRender, cleanupAllEffects } from "./commit.js";
import { withResourceFiber } from "./execution-context.js";
import { callResourceFn } from "./callResourceFn.js";
export function createResourceFiber(resource, scheduleRerender) {
    return {
        resource,
        scheduleRerender,
        cells: [],
        currentIndex: 0,
        renderContext: undefined,
        isFirstRender: true,
        isMounted: false,
        isNeverMounted: true,
    };
}
export function unmountResourceFiber(fiber) {
    // Clean up all effects
    fiber.isMounted = false;
    cleanupAllEffects(fiber);
}
export function renderResourceFiber(fiber, props) {
    const result = {
        commitTasks: [],
        props,
        state: undefined,
    };
    withResourceFiber(fiber, () => {
        fiber.renderContext = result;
        try {
            result.state = callResourceFn(fiber.resource, props);
        }
        finally {
            fiber.renderContext = undefined;
        }
    });
    return result;
}
export function commitResourceFiber(fiber, result) {
    fiber.isMounted = true;
    fiber.isNeverMounted = false;
    commitRender(result, fiber);
}
//# sourceMappingURL=ResourceFiber.js.map