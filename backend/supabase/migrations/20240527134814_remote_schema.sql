CREATE INDEX objects_path_tokens_2__idx ON storage.objects USING btree ((path_tokens[2]));

create policy "tenant_storage_objects_insert"
on "storage"."objects"
as restrictive
for insert
to authenticated
with check ((path_tokens[2] = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_storage_objects_select"
on "storage"."objects"
as restrictive
for select
to authenticated
using ((path_tokens[2] = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));


create policy "tenant_storage_objects_update"
on "storage"."objects"
as restrictive
for update
to authenticated
using ((path_tokens[2] = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))))
with check ((path_tokens[2] = ( SELECT ((auth.jwt() -> 'app_metadata'::text) ->> 'tenant_id'::text))));



