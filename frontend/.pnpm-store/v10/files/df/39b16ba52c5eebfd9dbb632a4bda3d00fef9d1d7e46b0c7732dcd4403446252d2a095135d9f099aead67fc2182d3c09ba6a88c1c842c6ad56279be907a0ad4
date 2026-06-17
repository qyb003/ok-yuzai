// src/legacy-runtime/runtime-cores/external-store/auto-status.tsx
var symbolAutoStatus = Symbol("autoStatus");
var AUTO_STATUS_RUNNING = Object.freeze(
  Object.assign({ type: "running" }, { [symbolAutoStatus]: true })
);
var AUTO_STATUS_COMPLETE = Object.freeze(
  Object.assign(
    {
      type: "complete",
      reason: "unknown"
    },
    { [symbolAutoStatus]: true }
  )
);
var AUTO_STATUS_PENDING = Object.freeze(
  Object.assign(
    {
      type: "requires-action",
      reason: "tool-calls"
    },
    { [symbolAutoStatus]: true }
  )
);
var AUTO_STATUS_INTERRUPT = Object.freeze(
  Object.assign(
    {
      type: "requires-action",
      reason: "interrupt"
    },
    { [symbolAutoStatus]: true }
  )
);
var isAutoStatus = (status) => status[symbolAutoStatus] === true;
var getAutoStatus = (isLast, isRunning, hasInterruptedToolCalls, hasPendingToolCalls, error) => {
  if (isLast && error) {
    return Object.assign(
      {
        type: "incomplete",
        reason: "error",
        error
      },
      { [symbolAutoStatus]: true }
    );
  }
  return isLast && isRunning ? AUTO_STATUS_RUNNING : hasInterruptedToolCalls ? AUTO_STATUS_INTERRUPT : hasPendingToolCalls ? AUTO_STATUS_PENDING : AUTO_STATUS_COMPLETE;
};
export {
  getAutoStatus,
  isAutoStatus
};
//# sourceMappingURL=auto-status.js.map