export type Item<T> = {
  value: T;
  display: string;
};

type SectionType = "file" | "command";

type Section<T> = {
  title: string;
  topLevelItems: Item<T>[];
  allItems: Item<T>[];
  type: SectionType;
};

export type FileValue = {
  name: string;
  path: string;
};
export type CommandValue = string;
export type FileSection = Section<FileValue>;
export type CommandSection = Section<CommandValue>;

export type FilteredSection =
  | {
      title: string;
      items: Item<FileValue>[];
      type: "file";
    }
  | {
      title: string;
      items: Item<CommandValue>[];
      type: "command";
    };

export type FlatItem = {
  sectionTitle: string;
  item: Item<any>;
  type: SectionType;
};
