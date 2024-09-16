import { z } from "zod"

// We're keeping a simple non-relational schema here.
// IRL, you will have a schema for your data models.
export const assetSchema = z.object({
    id: z.string(),
    name: z.string(),
    type: z.string(),
    unique_name: z.string(),
    description: z.string(),
    tags: z.array(z.string()),
    num_columns: z.number(),
    resource_subtype: z.string(),
    resource_has_dbt: z.boolean(),
    resource_id: z.string(),
    resource_name: z.string(),
})

export type Asset = z.infer<typeof assetSchema>
