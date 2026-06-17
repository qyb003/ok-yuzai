"use client";

// src/legacy-runtime/runtime-cores/assistant-transport/useAssistantTransportRuntime.tsx
import {
  asAsyncIterableStream
} from "assistant-stream/utils";
import { useExternalStoreRuntime } from "../external-store/useExternalStoreRuntime.js";
import { useState, useRef, useMemo } from "react";
import {
  AssistantMessageAccumulator,
  DataStreamDecoder,
  AssistantTransportDecoder,
  unstable_createInitialMessage as createInitialMessage
} from "assistant-stream";
import { useCommandQueue } from "./commandQueue.js";
import { useRunManager } from "./runManager.js";
import { useConvertedState } from "./useConvertedState.js";
import { useToolInvocations } from "./useToolInvocations.js";
import { toAISDKTools, getEnabledTools, createRequestHeaders } from "./utils.js";
import { useRemoteThreadListRuntime } from "../remote-thread-list/useRemoteThreadListRuntime.js";
import { InMemoryThreadListAdapter } from "../remote-thread-list/adapter/in-memory.js";
import { useAssistantApi, useAssistantState } from "../../../context/react/index.js";
var symbolAssistantTransportExtras = Symbol("assistant-transport-extras");
var asAssistantTransportExtras = (extras) => {
  if (typeof extras !== "object" || extras == null || !(symbolAssistantTransportExtras in extras))
    throw new Error(
      "This method can only be called when you are using useAssistantTransportRuntime"
    );
  return extras;
};
var useAssistantTransportSendCommand = () => {
  const api = useAssistantApi();
  return (command) => {
    const extras = api.thread().getState().extras;
    const transportExtras = asAssistantTransportExtras(extras);
    transportExtras.sendCommand(command);
  };
};
function useAssistantTransportState(selector = (t) => t) {
  return useAssistantState(
    ({ thread }) => selector(asAssistantTransportExtras(thread.extras).state)
  );
}
var useAssistantTransportThreadRuntime = (options) => {
  const agentStateRef = useRef(options.initialState);
  const [, rerender] = useState(0);
  const resumeFlagRef = useRef(false);
  const commandQueue = useCommandQueue({
    onQueue: () => runManager.schedule()
  });
  const runManager = useRunManager({
    onRun: async (signal) => {
      const isResume = resumeFlagRef.current;
      resumeFlagRef.current = false;
      const commands = isResume ? [] : commandQueue.flush();
      if (commands.length === 0 && !isResume)
        throw new Error("No commands to send");
      const headers = await createRequestHeaders(options.headers);
      const context = runtime.thread.getModelContext();
      const response = await fetch(
        isResume ? options.resumeApi : options.api,
        {
          method: "POST",
          headers,
          body: JSON.stringify({
            commands,
            state: agentStateRef.current,
            system: context.system,
            tools: context.tools ? toAISDKTools(getEnabledTools(context.tools)) : void 0,
            ...context.callSettings,
            ...context.config,
            ...options.body
          }),
          signal
        }
      );
      options.onResponse?.(response);
      if (!response.ok) {
        throw new Error(`Status ${response.status}: ${await response.text()}`);
      }
      if (!response.body) {
        throw new Error("Response body is null");
      }
      const protocol = options.protocol ?? "data-stream";
      const decoder = protocol === "assistant-transport" ? new AssistantTransportDecoder() : new DataStreamDecoder();
      let err;
      const stream = response.body.pipeThrough(decoder).pipeThrough(
        new AssistantMessageAccumulator({
          initialMessage: createInitialMessage({
            unstable_state: agentStateRef.current ?? null
          }),
          throttle: isResume,
          onError: (error) => {
            err = error;
          }
        })
      );
      let markedDelivered = false;
      for await (const chunk of asAsyncIterableStream(stream)) {
        if (chunk.metadata.unstable_state === agentStateRef.current) continue;
        if (!markedDelivered) {
          commandQueue.markDelivered();
          markedDelivered = true;
        }
        agentStateRef.current = chunk.metadata.unstable_state;
        rerender((prev) => prev + 1);
      }
      if (err) {
        throw new Error(err);
      }
    },
    onFinish: options.onFinish,
    onCancel: () => {
      const cmds = [
        ...commandQueue.state.inTransit,
        ...commandQueue.state.queued
      ];
      commandQueue.reset();
      options.onCancel?.({
        commands: cmds,
        updateState: (updater) => {
          agentStateRef.current = updater(agentStateRef.current);
          rerender((prev) => prev + 1);
        }
      });
    },
    onError: async (error) => {
      const inTransitCmds = [...commandQueue.state.inTransit];
      const queuedCmds = [...commandQueue.state.queued];
      commandQueue.reset();
      try {
        await options.onError?.(error, {
          commands: inTransitCmds,
          updateState: (updater) => {
            agentStateRef.current = updater(agentStateRef.current);
            rerender((prev) => prev + 1);
          }
        });
      } finally {
        options.onCancel?.({
          commands: queuedCmds,
          updateState: (updater) => {
            agentStateRef.current = updater(agentStateRef.current);
            rerender((prev) => prev + 1);
          },
          error
        });
      }
    }
  });
  const [toolStatuses, setToolStatuses] = useState({});
  const pendingCommands = useMemo(
    () => [...commandQueue.state.inTransit, ...commandQueue.state.queued],
    [commandQueue.state]
  );
  const converted = useConvertedState(
    options.converter,
    agentStateRef.current,
    pendingCommands,
    runManager.isRunning,
    toolStatuses
  );
  const runtime = useExternalStoreRuntime({
    messages: converted.messages,
    state: converted.state,
    isRunning: converted.isRunning,
    adapters: options.adapters,
    extras: {
      [symbolAssistantTransportExtras]: true,
      sendCommand: (command) => {
        commandQueue.enqueue(command);
      },
      state: agentStateRef.current
    },
    onNew: async (message) => {
      if (message.role !== "user")
        throw new Error("Only user messages are supported");
      const parts = [];
      const content = [
        ...message.content,
        ...message.attachments?.flatMap((a) => a.content) ?? []
      ];
      for (const contentPart of content) {
        if (contentPart.type === "text") {
          parts.push({ type: "text", text: contentPart.text });
        } else if (contentPart.type === "image") {
          parts.push({ type: "image", image: contentPart.image });
        }
      }
      const command = {
        type: "add-message",
        message: {
          role: "user",
          parts
        }
      };
      commandQueue.enqueue(command);
    },
    onCancel: async () => {
      runManager.cancel();
      toolInvocations.abort();
    },
    onResume: async () => {
      if (!options.resumeApi)
        throw new Error("Must pass resumeApi to options to resume runs");
      resumeFlagRef.current = true;
      runManager.schedule();
    },
    onAddToolResult: async (toolOptions) => {
      const command = {
        type: "add-tool-result",
        toolCallId: toolOptions.toolCallId,
        result: toolOptions.result,
        toolName: toolOptions.toolName,
        isError: toolOptions.isError,
        ...toolOptions.artifact && { artifact: toolOptions.artifact }
      };
      commandQueue.enqueue(command);
    },
    onLoadExternalState: async (state) => {
      agentStateRef.current = state;
      toolInvocations.reset();
      rerender((prev) => prev + 1);
    }
  });
  const toolInvocations = useToolInvocations({
    state: converted,
    getTools: () => runtime.thread.getModelContext().tools,
    onResult: commandQueue.enqueue,
    setToolStatuses
  });
  return runtime;
};
var useAssistantTransportRuntime = (options) => {
  const runtime = useRemoteThreadListRuntime({
    runtimeHook: function RuntimeHook() {
      return useAssistantTransportThreadRuntime(options);
    },
    adapter: new InMemoryThreadListAdapter()
  });
  return runtime;
};
export {
  useAssistantTransportRuntime,
  useAssistantTransportSendCommand,
  useAssistantTransportState
};
//# sourceMappingURL=useAssistantTransportRuntime.js.map