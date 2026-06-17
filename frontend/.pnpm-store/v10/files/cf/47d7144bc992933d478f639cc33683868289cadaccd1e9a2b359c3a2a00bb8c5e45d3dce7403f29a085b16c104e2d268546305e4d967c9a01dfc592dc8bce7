import { getCurrentResourceFiber } from "../core/execution-context.js";
const rerender = (fiber) => {
    if (fiber.renderContext) {
        throw new Error("Resource updated during render");
    }
    if (fiber.isMounted) {
        // Only schedule rerender if currently mounted
        fiber.scheduleRerender();
    }
    else if (fiber.isNeverMounted) {
        throw new Error("Resource updated before mount");
    }
};
function getStateCell(initialValue) {
    const fiber = getCurrentResourceFiber();
    const index = fiber.currentIndex++;
    // Check if we're trying to use more hooks than in previous renders
    if (!fiber.isFirstRender && index >= fiber.cells.length) {
        throw new Error("Rendered more hooks than during the previous render. " +
            "Hooks must be called in the exact same order in every render.");
    }
    if (!fiber.cells[index]) {
        // Initialize the value immediately
        const value = typeof initialValue === "function"
            ? initialValue()
            : initialValue;
        const cell = {
            type: "state",
            value,
            set: (updater) => {
                const currentValue = cell.value;
                const nextValue = typeof updater === "function"
                    ? updater(currentValue)
                    : updater;
                if (!Object.is(currentValue, nextValue)) {
                    cell.value = nextValue;
                    rerender(fiber);
                }
            },
        };
        fiber.cells[index] = cell;
    }
    const cell = fiber.cells[index];
    if (cell.type !== "state") {
        throw new Error("Hook order changed between renders");
    }
    return cell;
}
export function tapState(initial) {
    const cell = getStateCell(initial);
    return [cell.value, cell.set];
}
//# sourceMappingURL=tap-state.js.map