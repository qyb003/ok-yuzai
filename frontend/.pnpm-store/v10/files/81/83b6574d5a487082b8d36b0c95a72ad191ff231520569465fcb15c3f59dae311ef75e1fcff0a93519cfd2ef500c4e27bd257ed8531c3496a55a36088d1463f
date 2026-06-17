import { ExtractResourceOutput, RenderResult, ResourceElement, ResourceFiber } from "../core/types.js";
export type TapResourcesRenderResult<R, K extends string | number | symbol> = {
    add: [K, ResourceFiber<R, any>][];
    remove: K[];
    commit: [K, RenderResult][];
    return: Record<K, R>;
};
export declare function tapResources<M extends Record<string | number | symbol, any>, E extends ResourceElement<any, any>>(map: M, getElement: (t: M[keyof M], key: keyof M) => E, getElementDeps: any[]): {
    [K in keyof M]: ExtractResourceOutput<E>;
};
//# sourceMappingURL=tap-resources.d.ts.map