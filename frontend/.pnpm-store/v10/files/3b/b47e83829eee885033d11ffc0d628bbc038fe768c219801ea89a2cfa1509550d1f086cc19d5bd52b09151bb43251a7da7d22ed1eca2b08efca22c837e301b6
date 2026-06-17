// src/legacy-runtime/runtime-cores/assistant-transport/useConvertedState.ts
import { useMemo } from "react";
function useConvertedState(converter, agentState, pendingCommands, isSending, toolStatuses) {
  return useMemo(
    () => converter(agentState, { pendingCommands, isSending, toolStatuses }),
    [converter, agentState, pendingCommands, isSending, toolStatuses]
  );
}
export {
  useConvertedState
};
//# sourceMappingURL=useConvertedState.js.map