
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

CREATE SCHEMA IF NOT EXISTS "dev";

ALTER SCHEMA "dev" OWNER TO "postgres";

COMMENT ON SCHEMA "dev" IS 'standard public schema';

CREATE EXTENSION IF NOT EXISTS "pgsodium" WITH SCHEMA "pgsodium";

COMMENT ON SCHEMA "public" IS 'standard public schema';

CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";

CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgjwt" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";

SET default_tablespace = '';

SET default_table_access_method = "heap";

CREATE TABLE IF NOT EXISTS "dev"."asset_bfs_helper" (
    "node_id" "uuid" NOT NULL,
    "depth" integer,
    "path" "uuid"[]
);

ALTER TABLE "dev"."asset_bfs_helper" OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "dev"."assets_bfs"("nodes" "uuid"[], "max_depth" integer) RETURNS SETOF "dev"."asset_bfs_helper"
    LANGUAGE "sql"
    AS $$
  WITH RECURSIVE traversed AS (
    SELECT
      target_id AS node_id,
      1 AS depth,
      ARRAY[source_id] AS path
    FROM asset_links as a
    WHERE a.source_id = any(assets_bfs.nodes) -- Insert starting node here

    UNION ALL

    SELECT
      a.target_id,
      t.depth + 1,
      t.path || a.source_id
    FROM traversed as t
    JOIN asset_links as a ON a.source_id = t.node_id
    where t.depth <= max_depth or max_depth is null
  )
  SELECT node_id, depth, path || node_id AS path
  FROM traversed;
$$;

ALTER FUNCTION "dev"."assets_bfs"("nodes" "uuid"[], "max_depth" integer) OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "dev"."assets_bfs_inverse"("nodes" "uuid"[], "max_depth" integer) RETURNS SETOF "dev"."asset_bfs_helper"
    LANGUAGE "sql"
    AS $$
  WITH RECURSIVE traversed AS (
    SELECT
      source_id AS node_id,
      1 AS depth,
      ARRAY[target_id] AS path
    FROM asset_links as a
    WHERE a.target_id = any(assets_bfs_inverse.nodes) -- Insert starting node here

    UNION ALL

    SELECT
      a.source_id,
      t.depth + 1,
      t.path || a.target_id
    FROM traversed as t
    JOIN asset_links as a ON a.target_id = t.node_id
    where t.depth <= max_depth or max_depth is null
  )
  SELECT node_id, depth, path || node_id AS path
  FROM traversed;
$$;

ALTER FUNCTION "dev"."assets_bfs_inverse"("nodes" "uuid"[], "max_depth" integer) OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."asset_bfs_helper" (
    "node_id" "uuid" NOT NULL,
    "depth" integer,
    "path" "uuid"[]
);

ALTER TABLE "public"."asset_bfs_helper" OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."assets_bfs"("nodes" "uuid"[], "max_depth" integer) RETURNS SETOF "public"."asset_bfs_helper"
    LANGUAGE "sql"
    AS $$
  WITH RECURSIVE traversed AS (
    SELECT
      target_id AS node_id,
      1 AS depth,
      ARRAY[source_id] AS path
    FROM asset_links as a
    WHERE a.source_id = any(assets_bfs.nodes) -- Insert starting node here

    UNION ALL

    SELECT
      a.target_id,
      t.depth + 1,
      t.path || a.source_id
    FROM traversed as t
    JOIN asset_links as a ON a.source_id = t.node_id
    where t.depth <= max_depth or max_depth is null
  )
  SELECT node_id, depth, path || node_id AS path
  FROM traversed;
$$;

ALTER FUNCTION "public"."assets_bfs"("nodes" "uuid"[], "max_depth" integer) OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."assets_bfs_inverse"("nodes" "uuid"[], "max_depth" integer) RETURNS SETOF "public"."asset_bfs_helper"
    LANGUAGE "sql"
    AS $$
  WITH RECURSIVE traversed AS (
    SELECT
      source_id AS node_id,
      1 AS depth,
      ARRAY[target_id] AS path
    FROM asset_links as a
    WHERE a.target_id = any(assets_bfs_inverse.nodes) -- Insert starting node here

    UNION ALL

    SELECT
      a.source_id,
      t.depth + 1,
      t.path || a.target_id
    FROM traversed as t
    JOIN asset_links as a ON a.target_id = t.node_id
    where t.depth <= max_depth or max_depth is null
  )
  SELECT node_id, depth, path || node_id AS path
  FROM traversed;
$$;

ALTER FUNCTION "public"."assets_bfs_inverse"("nodes" "uuid"[], "max_depth" integer) OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."save_creds"() RETURNS "text"
    LANGUAGE "sql"
    AS $$
  select 'hello world';
$$;

ALTER FUNCTION "public"."save_creds"() OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "dev"."asset_links" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "type" character varying,
    "source_id" "uuid",
    "target_id" "uuid"
);

ALTER TABLE "dev"."asset_links" OWNER TO "postgres";

COMMENT ON COLUMN "dev"."asset_links"."type" IS 'logic or db';

CREATE TABLE IF NOT EXISTS "dev"."assets" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "type" character varying,
    "read_only" boolean,
    "resource_id" "uuid",
    "organization_id" "uuid",
    "created_at" timestamp without time zone DEFAULT "now"(),
    "created_by" "uuid",
    "updated_at" timestamp without time zone DEFAULT "now"(),
    "updated_by" "uuid",
    "viewers" character varying[],
    "name" character varying,
    "description" character varying,
    "config" "jsonb",
    "unique_name" "text"
);

ALTER TABLE "dev"."assets" OWNER TO "postgres";

COMMENT ON COLUMN "dev"."assets"."type" IS 'source, model or metric';

COMMENT ON COLUMN "dev"."assets"."resource_id" IS 'only will have value if type is source';

CREATE TABLE IF NOT EXISTS "dev"."block_links" (
    "id" "uuid" NOT NULL,
    "source_id" "uuid",
    "target_id" "uuid"
);

ALTER TABLE "dev"."block_links" OWNER TO "postgres";

COMMENT ON COLUMN "dev"."block_links"."source_id" IS 'can be an asset as well';

CREATE TABLE IF NOT EXISTS "dev"."blocks" (
    "id" "uuid" NOT NULL,
    "created_at" timestamp without time zone,
    "created_by" "uuid",
    "updated_at" timestamp without time zone,
    "updated_by" "uuid",
    "config" "jsonb"
);

ALTER TABLE "dev"."blocks" OWNER TO "postgres";

COMMENT ON COLUMN "dev"."blocks"."id" IS 'needs to be globally unique with asset id';

CREATE TABLE IF NOT EXISTS "dev"."blocks_deprecated" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "type" character varying NOT NULL,
    "title" character varying,
    "sql" "text",
    "database" character varying,
    "notebook_id" "uuid"
);

ALTER TABLE "dev"."blocks_deprecated" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "dev"."column_links" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "lineage_type" character varying,
    "connection_types" character varying[],
    "source_id" "uuid",
    "target_id" "uuid"
);

ALTER TABLE "dev"."column_links" OWNER TO "postgres";

COMMENT ON COLUMN "dev"."column_links"."lineage_type" IS 'all or direct_only';

CREATE TABLE IF NOT EXISTS "dev"."columns" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "asset_id" "uuid",
    "name" character varying,
    "type" character varying,
    "description" character varying,
    "pk" boolean,
    "unique" boolean,
    "fk" "uuid",
    "pii" boolean,
    "errors" "jsonb"[],
    "table_unique_name" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);

ALTER TABLE "dev"."columns" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "dev"."github_installations" (
    "installation_id" character varying NOT NULL,
    "tenant_id" character varying NOT NULL,
    "user_id" character varying NOT NULL
);

ALTER TABLE "dev"."github_installations" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "dev"."models" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" character varying NOT NULL,
    "schema" "json" NOT NULL,
    "sql" "text"
);

ALTER TABLE "dev"."models" OWNER TO "postgres";

ALTER TABLE "dev"."models" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "dev"."models_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "dev"."notebook_blocks" (
    "notebook_id" "uuid",
    "block_id" "uuid",
    "order" integer
);

ALTER TABLE "dev"."notebook_blocks" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "dev"."notebooks" (
    "id" "uuid" NOT NULL,
    "organization_id" "uuid",
    "created_at" "uuid",
    "created_by" "uuid",
    "updated_at" "uuid",
    "updated_by" "uuid",
    "title" character varying,
    "description" character varying,
    "tags" character varying[]
);

ALTER TABLE "dev"."notebooks" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "dev"."notebooks_deprecated" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "title" character varying,
    "description" "text",
    "creator_id" character varying,
    "block_order" character varying[],
    "organization_id" character varying
);

ALTER TABLE "dev"."notebooks_deprecated" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "dev"."repositories" (
    "id" "uuid" NOT NULL,
    "created_at" timestamp without time zone,
    "updated_at" timestamp without time zone,
    "github_repo_id" character varying,
    "repo_owner" character varying,
    "repo_name" character varying,
    "default_branch" character varying,
    "github_installation" character varying,
    "repo_path_zip" character varying
);

ALTER TABLE "dev"."repositories" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "dev"."repository" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "github_repo_id" character varying NOT NULL,
    "repo_owner" character varying,
    "repo_name" character varying,
    "default_branch" character varying,
    "github_installation" character varying NOT NULL,
    "catalog" "jsonb",
    "manifest" "jsonb",
    "target_path" character varying,
    "models_path" character varying,
    "repo_path_zip" character varying,
    "source_id" "uuid" NOT NULL
);

ALTER TABLE "dev"."repository" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "dev"."resources" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "type" character varying,
    "credential_id" "uuid",
    "organization_id" "uuid",
    "repository_id" "uuid",
    "created_at" timestamp without time zone,
    "created_by" "uuid",
    "updated_at" timestamp without time zone,
    "updated_by" "uuid",
    "tables" character varying[],
    "config" "jsonb",
    "name" "text"
);

ALTER TABLE "dev"."resources" OWNER TO "postgres";

COMMENT ON COLUMN "dev"."resources"."type" IS 'File, DatabaseFile, Bigquery, Postgres, or DBT';

COMMENT ON COLUMN "dev"."resources"."repository_id" IS 'Only used for dbt repos for now';

CREATE TABLE IF NOT EXISTS "dev"."sources" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "tenant_id" character varying NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "type" character varying NOT NULL,
    "name" character varying NOT NULL,
    "metadata" "json",
    "authentication" "json"
);

ALTER TABLE "dev"."sources" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."asset_links" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "type" character varying,
    "source_id" "uuid",
    "target_id" "uuid"
);

ALTER TABLE "public"."asset_links" OWNER TO "postgres";

COMMENT ON COLUMN "public"."asset_links"."type" IS 'logic or db';

CREATE TABLE IF NOT EXISTS "public"."assets" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "type" character varying,
    "read_only" boolean,
    "organization_id" "uuid",
    "created_at" timestamp without time zone DEFAULT "now"(),
    "created_by" "uuid",
    "updated_at" timestamp without time zone DEFAULT "now"(),
    "updated_by" "uuid",
    "viewers" character varying[],
    "name" character varying,
    "description" character varying,
    "config" "jsonb",
    "unique_name" "text",
    "resource_ids" "uuid"[],
    "tags" "text"[],
    "tenant_id" "text" DEFAULT 'org_2XVt0EheumDcoCerhQzcUlVmXvG'::"text"
);

ALTER TABLE "public"."assets" OWNER TO "postgres";

COMMENT ON COLUMN "public"."assets"."type" IS 'source, model or metric';

CREATE TABLE IF NOT EXISTS "public"."block_links" (
    "id" "uuid" NOT NULL,
    "source_id" "uuid",
    "target_id" "uuid"
);

ALTER TABLE "public"."block_links" OWNER TO "postgres";

COMMENT ON COLUMN "public"."block_links"."source_id" IS 'can be an asset as well';

CREATE TABLE IF NOT EXISTS "public"."blocks" (
    "id" "uuid" NOT NULL,
    "created_at" timestamp without time zone,
    "created_by" "uuid",
    "updated_at" timestamp without time zone,
    "updated_by" "uuid",
    "config" "jsonb"
);

ALTER TABLE "public"."blocks" OWNER TO "postgres";

COMMENT ON COLUMN "public"."blocks"."id" IS 'needs to be globally unique with asset id';

CREATE TABLE IF NOT EXISTS "public"."column_links" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "lineage_type" character varying,
    "connection_types" character varying[],
    "source_id" "uuid",
    "target_id" "uuid"
);

ALTER TABLE "public"."column_links" OWNER TO "postgres";

COMMENT ON COLUMN "public"."column_links"."lineage_type" IS 'all or direct_only';

CREATE TABLE IF NOT EXISTS "public"."columns" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "asset_id" "uuid",
    "name" character varying,
    "type" character varying,
    "description" character varying,
    "pk" boolean,
    "unique" boolean,
    "fk" "uuid",
    "pii" boolean,
    "errors" "jsonb"[],
    "table_unique_name" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);

ALTER TABLE "public"."columns" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."github_installations" (
    "installation_id" character varying NOT NULL,
    "tenant_id" character varying NOT NULL,
    "user_id" character varying NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"()
);

ALTER TABLE "public"."github_installations" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."models" (
    "id" bigint NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" character varying NOT NULL,
    "schema" "json" NOT NULL,
    "sql" "text"
);

ALTER TABLE "public"."models" OWNER TO "postgres";

ALTER TABLE "public"."models" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."models_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."notebook_blocks" (
    "notebook_id" "uuid",
    "block_id" "uuid",
    "order" integer
);

ALTER TABLE "public"."notebook_blocks" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."notebooks" (
    "id" "uuid" NOT NULL,
    "organization_id" "uuid",
    "created_at" "uuid",
    "created_by" "uuid",
    "updated_at" "uuid",
    "updated_by" "uuid",
    "title" character varying,
    "description" character varying,
    "tags" character varying[]
);

ALTER TABLE "public"."notebooks" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."profiles" (
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "name" character varying,
    "encrypted_secret" "text" NOT NULL,
    "description" "text",
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "tenant_id" "text" NOT NULL
);

ALTER TABLE "public"."profiles" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."repositories" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "created_at" timestamp without time zone DEFAULT ("now"() AT TIME ZONE 'utc'::"text"),
    "updated_at" timestamp without time zone,
    "github_repo_id" character varying,
    "repo_owner" character varying,
    "repo_name" character varying,
    "default_branch" character varying,
    "github_installation" character varying,
    "repo_path_zip" character varying,
    "resource_id" "uuid",
    "tables" "text"[]
);

ALTER TABLE "public"."repositories" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."resources" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "type" character varying,
    "tenant_id" "text",
    "created_at" timestamp without time zone DEFAULT ("now"() AT TIME ZONE 'utc'::"text"),
    "created_by" "uuid",
    "updated_at" timestamp without time zone,
    "updated_by" "uuid",
    "tables" character varying[],
    "config" "jsonb",
    "name" "text",
    "github_repo_id" "text",
    "auth_profile_id" "uuid"
);

ALTER TABLE "public"."resources" OWNER TO "postgres";

COMMENT ON COLUMN "public"."resources"."type" IS 'File, DatabaseFile, Bigquery, Postgres, or DBT';

ALTER TABLE ONLY "dev"."asset_links"
    ADD CONSTRAINT "asset_links_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."assets"
    ADD CONSTRAINT "assets_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."block_links"
    ADD CONSTRAINT "block_links_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."blocks_deprecated"
    ADD CONSTRAINT "blocks_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."blocks"
    ADD CONSTRAINT "blocks_pkey1" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."column_links"
    ADD CONSTRAINT "column_links_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."columns"
    ADD CONSTRAINT "columns_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."github_installations"
    ADD CONSTRAINT "github_installations_pkey" PRIMARY KEY ("installation_id");

ALTER TABLE ONLY "dev"."models"
    ADD CONSTRAINT "models_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."notebooks_deprecated"
    ADD CONSTRAINT "notebook_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."notebooks"
    ADD CONSTRAINT "notebooks_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."repositories"
    ADD CONSTRAINT "repositories_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."repository"
    ADD CONSTRAINT "repository_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."resources"
    ADD CONSTRAINT "resources_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."sources"
    ADD CONSTRAINT "sources_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "dev"."asset_bfs_helper"
    ADD CONSTRAINT "test_pkey" PRIMARY KEY ("node_id");

ALTER TABLE ONLY "public"."asset_links"
    ADD CONSTRAINT "asset_links_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."assets"
    ADD CONSTRAINT "assets_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."block_links"
    ADD CONSTRAINT "block_links_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."blocks"
    ADD CONSTRAINT "blocks_pkey1" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."column_links"
    ADD CONSTRAINT "column_links_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."columns"
    ADD CONSTRAINT "columns_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."github_installations"
    ADD CONSTRAINT "github_installations_pkey" PRIMARY KEY ("installation_id");

ALTER TABLE ONLY "public"."models"
    ADD CONSTRAINT "models_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."notebooks"
    ADD CONSTRAINT "notebooks_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_id_key" UNIQUE ("id");

ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."repositories"
    ADD CONSTRAINT "repositories_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."resources"
    ADD CONSTRAINT "resources_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."asset_bfs_helper"
    ADD CONSTRAINT "test_pkey" PRIMARY KEY ("node_id");

ALTER TABLE ONLY "dev"."asset_links"
    ADD CONSTRAINT "asset_links_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "dev"."assets"("id");

ALTER TABLE ONLY "dev"."asset_links"
    ADD CONSTRAINT "asset_links_target_id_fkey" FOREIGN KEY ("target_id") REFERENCES "dev"."assets"("id");

ALTER TABLE ONLY "dev"."assets"
    ADD CONSTRAINT "assets_resource_id_fkey" FOREIGN KEY ("resource_id") REFERENCES "dev"."resources"("id");

ALTER TABLE ONLY "dev"."block_links"
    ADD CONSTRAINT "block_links_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "dev"."blocks"("id");

ALTER TABLE ONLY "dev"."block_links"
    ADD CONSTRAINT "block_links_source_id_fkey1" FOREIGN KEY ("source_id") REFERENCES "dev"."assets"("id");

ALTER TABLE ONLY "dev"."block_links"
    ADD CONSTRAINT "block_links_target_id_fkey" FOREIGN KEY ("target_id") REFERENCES "dev"."blocks"("id");

ALTER TABLE ONLY "dev"."column_links"
    ADD CONSTRAINT "column_links_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "dev"."columns"("id");

ALTER TABLE ONLY "dev"."column_links"
    ADD CONSTRAINT "column_links_target_id_fkey" FOREIGN KEY ("target_id") REFERENCES "dev"."columns"("id");

ALTER TABLE ONLY "dev"."columns"
    ADD CONSTRAINT "columns_asset_id_fkey" FOREIGN KEY ("asset_id") REFERENCES "dev"."assets"("id");

ALTER TABLE ONLY "dev"."columns"
    ADD CONSTRAINT "columns_fk_fkey" FOREIGN KEY ("fk") REFERENCES "dev"."columns"("id");

ALTER TABLE ONLY "dev"."notebook_blocks"
    ADD CONSTRAINT "notebook_blocks_block_id_fkey" FOREIGN KEY ("block_id") REFERENCES "dev"."blocks"("id");

ALTER TABLE ONLY "dev"."notebook_blocks"
    ADD CONSTRAINT "notebook_blocks_notebook_id_fkey" FOREIGN KEY ("notebook_id") REFERENCES "dev"."notebooks"("id");

ALTER TABLE ONLY "dev"."blocks_deprecated"
    ADD CONSTRAINT "public_blocks_notebook_id_fkey" FOREIGN KEY ("notebook_id") REFERENCES "dev"."notebooks_deprecated"("id");

ALTER TABLE ONLY "dev"."repository"
    ADD CONSTRAINT "public_repository_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "dev"."sources"("id");

ALTER TABLE ONLY "dev"."resources"
    ADD CONSTRAINT "resources_repository_id_fkey" FOREIGN KEY ("repository_id") REFERENCES "dev"."repositories"("id");

ALTER TABLE ONLY "public"."asset_links"
    ADD CONSTRAINT "asset_links_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "public"."assets"("id") ON DELETE CASCADE;

ALTER TABLE ONLY "public"."asset_links"
    ADD CONSTRAINT "asset_links_target_id_fkey" FOREIGN KEY ("target_id") REFERENCES "public"."assets"("id") ON DELETE CASCADE;

ALTER TABLE ONLY "public"."block_links"
    ADD CONSTRAINT "block_links_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "public"."blocks"("id");

ALTER TABLE ONLY "public"."block_links"
    ADD CONSTRAINT "block_links_source_id_fkey1" FOREIGN KEY ("source_id") REFERENCES "public"."assets"("id");

ALTER TABLE ONLY "public"."block_links"
    ADD CONSTRAINT "block_links_target_id_fkey" FOREIGN KEY ("target_id") REFERENCES "public"."blocks"("id");

ALTER TABLE ONLY "public"."column_links"
    ADD CONSTRAINT "column_links_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "public"."columns"("id") ON DELETE CASCADE;

ALTER TABLE ONLY "public"."column_links"
    ADD CONSTRAINT "column_links_target_id_fkey" FOREIGN KEY ("target_id") REFERENCES "public"."columns"("id") ON DELETE CASCADE;

ALTER TABLE ONLY "public"."columns"
    ADD CONSTRAINT "columns_asset_id_fkey" FOREIGN KEY ("asset_id") REFERENCES "public"."assets"("id") ON DELETE CASCADE;

ALTER TABLE ONLY "public"."columns"
    ADD CONSTRAINT "columns_fk_fkey" FOREIGN KEY ("fk") REFERENCES "public"."columns"("id");

ALTER TABLE ONLY "public"."notebook_blocks"
    ADD CONSTRAINT "notebook_blocks_block_id_fkey" FOREIGN KEY ("block_id") REFERENCES "public"."blocks"("id");

ALTER TABLE ONLY "public"."notebook_blocks"
    ADD CONSTRAINT "notebook_blocks_notebook_id_fkey" FOREIGN KEY ("notebook_id") REFERENCES "public"."notebooks"("id");

ALTER TABLE ONLY "public"."repositories"
    ADD CONSTRAINT "repositories_resource_id_fkey" FOREIGN KEY ("resource_id") REFERENCES "public"."resources"("id");

ALTER TABLE ONLY "public"."resources"
    ADD CONSTRAINT "resources_auth_profile_id_fkey" FOREIGN KEY ("auth_profile_id") REFERENCES "public"."profiles"("id");

ALTER TABLE "dev"."asset_links" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."assets" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."block_links" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."blocks" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."blocks_deprecated" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."column_links" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."columns" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."github_installations" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."models" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."notebook_blocks" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."notebooks" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."notebooks_deprecated" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."repositories" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."repository" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."resources" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "dev"."sources" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."asset_links" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."assets" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."block_links" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."blocks" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."column_links" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."columns" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."github_installations" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."models" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."notebook_blocks" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."notebooks" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."profiles" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."repositories" ENABLE ROW LEVEL SECURITY;

ALTER TABLE "public"."resources" ENABLE ROW LEVEL SECURITY;

ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";

GRANT USAGE ON SCHEMA "dev" TO "anon";
GRANT USAGE ON SCHEMA "dev" TO "authenticated";
GRANT USAGE ON SCHEMA "dev" TO "service_role";

GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";

GRANT ALL ON TABLE "dev"."asset_bfs_helper" TO "anon";
GRANT ALL ON TABLE "dev"."asset_bfs_helper" TO "authenticated";
GRANT ALL ON TABLE "dev"."asset_bfs_helper" TO "service_role";

GRANT ALL ON FUNCTION "dev"."assets_bfs"("nodes" "uuid"[], "max_depth" integer) TO "anon";
GRANT ALL ON FUNCTION "dev"."assets_bfs"("nodes" "uuid"[], "max_depth" integer) TO "authenticated";
GRANT ALL ON FUNCTION "dev"."assets_bfs"("nodes" "uuid"[], "max_depth" integer) TO "service_role";

GRANT ALL ON FUNCTION "dev"."assets_bfs_inverse"("nodes" "uuid"[], "max_depth" integer) TO "anon";
GRANT ALL ON FUNCTION "dev"."assets_bfs_inverse"("nodes" "uuid"[], "max_depth" integer) TO "authenticated";
GRANT ALL ON FUNCTION "dev"."assets_bfs_inverse"("nodes" "uuid"[], "max_depth" integer) TO "service_role";

GRANT ALL ON TABLE "public"."asset_bfs_helper" TO "anon";
GRANT ALL ON TABLE "public"."asset_bfs_helper" TO "authenticated";
GRANT ALL ON TABLE "public"."asset_bfs_helper" TO "service_role";

GRANT ALL ON FUNCTION "public"."assets_bfs"("nodes" "uuid"[], "max_depth" integer) TO "anon";
GRANT ALL ON FUNCTION "public"."assets_bfs"("nodes" "uuid"[], "max_depth" integer) TO "authenticated";
GRANT ALL ON FUNCTION "public"."assets_bfs"("nodes" "uuid"[], "max_depth" integer) TO "service_role";

GRANT ALL ON FUNCTION "public"."assets_bfs_inverse"("nodes" "uuid"[], "max_depth" integer) TO "anon";
GRANT ALL ON FUNCTION "public"."assets_bfs_inverse"("nodes" "uuid"[], "max_depth" integer) TO "authenticated";
GRANT ALL ON FUNCTION "public"."assets_bfs_inverse"("nodes" "uuid"[], "max_depth" integer) TO "service_role";

GRANT ALL ON FUNCTION "public"."save_creds"() TO "anon";
GRANT ALL ON FUNCTION "public"."save_creds"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."save_creds"() TO "service_role";

GRANT ALL ON TABLE "dev"."asset_links" TO "anon";
GRANT ALL ON TABLE "dev"."asset_links" TO "authenticated";
GRANT ALL ON TABLE "dev"."asset_links" TO "service_role";

GRANT ALL ON TABLE "dev"."assets" TO "anon";
GRANT ALL ON TABLE "dev"."assets" TO "authenticated";
GRANT ALL ON TABLE "dev"."assets" TO "service_role";

GRANT ALL ON TABLE "dev"."block_links" TO "anon";
GRANT ALL ON TABLE "dev"."block_links" TO "authenticated";
GRANT ALL ON TABLE "dev"."block_links" TO "service_role";

GRANT ALL ON TABLE "dev"."blocks" TO "anon";
GRANT ALL ON TABLE "dev"."blocks" TO "authenticated";
GRANT ALL ON TABLE "dev"."blocks" TO "service_role";

GRANT ALL ON TABLE "dev"."blocks_deprecated" TO "anon";
GRANT ALL ON TABLE "dev"."blocks_deprecated" TO "authenticated";
GRANT ALL ON TABLE "dev"."blocks_deprecated" TO "service_role";

GRANT ALL ON TABLE "dev"."column_links" TO "anon";
GRANT ALL ON TABLE "dev"."column_links" TO "authenticated";
GRANT ALL ON TABLE "dev"."column_links" TO "service_role";

GRANT ALL ON TABLE "dev"."columns" TO "anon";
GRANT ALL ON TABLE "dev"."columns" TO "authenticated";
GRANT ALL ON TABLE "dev"."columns" TO "service_role";

GRANT ALL ON TABLE "dev"."github_installations" TO "anon";
GRANT ALL ON TABLE "dev"."github_installations" TO "authenticated";
GRANT ALL ON TABLE "dev"."github_installations" TO "service_role";

GRANT ALL ON TABLE "dev"."models" TO "anon";
GRANT ALL ON TABLE "dev"."models" TO "authenticated";
GRANT ALL ON TABLE "dev"."models" TO "service_role";

GRANT ALL ON SEQUENCE "dev"."models_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "dev"."models_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "dev"."models_id_seq" TO "service_role";

GRANT ALL ON TABLE "dev"."notebook_blocks" TO "anon";
GRANT ALL ON TABLE "dev"."notebook_blocks" TO "authenticated";
GRANT ALL ON TABLE "dev"."notebook_blocks" TO "service_role";

GRANT ALL ON TABLE "dev"."notebooks" TO "anon";
GRANT ALL ON TABLE "dev"."notebooks" TO "authenticated";
GRANT ALL ON TABLE "dev"."notebooks" TO "service_role";

GRANT ALL ON TABLE "dev"."notebooks_deprecated" TO "anon";
GRANT ALL ON TABLE "dev"."notebooks_deprecated" TO "authenticated";
GRANT ALL ON TABLE "dev"."notebooks_deprecated" TO "service_role";

GRANT ALL ON TABLE "dev"."repositories" TO "anon";
GRANT ALL ON TABLE "dev"."repositories" TO "authenticated";
GRANT ALL ON TABLE "dev"."repositories" TO "service_role";

GRANT ALL ON TABLE "dev"."repository" TO "anon";
GRANT ALL ON TABLE "dev"."repository" TO "authenticated";
GRANT ALL ON TABLE "dev"."repository" TO "service_role";

GRANT ALL ON TABLE "dev"."resources" TO "anon";
GRANT ALL ON TABLE "dev"."resources" TO "authenticated";
GRANT ALL ON TABLE "dev"."resources" TO "service_role";

GRANT ALL ON TABLE "dev"."sources" TO "anon";
GRANT ALL ON TABLE "dev"."sources" TO "authenticated";
GRANT ALL ON TABLE "dev"."sources" TO "service_role";

GRANT ALL ON TABLE "public"."asset_links" TO "anon";
GRANT ALL ON TABLE "public"."asset_links" TO "authenticated";
GRANT ALL ON TABLE "public"."asset_links" TO "service_role";

GRANT ALL ON TABLE "public"."assets" TO "anon";
GRANT ALL ON TABLE "public"."assets" TO "authenticated";
GRANT ALL ON TABLE "public"."assets" TO "service_role";

GRANT ALL ON TABLE "public"."block_links" TO "anon";
GRANT ALL ON TABLE "public"."block_links" TO "authenticated";
GRANT ALL ON TABLE "public"."block_links" TO "service_role";

GRANT ALL ON TABLE "public"."blocks" TO "anon";
GRANT ALL ON TABLE "public"."blocks" TO "authenticated";
GRANT ALL ON TABLE "public"."blocks" TO "service_role";

GRANT ALL ON TABLE "public"."column_links" TO "anon";
GRANT ALL ON TABLE "public"."column_links" TO "authenticated";
GRANT ALL ON TABLE "public"."column_links" TO "service_role";

GRANT ALL ON TABLE "public"."columns" TO "anon";
GRANT ALL ON TABLE "public"."columns" TO "authenticated";
GRANT ALL ON TABLE "public"."columns" TO "service_role";

GRANT ALL ON TABLE "public"."github_installations" TO "anon";
GRANT ALL ON TABLE "public"."github_installations" TO "authenticated";
GRANT ALL ON TABLE "public"."github_installations" TO "service_role";

GRANT ALL ON TABLE "public"."models" TO "anon";
GRANT ALL ON TABLE "public"."models" TO "authenticated";
GRANT ALL ON TABLE "public"."models" TO "service_role";

GRANT ALL ON SEQUENCE "public"."models_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."models_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."models_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."notebook_blocks" TO "anon";
GRANT ALL ON TABLE "public"."notebook_blocks" TO "authenticated";
GRANT ALL ON TABLE "public"."notebook_blocks" TO "service_role";

GRANT ALL ON TABLE "public"."notebooks" TO "anon";
GRANT ALL ON TABLE "public"."notebooks" TO "authenticated";
GRANT ALL ON TABLE "public"."notebooks" TO "service_role";

GRANT ALL ON TABLE "public"."profiles" TO "anon";
GRANT ALL ON TABLE "public"."profiles" TO "authenticated";
GRANT ALL ON TABLE "public"."profiles" TO "service_role";

GRANT ALL ON TABLE "public"."repositories" TO "anon";
GRANT ALL ON TABLE "public"."repositories" TO "authenticated";
GRANT ALL ON TABLE "public"."repositories" TO "service_role";

GRANT ALL ON TABLE "public"."resources" TO "anon";
GRANT ALL ON TABLE "public"."resources" TO "authenticated";
GRANT ALL ON TABLE "public"."resources" TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "dev" GRANT ALL ON SEQUENCES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "dev" GRANT ALL ON SEQUENCES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "dev" GRANT ALL ON SEQUENCES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "dev" GRANT ALL ON SEQUENCES  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "dev" GRANT ALL ON FUNCTIONS  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "dev" GRANT ALL ON FUNCTIONS  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "dev" GRANT ALL ON FUNCTIONS  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "dev" GRANT ALL ON FUNCTIONS  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "dev" GRANT ALL ON TABLES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "dev" GRANT ALL ON TABLES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "dev" GRANT ALL ON TABLES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "dev" GRANT ALL ON TABLES  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "service_role";

RESET ALL;
