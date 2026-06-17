import type { tapEffect } from "../hooks/tap-effect.js";
import type { tapState } from "../hooks/tap-state.js";
import { fnSymbol } from "./callResourceFn.js";
export type ResourceElement<R, P = any> = {
    type: Resource<R, P> & {
        [fnSymbol]: (props: P) => R;
    };
    props: P;
};
type ResourceArgs<P> = undefined extends P ? [props?: P] : [props: P];
export type Resource<R, P> = (...args: ResourceArgs<P>) => ResourceElement<R, P>;
export type ContravariantResource<R, P> = (...args: ResourceArgs<P>) => ResourceElement<R>;
export type ExtractResourceOutput<T> = T extends ResourceElement<infer R, any> ? R : never;
export type Cell = {
    type: "state";
    value: any;
    set: (updater: tapState.StateUpdater<any>) => void;
} | {
    type: "effect";
    mounted: boolean;
    cleanup?: tapEffect.Destructor | undefined;
    deps?: readonly unknown[] | undefined;
};
export interface EffectTask {
    effect: tapEffect.EffectCallback;
    deps?: readonly unknown[] | undefined;
    cellIndex: number;
}
export interface RenderResult {
    state: any;
    props: any;
    commitTasks: EffectTask[];
}
export interface ResourceFiber<R, P> {
    readonly scheduleRerender: () => void;
    readonly resource: Resource<R, P>;
    cells: Cell[];
    currentIndex: number;
    renderContext: RenderResult | undefined;
    isMounted: boolean;
    isFirstRender: boolean;
    isNeverMounted: boolean;
}
export {};
//# sourceMappingURL=types.d.ts.map