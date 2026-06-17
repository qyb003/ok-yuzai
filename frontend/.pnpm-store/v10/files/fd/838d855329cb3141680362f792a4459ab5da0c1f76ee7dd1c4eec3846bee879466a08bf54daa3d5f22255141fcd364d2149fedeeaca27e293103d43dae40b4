"use client";

// src/legacy-runtime/runtime-cores/remote-thread-list/RemoteThreadListHookInstanceManager.tsx
import {
  useCallback,
  useRef,
  useEffect,
  memo
} from "react";
import { create } from "zustand";
import { useAssistantApi, ThreadListItemByIdProvider } from "../../../context/index.js";
import { BaseSubscribable } from "./BaseSubscribable.js";
import { jsx } from "react/jsx-runtime";
var RemoteThreadListHookInstanceManager = class extends BaseSubscribable {
  useRuntimeHook;
  instances = /* @__PURE__ */ new Map();
  useAliveThreadsKeysChanged = create(() => ({}));
  constructor(runtimeHook) {
    super();
    this.useRuntimeHook = create(() => ({ useRuntime: runtimeHook }));
  }
  startThreadRuntime(threadId) {
    if (!this.instances.has(threadId)) {
      this.instances.set(threadId, {});
      this.useAliveThreadsKeysChanged.setState({}, true);
    }
    return new Promise((resolve, reject) => {
      const callback = () => {
        const instance = this.instances.get(threadId);
        if (!instance) {
          dispose();
          reject(new Error("Thread was deleted before runtime was started"));
        } else if (!instance.runtime) {
          return;
        } else {
          dispose();
          resolve(instance.runtime);
        }
      };
      const dispose = this.subscribe(callback);
      callback();
    });
  }
  getThreadRuntimeCore(threadId) {
    const instance = this.instances.get(threadId);
    if (!instance) return void 0;
    return instance.runtime;
  }
  stopThreadRuntime(threadId) {
    this.instances.delete(threadId);
    this.useAliveThreadsKeysChanged.setState({}, true);
  }
  setRuntimeHook(newRuntimeHook) {
    const prevRuntimeHook = this.useRuntimeHook.getState().useRuntime;
    if (prevRuntimeHook !== newRuntimeHook) {
      this.useRuntimeHook.setState({ useRuntime: newRuntimeHook }, true);
    }
  }
  _InnerActiveThreadProvider = ({ threadId }) => {
    const { useRuntime } = this.useRuntimeHook();
    const runtime = useRuntime();
    const threadBinding = runtime.thread.__internal_threadBinding;
    const updateRuntime = useCallback(() => {
      const aliveThread = this.instances.get(threadId);
      if (!aliveThread)
        throw new Error("Thread not found. This is a bug in assistant-ui.");
      aliveThread.runtime = threadBinding.getState();
      this._notifySubscribers();
    }, [threadId, threadBinding]);
    const isMounted = useRef(false);
    if (!isMounted.current) {
      updateRuntime();
    }
    useEffect(() => {
      isMounted.current = true;
      updateRuntime();
      return threadBinding.outerSubscribe(updateRuntime);
    }, [threadBinding, updateRuntime]);
    const api = useAssistantApi();
    useEffect(() => {
      return runtime.threads.main.unstable_on("initialize", () => {
        const state = api.threadListItem().getState();
        if (state.status === "new") {
          api.threadListItem().initialize();
          const dispose = runtime.thread.unstable_on("run-end", () => {
            dispose();
            api.threadListItem().generateTitle();
          });
        }
      });
    }, [runtime, api]);
    return null;
  };
  _OuterActiveThreadProvider = memo(({ threadId, provider: Provider }) => {
    return /* @__PURE__ */ jsx(ThreadListItemByIdProvider, { id: threadId, children: /* @__PURE__ */ jsx(Provider, { children: /* @__PURE__ */ jsx(this._InnerActiveThreadProvider, { threadId }) }) });
  });
  __internal_RenderThreadRuntimes = ({ provider }) => {
    this.useAliveThreadsKeysChanged();
    return Array.from(this.instances.keys()).map((threadId) => /* @__PURE__ */ jsx(
      this._OuterActiveThreadProvider,
      {
        threadId,
        provider
      },
      threadId
    ));
  };
};
export {
  RemoteThreadListHookInstanceManager
};
//# sourceMappingURL=RemoteThreadListHookInstanceManager.js.map