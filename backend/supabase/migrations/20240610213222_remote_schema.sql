drop materialized view if exists "public"."asset_lineage";

alter table "public"."assets" drop column "resource_ids";

alter table "public"."assets" add column "resource_id" uuid;

alter table "public"."assets" add constraint "assets_resource_id_fkey" FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE not valid;

alter table "public"."assets" validate constraint "assets_resource_id_fkey";

create materialized view "public"."asset_lineage" as  WITH assets_columns AS (
         SELECT assets.id AS asset_id,
            assets.type AS asset_type,
            columns.id AS column_id,
            columns.name AS column_name,
            columns.type AS column_type,
            assets.created_at,
            assets.description AS model_description,
            columns.description AS column_description,
            assets.unique_name
           FROM (assets
             LEFT JOIN columns ON ((assets.id = columns.asset_id)))
        ), assets_columns_links AS (
         SELECT assets_columns_1.asset_id,
            assets_columns_1.asset_type,
            assets_columns_1.column_id,
            assets_columns_1.column_name,
            assets_columns_1.column_type,
            assets_columns_1.created_at,
            assets_columns_1.model_description,
            assets_columns_1.column_description,
            assets_columns_1.unique_name,
            cl.source_column_id,
            cl.target_column_id
           FROM (assets_columns assets_columns_1
             LEFT JOIN ( SELECT column_links.source_id AS source_column_id,
                    column_links.target_id AS target_column_id
                   FROM column_links) cl ON (((assets_columns_1.column_id = cl.source_column_id) OR (cl.target_column_id = assets_columns_1.column_id))))
        )
 SELECT assets_columns.asset_id,
    assets_columns.asset_type,
    assets_columns.column_id,
    assets_columns.column_name,
    assets_columns.column_type,
    assets_columns.created_at,
    assets_columns.model_description,
    assets_columns.column_description,
    assets_columns.unique_name
   FROM assets_columns;



