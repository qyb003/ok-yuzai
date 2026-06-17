import { ResourceElement } from "./types.js";
export declare namespace createResource {
    type Unsubscribe = () => void;
    interface Handle<R, P> {
        getState(): R;
        subscribe(callback: () => void): Unsubscribe;
        render(element: ResourceElement<R, P>): void;
        unmount(): void;
    }
}
export declare const createResource: <R, P>(element: ResourceElement<R, P>, { mount }?: {
    mount?: boolean;
}) => createResource.Handle<R, P>;
//# sourceMappingURL=createResource.d.ts.map