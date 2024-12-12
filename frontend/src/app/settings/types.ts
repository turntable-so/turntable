export type AssetExclusionFilter = {
  filter_name_contains: string;
  count: number;
};

export type Settings = {
  exclusion_filters: AssetExclusionFilter[];
  api_keys: Record<string, string>;
  ai_custom_instructions?: string;
  env?: Record<string, string>;
};
