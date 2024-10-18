import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useLocalStorage } from 'usehooks-ts';
import { Command, CommandPanelState, CommandStatus } from "./types";

interface CommandPanelContextType {
  commandPanelState: CommandPanelState;
  setCommandPanelState: React.Dispatch<React.SetStateAction<CommandPanelState>>;
  selectedCommandIndex: number;
  setSelectedCommandIndex: React.Dispatch<React.SetStateAction<number>>;
  commandHistory: Command[];
  addCommandToHistory: (newCommand: Command) => void;
  updateCommandLogById: (id: string, newLog: string) => void;
  updateCommandById: (id: string, {
    status,
    duration,
  }: {
    status?: CommandStatus;
    duration?: string;
  }) => void;
}

const defaultContextValue: CommandPanelContextType = {
    commandPanelState: 'idling',
    setCommandPanelState: () => {},
    selectedCommandIndex: 0,
    setSelectedCommandIndex: () => {},
    commandHistory: [],
    addCommandToHistory: () => {},
    updateCommandLogById: () => {},
    updateCommandById: () => {},
  };
  
  const CommandPanelContext = createContext<CommandPanelContextType>(defaultContextValue);
  

export const useCommandPanelContext = (): CommandPanelContextType => {
  const context = useContext(CommandPanelContext);
  if (!context) {
    throw new Error('useCommandPanelContext must be used within a MyProvider');
  }
  return context;
};

interface CommandPanelProviderProps {
  children: ReactNode;
}

export const CommandPanelProvider: React.FC<CommandPanelProviderProps> = ({ children }) => {
  const [commandPanelState, setCommandPanelState] = useState<CommandPanelState>("idling");
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
      newHistory[index] = { 
        ...newHistory[index], 
        logs: [...(newHistory[index].logs || []), newLog]
      };
      return newHistory;
    });
  }

  const updateCommandById = (id: string, {
    status,
    duration,
  }: {
    status?: CommandStatus;
    duration?: string;
  }) => {
    setCommandHistory((prevHistory) => {
      const index = prevHistory.findIndex(command => command.id === id);
      if (index === -1) return prevHistory;
      const newHistory = [...prevHistory];
      newHistory[index] = { 
        ...newHistory[index], 
        status: status || newHistory[index].status, 
        duration: duration || newHistory[index].duration 
      };
      return newHistory;
    });
  }

  return (
    <CommandPanelContext.Provider value={{ 
        commandPanelState,
        setCommandPanelState,
        selectedCommandIndex,
        setSelectedCommandIndex,
        commandHistory,
        addCommandToHistory,
        updateCommandLogById,
        updateCommandById,
     }}>
      {children}
    </CommandPanelContext.Provider>
  );
};
