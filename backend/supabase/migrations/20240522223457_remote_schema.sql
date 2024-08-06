create type "public"."asset_type" as enum ('model', 'source', 'seed', 'analysis', 'metric');

create table "public"."asset_errors" (
    "asset_id" uuid default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "id" uuid not null default gen_random_uuid(),
    "error" jsonb,
    "repository_id" uuid,
    "lineage_type" text
);


alter table "public"."asset_errors" enable row level security;

alter table "public"."assets" drop column "organization_id";

alter table "public"."assets" add column "repository_id" uuid;

alter table "public"."assets" add column "status" text;

alter table "public"."assets" alter column "type" set data type asset_type using "type"::asset_type;

alter table "public"."repositories" add column "status" text;

CREATE UNIQUE INDEX asset_errors_pkey ON public.asset_errors USING btree (id);

CREATE INDEX asset_links_source_id_target_id_idx ON public.asset_links USING btree (source_id, target_id);

CREATE INDEX column_links_source_id_target_id_idx ON public.column_links USING btree (source_id, target_id);

CREATE INDEX columns_asset_id_idx ON public.columns USING hash (asset_id);

alter table "public"."asset_errors" add constraint "asset_errors_pkey" PRIMARY KEY using index "asset_errors_pkey";

alter table "public"."asset_errors" add constraint "asset_errors_asset_id_fkey" FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE not valid;

alter table "public"."asset_errors" validate constraint "asset_errors_asset_id_fkey";

alter table "public"."asset_errors" add constraint "asset_errors_repository_id_fkey" FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE not valid;

alter table "public"."asset_errors" validate constraint "asset_errors_repository_id_fkey";

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


grant delete on table "public"."asset_errors" to "anon";

grant insert on table "public"."asset_errors" to "anon";

grant references on table "public"."asset_errors" to "anon";

grant select on table "public"."asset_errors" to "anon";

grant trigger on table "public"."asset_errors" to "anon";

grant truncate on table "public"."asset_errors" to "anon";

grant update on table "public"."asset_errors" to "anon";

grant delete on table "public"."asset_errors" to "authenticated";

grant insert on table "public"."asset_errors" to "authenticated";

grant references on table "public"."asset_errors" to "authenticated";

grant select on table "public"."asset_errors" to "authenticated";

grant trigger on table "public"."asset_errors" to "authenticated";

grant truncate on table "public"."asset_errors" to "authenticated";

grant update on table "public"."asset_errors" to "authenticated";

grant delete on table "public"."asset_errors" to "service_role";

grant insert on table "public"."asset_errors" to "service_role";

grant references on table "public"."asset_errors" to "service_role";

grant select on table "public"."asset_errors" to "service_role";

grant trigger on table "public"."asset_errors" to "service_role";

grant truncate on table "public"."asset_errors" to "service_role";

grant update on table "public"."asset_errors" to "service_role";


