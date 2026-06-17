import { ThreadListRuntimeCore } from "../core/ThreadListRuntimeCore";
import { BaseSubscribable } from "../remote-thread-list/BaseSubscribable";
import { LocalThreadRuntimeCore } from "./LocalThreadRuntimeCore";
export type LocalThreadFactory = () => LocalThreadRuntimeCore;
export declare class LocalThreadListRuntimeCore extends BaseSubscribable implements ThreadListRuntimeCore {
    private _mainThread;
    constructor(_threadFactory: LocalThreadFactory);
    get isLoading(): boolean;
    getMainThreadRuntimeCore(): LocalThreadRuntimeCore;
    get newThreadId(): string;
    get threadIds(): readonly string[];
    get archivedThreadIds(): readonly string[];
    get mainThreadId(): string;
    get threadData(): Readonly<{
        __DEFAULT_ID__: {
            id: string;
            remoteId: undefined;
            externalId: undefined;
            status: "regular";
            title: undefined;
        };
    }>;
    getThreadRuntimeCore(): never;
    getLoadThreadsPromise(): Promise<void>;
    getItemById(threadId: string): {
        status: "regular";
        id: string;
        remoteId: string;
        externalId: undefined;
        title: undefined;
        isMain: boolean;
    };
    switchToThread(): Promise<void>;
    switchToNewThread(): Promise<void>;
    rename(): Promise<void>;
    archive(): Promise<void>;
    detach(): Promise<void>;
    unarchive(): Promise<void>;
    delete(): Promise<void>;
    initialize(threadId: string): Promise<{
        remoteId: string;
        externalId: string | undefined;
    }>;
    generateTitle(): never;
}
//# sourceMappingURL=LocalThreadListRuntimeCore.d.ts.map