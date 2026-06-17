"use client";

// src/primitives/reasoning/useScrollLock.tsx
import { useCallback, useEffect, useRef } from "react";
var useScrollLock = (animatedElementRef, animationDuration) => {
  const scrollContainerRef = useRef(null);
  const cleanupRef = useRef(null);
  useEffect(() => {
    return () => {
      cleanupRef.current?.();
    };
  }, []);
  const lockScroll = useCallback(() => {
    cleanupRef.current?.();
    (function findScrollableAncestor() {
      if (scrollContainerRef.current || !animatedElementRef.current) return;
      let el = animatedElementRef.current;
      while (el) {
        const { overflowY } = getComputedStyle(el);
        if (overflowY === "scroll" || overflowY === "auto") {
          scrollContainerRef.current = el;
          break;
        }
        el = el.parentElement;
      }
    })();
    const scrollContainer = scrollContainerRef.current;
    if (!scrollContainer) return;
    const scrollPosition = scrollContainer.scrollTop;
    const scrollbarWidth = scrollContainer.style.scrollbarWidth;
    scrollContainer.style.scrollbarWidth = "none";
    const resetPosition = () => scrollContainer.scrollTop = scrollPosition;
    scrollContainer.addEventListener("scroll", resetPosition);
    const timeoutId = setTimeout(() => {
      scrollContainer.removeEventListener("scroll", resetPosition);
      scrollContainer.style.scrollbarWidth = scrollbarWidth;
      cleanupRef.current = null;
    }, animationDuration);
    cleanupRef.current = () => {
      clearTimeout(timeoutId);
      scrollContainer.removeEventListener("scroll", resetPosition);
      scrollContainer.style.scrollbarWidth = scrollbarWidth;
    };
  }, [animationDuration, animatedElementRef]);
  return lockScroll;
};
export {
  useScrollLock
};
//# sourceMappingURL=useScrollLock.js.map