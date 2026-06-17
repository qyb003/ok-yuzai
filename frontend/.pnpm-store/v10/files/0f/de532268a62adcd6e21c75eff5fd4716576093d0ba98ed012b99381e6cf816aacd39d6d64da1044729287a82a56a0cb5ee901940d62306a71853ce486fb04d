"use client";

// src/legacy-runtime/cloud/useCloudThreadListRuntime.tsx
import { useRemoteThreadListRuntime } from "../runtime-cores/remote-thread-list/useRemoteThreadListRuntime.js";
import { useCloudThreadListAdapter } from "../runtime-cores/remote-thread-list/adapter/cloud.js";
var useCloudThreadListRuntime = ({
  runtimeHook,
  ...adapterOptions
}) => {
  const adapter = useCloudThreadListAdapter(adapterOptions);
  const runtime = useRemoteThreadListRuntime({
    runtimeHook,
    adapter
  });
  return runtime;
};
export {
  useCloudThreadListRuntime
};
//# sourceMappingURL=useCloudThreadListRuntime.js.map