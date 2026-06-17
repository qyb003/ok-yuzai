import { tapRef } from "./tap-ref.js";
import { tapEffect } from "./tap-effect.js";
/**
 * Creates a stable function reference that always calls the most recent version of the callback.
 * Similar to React's useEffectEvent hook.
 *
 * @param callback - The callback function to wrap
 * @returns A stable function reference that always calls the latest callback
 *
 * @example
 * ```typescript
 * const handleClick = tapEffectEvent((value: string) => {
 *   console.log(value);
 * });
 * // handleClick reference is stable, but always calls the latest version
 * ```
 */
export function tapEffectEvent(callback) {
    const callbackRef = tapRef(callback);
    tapEffect(() => {
        callbackRef.current = callback;
    });
    return callbackRef.current;
}
//# sourceMappingURL=tap-effect-event.js.map