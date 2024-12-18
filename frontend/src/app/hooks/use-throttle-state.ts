import { useCallback, useRef, useState } from "react";

/**
 * A hook that returns a stateful value and a throttled setter function.
 * The setter will only trigger a state change at most once every `delay` ms.
 */
export function useThrottleState<T>(initialValue: T, delay: number) {
  const [state, setState] = useState<T>(initialValue);

  // Time of last actual update
  const lastRanRef = useRef<number>(0);
  // Pending update if we’re inside the throttle cooldown
  const pendingUpdateRef = useRef<T | null>(null);
  // Timer for a scheduled update
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const throttledSetState = useCallback(
    (newValue: T | ((prev: T) => T)) => {
      const now = Date.now();
      const timeSinceLastUpdate = now - lastRanRef.current;

      // Cancel any pending timer if a new update comes in
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      const resolvedValue =
        typeof newValue === "function" ? (newValue as (prev: T) => T)(state) : newValue;

      if (timeSinceLastUpdate >= delay) {
        // If it’s been >= delay ms since last update, update immediately
        setState(resolvedValue);
        lastRanRef.current = now;
        pendingUpdateRef.current = null;
      } else {
        // Otherwise, schedule an update after the remainder of the delay
        pendingUpdateRef.current = resolvedValue;
        const remainingTime = delay - timeSinceLastUpdate;

        timeoutRef.current = setTimeout(() => {
          if (pendingUpdateRef.current !== null) {
            setState(pendingUpdateRef.current);
            lastRanRef.current = Date.now();
            pendingUpdateRef.current = null;
          }
          timeoutRef.current = null;
        }, remainingTime);
      }
    },
    [delay, state]
  );

  return [state, throttledSetState] as const;
}
