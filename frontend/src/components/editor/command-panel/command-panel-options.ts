export const DEFAULT_COMMAND_OPTIONS = [
  "compile",
  "run",
  "test",
  "build",
  "snapshot",
];

const MAX_RECENT_COMMANDS = 10;

export function getCommandOptions(): string[] {
  let recentCommands = JSON.parse(
    localStorage.getItem("recentCommands") || "[]",
  ) as string[];

  if (recentCommands.length === 0) {
    // If there are no recent commands, initialize with default commands
    recentCommands = [...DEFAULT_COMMAND_OPTIONS];
    localStorage.setItem("recentCommands", JSON.stringify(recentCommands));
  }

  return recentCommands;
}

export function addRecentCommand(command: string): void {
  let recentCommands = JSON.parse(
    localStorage.getItem("recentCommands") || "[]",
  ) as string[];

  // Remove the command if it already exists to prevent duplicates
  recentCommands = recentCommands.filter((cmd) => cmd !== command);

  // Add the new command to the start of the array
  recentCommands.unshift(command);

  // Keep only the most recent MAX_RECENT_COMMANDS commands
  recentCommands = recentCommands.slice(0, MAX_RECENT_COMMANDS);

  // Update localStorage
  localStorage.setItem("recentCommands", JSON.stringify(recentCommands));
}
