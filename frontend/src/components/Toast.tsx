import { useEffect } from "react";

// Confirms what just happened (book Chapter 6: visibility of system status).
export function Toast({ message, onDone }: { message: string; onDone: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onDone, 3500);
    return () => clearTimeout(timer);
  }, [message, onDone]);
  return (
    <div className="toast" role="status" aria-live="polite">
      ✓ {message}
    </div>
  );
}
