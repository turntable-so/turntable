import Convert from 'ansi-to-html';
import { useCommandPanelContext } from './context';
import { Loader2 } from "lucide-react";
import { useEffect, useRef } from 'react';

export default function CommandLog({ bottomPanelHeight }: { bottomPanelHeight: number }) {
  const { commandPanelState, commandHistory, selectedCommandIndex } = useCommandPanelContext();
  const convert = new Convert();

  const logs = commandHistory[selectedCommandIndex]?.logs || [];
  const showLoader = commandPanelState === 'running' && logs.length === 0;
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return showLoader ? 
  <div className="flex items-center justify-center">
          <Loader2 className="w-6 h-6 animate-spin" />
        </div> :
  (
    <div
      className="flex flex-col overflow-y-auto"
      ref={containerRef}
      style={{ maxHeight: `${bottomPanelHeight}px` }}
    >
      {logs.map((log, index) => (
          <p 
            key={index} 
            dangerouslySetInnerHTML={{ __html: convert.toHtml(log) }} 
            className="whitespace-pre-wrap break-words"
          />
        ))}
    </div>
  );
}
