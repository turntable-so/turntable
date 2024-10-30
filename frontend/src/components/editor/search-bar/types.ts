export type SectionType = "file" | "command";

export type Section = {
  title: string;
  /*
    * These are the items that show up when the search bar is focused
   */
  topLevelItems: string[];
  /*
    * These are all the searchable items.
   */
  allItems: string[];
  type: SectionType;
};
