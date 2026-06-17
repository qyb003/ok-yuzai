import { createResourceFiber, unmountResourceFiber, renderResourceFiber, commitResourceFiber, } from "./ResourceFiber.js";
import { flushSync, UpdateScheduler } from "./scheduler.js";
import { tapRef } from "../hooks/tap-ref.js";
import { tapState } from "../hooks/tap-state.js";
import { tapMemo } from "../hooks/tap-memo.js";
import { tapEffect } from "../hooks/tap-effect.js";
import { resource } from "./resource.js";
import { tapResource } from "../hooks/tap-resource.js";
const HandleWrapperResource = resource((state) => {
    const [, setElement] = tapState(state.element);
    const value = tapResource(state.element);
    const subscribers = tapRef(new Set()).current;
    const valueRef = tapRef(value);
    tapEffect(() => {
        if (value !== valueRef.current) {
            valueRef.current = value;
            subscribers.forEach((callback) => callback());
        }
    });
    const handle = tapMemo(() => ({
        getState: () => valueRef.current,
        subscribe: (callback) => {
            subscribers.add(callback);
            return () => subscribers.delete(callback);
        },
        render: (element) => {
            const changed = state.element !== element;
            state.element = element;
            if (state.onRender(changed)) {
                setElement(element);
            }
        },
        unmount: state.onUnmount,
    }), []);
    return handle;
});
export const createResource = (element, { mount = true } = {}) => {
    let isMounted = mount;
    let render;
    const props = {
        element,
        onRender: (changed) => {
            if (isMounted)
                return changed;
            isMounted = true;
            flushSync(() => {
                if (changed) {
                    render = renderResourceFiber(fiber, props);
                }
                if (scheduler.isDirty)
                    return;
                commitResourceFiber(fiber, render);
            });
            return false;
        },
        onUnmount: () => {
            if (!isMounted)
                throw new Error("Resource not mounted");
            isMounted = false;
            unmountResourceFiber(fiber);
        },
    };
    const scheduler = new UpdateScheduler(() => {
        render = renderResourceFiber(fiber, props);
        if (scheduler.isDirty || !isMounted)
            return;
        commitResourceFiber(fiber, render);
    });
    const fiber = createResourceFiber((HandleWrapperResource), () => scheduler.markDirty());
    flushSync(() => {
        scheduler.markDirty();
    });
    return render.state;
};
//# sourceMappingURL=createResource.js.map