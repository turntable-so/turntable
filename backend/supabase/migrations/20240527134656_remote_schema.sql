alter table "public"."asset_errors" add column "tenant_id" text;

alter table "public"."asset_links" add column "tenant_id" text;

alter table "public"."assets" alter column "tenant_id" drop default;

alter table "public"."block_links" add column "tenant_id" text;

alter table "public"."blocks" add column "tenant_id" text;

alter table "public"."column_links" add column "tenant_id" text;

alter table "public"."columns" add column "tenant_id" text;

alter table "public"."models" add column "tenant_id" text;

alter table "public"."notebook_blocks" add column "tenant_id" text;

alter table "public"."notebooks" drop column "organization_id";

alter table "public"."notebooks" add column "tenant_id" text;

alter table "public"."repositories" add column "tenant_id" text;

CREATE INDEX asset_errors_tenant_id_idx ON public.asset_errors USING btree (tenant_id);

CREATE INDEX asset_links_tenant_id_idx ON public.asset_links USING btree (tenant_id);

CREATE INDEX assets_tenant_id_idx ON public.assets USING btree (tenant_id);

CREATE INDEX block_links_tenant_id_idx ON public.block_links USING btree (tenant_id);

CREATE INDEX blocks_tenant_id_idx ON public.blocks USING btree (tenant_id);

CREATE INDEX column_links_tenant_id_idx ON public.column_links USING btree (tenant_id);

CREATE INDEX columns_tenant_id_idx ON public.columns USING btree (tenant_id);

CREATE INDEX github_installations_tenant_id_idx ON public.github_installations USING btree (tenant_id);

CREATE INDEX models_tenant_id_idx ON public.models USING btree (tenant_id);

CREATE INDEX notebook_blocks_tenant_id_idx ON public.notebook_blocks USING btree (tenant_id);

CREATE INDEX notebooks_tenant_id_idx ON public.notebooks USING btree (tenant_id);

CREATE INDEX profiles_tenant_id_idx ON public.profiles USING btree (tenant_id);

CREATE INDEX repositories_tenant_id_idx ON public.repositories USING btree (tenant_id);

CREATE INDEX resources_tenant_id_idx ON public.resources USING btree (tenant_id);

alter table "public"."assets" add constraint "assets_repository_id_fkey" FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE not valid;

alter table "public"."assets" validate constraint "assets_repository_id_fkey";

create policy "tenant_public_asset_links_insert"
on "public"."asset_links"
as restrictive
for insert
to authenticated
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_asset_links_select"
on "public"."asset_links"
as restrictive
for select
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_asset_links_update"
on "public"."asset_links"
as restrictive
for update
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_assets_insert"
on "public"."assets"
as restrictive
for insert
to authenticated
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_assets_select"
on "public"."assets"
as restrictive
for select
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_assets_update"
on "public"."assets"
as restrictive
for update
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_block_links_insert"
on "public"."block_links"
as restrictive
for insert
to authenticated
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_block_links_select"
on "public"."block_links"
as restrictive
for select
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_block_links_update"
on "public"."block_links"
as restrictive
for update
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_blocks_insert"
on "public"."blocks"
as restrictive
for insert
to authenticated
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_blocks_select"
on "public"."blocks"
as restrictive
for select
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_blocks_update"
on "public"."blocks"
as restrictive
for update
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_column_links_insert"
on "public"."column_links"
as restrictive
for insert
to authenticated
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_column_links_select"
on "public"."column_links"
as restrictive
for select
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_column_links_update"
on "public"."column_links"
as restrictive
for update
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_columns_insert"
on "public"."columns"
as restrictive
for insert
to authenticated
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_columns_select"
on "public"."columns"
as restrictive
for select
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_columns_update"
on "public"."columns"
as restrictive
for update
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_github_installations_insert"
on "public"."github_installations"
as restrictive
for insert
to authenticated
with check (((tenant_id)::text = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_github_installations_select"
on "public"."github_installations"
as restrictive
for select
to authenticated
using (((tenant_id)::text = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_github_installations_update"
on "public"."github_installations"
as restrictive
for update
to authenticated
using (((tenant_id)::text = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check (((tenant_id)::text = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_models_insert"
on "public"."models"
as restrictive
for insert
to authenticated
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_models_select"
on "public"."models"
as restrictive
for select
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_models_update"
on "public"."models"
as restrictive
for update
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_notebook_blocks_insert"
on "public"."notebook_blocks"
as restrictive
for insert
to authenticated
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_notebook_blocks_select"
on "public"."notebook_blocks"
as restrictive
for select
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_notebook_blocks_update"
on "public"."notebook_blocks"
as restrictive
for update
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_notebooks_insert"
on "public"."notebooks"
as restrictive
for insert
to authenticated
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_notebooks_select"
on "public"."notebooks"
as restrictive
for select
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_notebooks_update"
on "public"."notebooks"
as restrictive
for update
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_profiles_insert"
on "public"."profiles"
as restrictive
for insert
to authenticated
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_profiles_select"
on "public"."profiles"
as restrictive
for select
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_profiles_update"
on "public"."profiles"
as restrictive
for update
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_repositories_insert"
on "public"."repositories"
as restrictive
for insert
to authenticated
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_repositories_select"
on "public"."repositories"
as restrictive
for select
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_repositories_update"
on "public"."repositories"
as restrictive
for update
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_resources_insert"
on "public"."resources"
as restrictive
for insert
to authenticated
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_resources_select"
on "public"."resources"
as restrictive
for select
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_public_resources_update"
on "public"."resources"
as restrictive
for update
to authenticated
using ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check ((tenant_id = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));



