import { ThreadListItemStatus } from "../../types";
export type ThreadListItemClientState = {
    readonly id: string;
    readonly remoteId: string | undefined;
    readonly externalId: string | undefined;
    readonly title?: string | undefined;
    readonly status: ThreadListItemStatus;
};
export type ThreadListItemClientApi = {
    getState(): ThreadListItemClientState;
    switchTo(): void;
    rename(newTitle: string): void;
    archive(): void;
    unarchive(): void;
    delete(): void;
    generateTitle(): void;
    initialize(): Promise<{
        remoteId: string;
        externalId: string | undefined;
    }>;
    detach(): void;
};
//# sourceMappingURL=ThreadListItem.d.ts.map