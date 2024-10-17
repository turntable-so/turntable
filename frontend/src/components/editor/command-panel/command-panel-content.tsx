import { useState } from "react";
import CommandPanelInput from "./command-panel-input";
import CommandList from "./command-list";
import CommandLog from "./command-log";
import { useLocalStorage } from 'usehooks-ts';
import { Command } from "./types";

export default function CommandPanelContent() {
  const [selectedCommandIndex, setSelectedCommandIndex] = useState<number>(0);
  const [commandHistory, setCommandHistory] = useLocalStorage<Command[]>('command-history', [
    {
      id: "1729184640",
      command: 'dbt run',
      status: 'failed',
      time: '2:27pm',
      log: '\x1b[30mblack\x1b[37mred'
    },
    {
      id: "1729184639",
      command: 'dbt run',
      status: 'success',
      time: '2:26pm',
      duration: '2s',
      log: '\x1b[30mblack\x1b[37mwhite'
    },
    {
      id: "1729184638",
      command: 'dbt run',
      status: 'running',
      time: '2:25pm'
    },
  ]);

  return (
    <div className="flex flex-col h-full p-4 gap-6">
      <div className="flex flex-col gap-2">
          <p className="text-muted-foreground font-semibold">Run a dbt command</p>
          <CommandPanelInput />
      </div>
      <div className="flex flex-col gap-2">
      <p className="text-muted-foreground font-semibold">Command History</p>
        {commandHistory.length > 0 ? <div className="grid grid-cols-12 gap-4">
        <div className="col-span-4 border-2 rounded-md">
          <CommandList commandHistory={commandHistory} selectedCommandIndex={selectedCommandIndex} setSelectedCommandIndex={setSelectedCommandIndex} />
        </div>
        <div className="col-span-8 rounded-md border-2 p-2">
          <CommandLog commandHistory={commandHistory} selectedCommandIndex={selectedCommandIndex} />
        </div>
      </div> : <p className="text-muted-foreground">No commands run yet</p>}
      </div>
    </div>
  );
}
