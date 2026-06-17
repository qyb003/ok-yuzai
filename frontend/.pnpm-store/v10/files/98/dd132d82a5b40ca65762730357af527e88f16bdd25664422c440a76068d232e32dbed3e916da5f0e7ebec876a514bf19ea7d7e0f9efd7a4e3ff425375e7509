// src/legacy-runtime/runtime-cores/remote-thread-list/adapter/in-memory.tsx
var InMemoryThreadListAdapter = class {
  list() {
    return Promise.resolve({
      threads: []
    });
  }
  rename() {
    return Promise.resolve();
  }
  archive() {
    return Promise.resolve();
  }
  unarchive() {
    return Promise.resolve();
  }
  delete() {
    return Promise.resolve();
  }
  initialize(threadId) {
    return Promise.resolve({ remoteId: threadId, externalId: void 0 });
  }
  generateTitle() {
    return Promise.resolve(new ReadableStream());
  }
  fetch(_threadId) {
    return Promise.reject(new Error("Thread not found"));
  }
};
export {
  InMemoryThreadListAdapter
};
//# sourceMappingURL=in-memory.js.map