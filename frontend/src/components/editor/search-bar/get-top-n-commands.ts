import type { Command } from "@/components/editor/command-panel/command-panel-types";
import type { Item } from "@/components/editor/search-bar/types";

type GetTopNCommandsParams = {
  commandHistory: Command[];
  N: number;
};

export const getTopNCommands = ({
  commandHistory,
  N,
}: GetTopNCommandsParams): Item[] => {
  const commandFrequency = commandHistory.reduce<Record<string, number>>(
    (accumulator, { command }) => {
      accumulator[command] = (accumulator[command] || 0) + 1;
      return accumulator;
    },
    {},
  );

  return Object.entries(commandFrequency)
    .sort((a, b) => b[1] - a[1])
    .slice(0, N)
    .map(([command]) => ({
      value: command,
      display: command,
    }));
};
