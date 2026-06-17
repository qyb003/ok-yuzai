import { ResourceElement } from "@assistant-ui/tap";
import { ThreadListClientApi, ThreadListClientState } from "./types/ThreadList";
import { AssistantApi } from "../context/react/AssistantApiContext";
import { ToolsApi, ToolsState } from "./types/Tools";
import { ModelContextApi, ModelContextState } from "./types/ModelContext";
export type AssistantClientProps = {
    threads: ResourceElement<{
        state: ThreadListClientState;
        api: ThreadListClientApi;
    }>;
    modelContext?: ResourceElement<{
        state: ModelContextState;
        api: ModelContextApi;
    }>;
    tools?: ResourceElement<{
        state: ToolsState;
        api: ToolsApi;
    }> | undefined;
};
export declare const useAssistantClient: (props: AssistantClientProps) => AssistantApi;
//# sourceMappingURL=AssistantClient.d.ts.map