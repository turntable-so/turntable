export type Item = {
  value: string;
  display: string;
};

export type SectionType = "file" | "command";

export type Section = {
  title: string;
  topLevelItems: Item[];
  allItems: Item[];
  type: SectionType;
};
