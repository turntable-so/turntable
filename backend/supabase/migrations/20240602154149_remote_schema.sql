drop materialized view if exists "public"."asset_lineage";

alter type "public"."asset_type" rename to "asset_type__old_version_to_be_dropped";

create type "public"."asset_type" as enum ('model', 'source', 'seed', 'analysis', 'metric', 'snapshot');

alter table "public"."assets" alter column type type "public"."asset_type" using type::text::"public"."asset_type";

drop type "public"."asset_type__old_version_to_be_dropped";

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



