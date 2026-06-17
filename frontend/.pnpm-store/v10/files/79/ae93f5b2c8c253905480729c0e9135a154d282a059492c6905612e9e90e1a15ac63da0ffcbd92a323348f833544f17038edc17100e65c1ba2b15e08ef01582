export interface ApiObject {
    [key: string]: ((...args: any[]) => any) | ApiObject;
}
export declare const tapApi: <TApi extends ApiObject & {
    getState: () => any;
}>(api: TApi, options?: {
    key?: string | undefined;
}) => {
    key: string | undefined;
    state: any;
    api: TApi;
};
//# sourceMappingURL=tap-api.d.ts.map