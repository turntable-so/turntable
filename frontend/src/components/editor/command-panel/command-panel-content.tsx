import { useState } from "react";
import CommandPanelInput from "./command-panel-input";
import CommandList from "./command-list";
import CommandLog from "./command-log";
import { useLocalStorage } from 'usehooks-ts';
import { Command } from "./types";

export default function CommandPanelContent() {
  const [selectedCommandIndex, setSelectedCommandIndex] = useState<number>(0);
  const [commandHistory, setCommandHistory] = useLocalStorage<Command[]>('command-history', []);

  const addCommandToHistory = (newCommand: Command) => {
    setCommandHistory([newCommand, ...commandHistory]);
  }

  const updateCommandLogById = (id: string, newLog: string) => {
    setCommandHistory(prevHistory => {
      const index = prevHistory.findIndex(command => command.id === id);
      if (index === -1) return prevHistory;
      const newHistory = [...prevHistory];
      const existingLog = newHistory[index].log || '';
      newHistory[index] = { 
        ...newHistory[index], 
        log: existingLog ? `${existingLog}\n${newLog}` : newLog 
      };
      return newHistory;
    });
  }

  return (
    <div className="flex flex-col h-full p-4 gap-6">
      <div className="flex flex-col gap-2">
          <p className="text-muted-foreground font-semibold">Run a dbt command</p>
          <CommandPanelInput addCommandToHistory={addCommandToHistory} updateCommandLogById={updateCommandLogById} setSelectedCommandIndex={setSelectedCommandIndex} />
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
