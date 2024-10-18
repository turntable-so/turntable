export const DEFAULT_COMMAND_OPTIONS = ["run", "test", "ls", "compile", "docs generate"];

const MAX_RECENT_COMMANDS = 10;

export function getCommandOptions(): string[] {
  const recentCommands = JSON.parse(localStorage.getItem('recentCommands') || '[]') as string[];
  return Array.from(new Set([...recentCommands, ...DEFAULT_COMMAND_OPTIONS])).slice(0, MAX_RECENT_COMMANDS + DEFAULT_COMMAND_OPTIONS.length);
}

export function addRecentCommand(command: string): void {
  const recentCommands = JSON.parse(localStorage.getItem('recentCommands') || '[]') as string[];
  const updatedCommands = [command, ...recentCommands.filter((cmd: string) => cmd !== command)].slice(0, MAX_RECENT_COMMANDS);
  localStorage.setItem('recentCommands', JSON.stringify(updatedCommands));
}