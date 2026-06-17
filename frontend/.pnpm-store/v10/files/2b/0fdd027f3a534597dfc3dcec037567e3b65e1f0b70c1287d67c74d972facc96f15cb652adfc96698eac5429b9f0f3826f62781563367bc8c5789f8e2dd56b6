const contextValue = Symbol("tap.Context");
export const createContext = (defaultValue) => {
    return {
        [contextValue]: defaultValue,
    };
};
export const withContextProvider = (context, value, fn) => {
    const previousValue = context[contextValue];
    context[contextValue] = value;
    try {
        return fn();
    }
    finally {
        context[contextValue] = previousValue;
    }
};
export const tapContext = (context) => {
    return context[contextValue];
};
//# sourceMappingURL=context.js.map