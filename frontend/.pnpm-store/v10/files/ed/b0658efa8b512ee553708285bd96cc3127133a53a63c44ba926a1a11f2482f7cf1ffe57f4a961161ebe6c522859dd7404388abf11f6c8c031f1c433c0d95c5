// src/client/EventContext.ts
import {
  createContext,
  tapContext,
  withContextProvider
} from "@assistant-ui/tap";
var EventsContext = createContext(null);
var withEventsProvider = (events, fn) => {
  return withContextProvider(EventsContext, events, fn);
};
var tapEvents = () => {
  const events = tapContext(EventsContext);
  if (!events) throw new Error("Events context is not available");
  return events;
};
export {
  tapEvents,
  withEventsProvider
};
//# sourceMappingURL=EventContext.js.map