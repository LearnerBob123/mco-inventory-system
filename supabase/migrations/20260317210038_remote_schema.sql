drop extension if exists "pg_net";

create sequence "public"."assemblies_assembly_id_seq";

create sequence "public"."audit_logs_log_id_seq";

create sequence "public"."components_component_id_seq";

create sequence "public"."guns_gun_id_seq";

create sequence "public"."inventory_inventory_id_seq";

create sequence "public"."lifecycle_logs_id_seq";

create sequence "public"."transactions_transaction_id_seq";

create sequence "public"."users_id_seq";


  create table "public"."assemblies" (
    "assembly_id" integer not null default nextval('public.assemblies_assembly_id_seq'::regclass),
    "gun_id" integer,
    "component_id" integer
      );



  create table "public"."audit_logs" (
    "log_id" integer not null default nextval('public.audit_logs_log_id_seq'::regclass),
    "action" character varying,
    "user_id" integer
      );



  create table "public"."components" (
    "component_id" integer not null default nextval('public.components_component_id_seq'::regclass),
    "name" character varying,
    "state" character varying,
    "qty_per_gun" integer,
    "annual_supply" integer,
    "max_replacement" integer
      );



  create table "public"."guns" (
    "gun_id" integer not null default nextval('public.guns_gun_id_seq'::regclass),
    "name" character varying,
    "status" character varying
      );



  create table "public"."inventory" (
    "inventory_id" integer not null default nextval('public.inventory_inventory_id_seq'::regclass),
    "component_id" integer,
    "quantity" integer,
    "location" character varying
      );



  create table "public"."lifecycle_logs" (
    "id" integer not null default nextval('public.lifecycle_logs_id_seq'::regclass),
    "component_id" integer,
    "old_state" character varying,
    "new_state" character varying
      );



  create table "public"."transactions" (
    "transaction_id" integer not null default nextval('public.transactions_transaction_id_seq'::regclass),
    "component_id" integer,
    "action" character varying,
    "user_id" integer
      );



  create table "public"."users" (
    "id" integer not null default nextval('public.users_id_seq'::regclass),
    "username" character varying,
    "password" character varying,
    "role" character varying
      );


alter sequence "public"."assemblies_assembly_id_seq" owned by "public"."assemblies"."assembly_id";

alter sequence "public"."audit_logs_log_id_seq" owned by "public"."audit_logs"."log_id";

alter sequence "public"."components_component_id_seq" owned by "public"."components"."component_id";

alter sequence "public"."guns_gun_id_seq" owned by "public"."guns"."gun_id";

alter sequence "public"."inventory_inventory_id_seq" owned by "public"."inventory"."inventory_id";

alter sequence "public"."lifecycle_logs_id_seq" owned by "public"."lifecycle_logs"."id";

alter sequence "public"."transactions_transaction_id_seq" owned by "public"."transactions"."transaction_id";

alter sequence "public"."users_id_seq" owned by "public"."users"."id";

CREATE UNIQUE INDEX assemblies_pkey ON public.assemblies USING btree (assembly_id);

CREATE UNIQUE INDEX audit_logs_pkey ON public.audit_logs USING btree (log_id);

CREATE UNIQUE INDEX components_pkey ON public.components USING btree (component_id);

CREATE UNIQUE INDEX guns_pkey ON public.guns USING btree (gun_id);

CREATE UNIQUE INDEX inventory_pkey ON public.inventory USING btree (inventory_id);

CREATE INDEX ix_assemblies_assembly_id ON public.assemblies USING btree (assembly_id);

CREATE INDEX ix_audit_logs_log_id ON public.audit_logs USING btree (log_id);

CREATE INDEX ix_components_component_id ON public.components USING btree (component_id);

CREATE INDEX ix_guns_gun_id ON public.guns USING btree (gun_id);

CREATE INDEX ix_inventory_inventory_id ON public.inventory USING btree (inventory_id);

CREATE INDEX ix_lifecycle_logs_id ON public.lifecycle_logs USING btree (id);

CREATE INDEX ix_transactions_transaction_id ON public.transactions USING btree (transaction_id);

CREATE INDEX ix_users_id ON public.users USING btree (id);

CREATE UNIQUE INDEX lifecycle_logs_pkey ON public.lifecycle_logs USING btree (id);

CREATE UNIQUE INDEX transactions_pkey ON public.transactions USING btree (transaction_id);

CREATE UNIQUE INDEX users_pkey ON public.users USING btree (id);

alter table "public"."assemblies" add constraint "assemblies_pkey" PRIMARY KEY using index "assemblies_pkey";

alter table "public"."audit_logs" add constraint "audit_logs_pkey" PRIMARY KEY using index "audit_logs_pkey";

alter table "public"."components" add constraint "components_pkey" PRIMARY KEY using index "components_pkey";

alter table "public"."guns" add constraint "guns_pkey" PRIMARY KEY using index "guns_pkey";

alter table "public"."inventory" add constraint "inventory_pkey" PRIMARY KEY using index "inventory_pkey";

alter table "public"."lifecycle_logs" add constraint "lifecycle_logs_pkey" PRIMARY KEY using index "lifecycle_logs_pkey";

alter table "public"."transactions" add constraint "transactions_pkey" PRIMARY KEY using index "transactions_pkey";

alter table "public"."users" add constraint "users_pkey" PRIMARY KEY using index "users_pkey";

grant delete on table "public"."assemblies" to "anon";

grant insert on table "public"."assemblies" to "anon";

grant references on table "public"."assemblies" to "anon";

grant select on table "public"."assemblies" to "anon";

grant trigger on table "public"."assemblies" to "anon";

grant truncate on table "public"."assemblies" to "anon";

grant update on table "public"."assemblies" to "anon";

grant delete on table "public"."assemblies" to "authenticated";

grant insert on table "public"."assemblies" to "authenticated";

grant references on table "public"."assemblies" to "authenticated";

grant select on table "public"."assemblies" to "authenticated";

grant trigger on table "public"."assemblies" to "authenticated";

grant truncate on table "public"."assemblies" to "authenticated";

grant update on table "public"."assemblies" to "authenticated";

grant delete on table "public"."assemblies" to "service_role";

grant insert on table "public"."assemblies" to "service_role";

grant references on table "public"."assemblies" to "service_role";

grant select on table "public"."assemblies" to "service_role";

grant trigger on table "public"."assemblies" to "service_role";

grant truncate on table "public"."assemblies" to "service_role";

grant update on table "public"."assemblies" to "service_role";

grant delete on table "public"."audit_logs" to "anon";

grant insert on table "public"."audit_logs" to "anon";

grant references on table "public"."audit_logs" to "anon";

grant select on table "public"."audit_logs" to "anon";

grant trigger on table "public"."audit_logs" to "anon";

grant truncate on table "public"."audit_logs" to "anon";

grant update on table "public"."audit_logs" to "anon";

grant delete on table "public"."audit_logs" to "authenticated";

grant insert on table "public"."audit_logs" to "authenticated";

grant references on table "public"."audit_logs" to "authenticated";

grant select on table "public"."audit_logs" to "authenticated";

grant trigger on table "public"."audit_logs" to "authenticated";

grant truncate on table "public"."audit_logs" to "authenticated";

grant update on table "public"."audit_logs" to "authenticated";

grant delete on table "public"."audit_logs" to "service_role";

grant insert on table "public"."audit_logs" to "service_role";

grant references on table "public"."audit_logs" to "service_role";

grant select on table "public"."audit_logs" to "service_role";

grant trigger on table "public"."audit_logs" to "service_role";

grant truncate on table "public"."audit_logs" to "service_role";

grant update on table "public"."audit_logs" to "service_role";

grant delete on table "public"."components" to "anon";

grant insert on table "public"."components" to "anon";

grant references on table "public"."components" to "anon";

grant select on table "public"."components" to "anon";

grant trigger on table "public"."components" to "anon";

grant truncate on table "public"."components" to "anon";

grant update on table "public"."components" to "anon";

grant delete on table "public"."components" to "authenticated";

grant insert on table "public"."components" to "authenticated";

grant references on table "public"."components" to "authenticated";

grant select on table "public"."components" to "authenticated";

grant trigger on table "public"."components" to "authenticated";

grant truncate on table "public"."components" to "authenticated";

grant update on table "public"."components" to "authenticated";

grant delete on table "public"."components" to "service_role";

grant insert on table "public"."components" to "service_role";

grant references on table "public"."components" to "service_role";

grant select on table "public"."components" to "service_role";

grant trigger on table "public"."components" to "service_role";

grant truncate on table "public"."components" to "service_role";

grant update on table "public"."components" to "service_role";

grant delete on table "public"."guns" to "anon";

grant insert on table "public"."guns" to "anon";

grant references on table "public"."guns" to "anon";

grant select on table "public"."guns" to "anon";

grant trigger on table "public"."guns" to "anon";

grant truncate on table "public"."guns" to "anon";

grant update on table "public"."guns" to "anon";

grant delete on table "public"."guns" to "authenticated";

grant insert on table "public"."guns" to "authenticated";

grant references on table "public"."guns" to "authenticated";

grant select on table "public"."guns" to "authenticated";

grant trigger on table "public"."guns" to "authenticated";

grant truncate on table "public"."guns" to "authenticated";

grant update on table "public"."guns" to "authenticated";

grant delete on table "public"."guns" to "service_role";

grant insert on table "public"."guns" to "service_role";

grant references on table "public"."guns" to "service_role";

grant select on table "public"."guns" to "service_role";

grant trigger on table "public"."guns" to "service_role";

grant truncate on table "public"."guns" to "service_role";

grant update on table "public"."guns" to "service_role";

grant delete on table "public"."inventory" to "anon";

grant insert on table "public"."inventory" to "anon";

grant references on table "public"."inventory" to "anon";

grant select on table "public"."inventory" to "anon";

grant trigger on table "public"."inventory" to "anon";

grant truncate on table "public"."inventory" to "anon";

grant update on table "public"."inventory" to "anon";

grant delete on table "public"."inventory" to "authenticated";

grant insert on table "public"."inventory" to "authenticated";

grant references on table "public"."inventory" to "authenticated";

grant select on table "public"."inventory" to "authenticated";

grant trigger on table "public"."inventory" to "authenticated";

grant truncate on table "public"."inventory" to "authenticated";

grant update on table "public"."inventory" to "authenticated";

grant delete on table "public"."inventory" to "service_role";

grant insert on table "public"."inventory" to "service_role";

grant references on table "public"."inventory" to "service_role";

grant select on table "public"."inventory" to "service_role";

grant trigger on table "public"."inventory" to "service_role";

grant truncate on table "public"."inventory" to "service_role";

grant update on table "public"."inventory" to "service_role";

grant delete on table "public"."lifecycle_logs" to "anon";

grant insert on table "public"."lifecycle_logs" to "anon";

grant references on table "public"."lifecycle_logs" to "anon";

grant select on table "public"."lifecycle_logs" to "anon";

grant trigger on table "public"."lifecycle_logs" to "anon";

grant truncate on table "public"."lifecycle_logs" to "anon";

grant update on table "public"."lifecycle_logs" to "anon";

grant delete on table "public"."lifecycle_logs" to "authenticated";

grant insert on table "public"."lifecycle_logs" to "authenticated";

grant references on table "public"."lifecycle_logs" to "authenticated";

grant select on table "public"."lifecycle_logs" to "authenticated";

grant trigger on table "public"."lifecycle_logs" to "authenticated";

grant truncate on table "public"."lifecycle_logs" to "authenticated";

grant update on table "public"."lifecycle_logs" to "authenticated";

grant delete on table "public"."lifecycle_logs" to "service_role";

grant insert on table "public"."lifecycle_logs" to "service_role";

grant references on table "public"."lifecycle_logs" to "service_role";

grant select on table "public"."lifecycle_logs" to "service_role";

grant trigger on table "public"."lifecycle_logs" to "service_role";

grant truncate on table "public"."lifecycle_logs" to "service_role";

grant update on table "public"."lifecycle_logs" to "service_role";

grant delete on table "public"."transactions" to "anon";

grant insert on table "public"."transactions" to "anon";

grant references on table "public"."transactions" to "anon";

grant select on table "public"."transactions" to "anon";

grant trigger on table "public"."transactions" to "anon";

grant truncate on table "public"."transactions" to "anon";

grant update on table "public"."transactions" to "anon";

grant delete on table "public"."transactions" to "authenticated";

grant insert on table "public"."transactions" to "authenticated";

grant references on table "public"."transactions" to "authenticated";

grant select on table "public"."transactions" to "authenticated";

grant trigger on table "public"."transactions" to "authenticated";

grant truncate on table "public"."transactions" to "authenticated";

grant update on table "public"."transactions" to "authenticated";

grant delete on table "public"."transactions" to "service_role";

grant insert on table "public"."transactions" to "service_role";

grant references on table "public"."transactions" to "service_role";

grant select on table "public"."transactions" to "service_role";

grant trigger on table "public"."transactions" to "service_role";

grant truncate on table "public"."transactions" to "service_role";

grant update on table "public"."transactions" to "service_role";

grant delete on table "public"."users" to "anon";

grant insert on table "public"."users" to "anon";

grant references on table "public"."users" to "anon";

grant select on table "public"."users" to "anon";

grant trigger on table "public"."users" to "anon";

grant truncate on table "public"."users" to "anon";

grant update on table "public"."users" to "anon";

grant delete on table "public"."users" to "authenticated";

grant insert on table "public"."users" to "authenticated";

grant references on table "public"."users" to "authenticated";

grant select on table "public"."users" to "authenticated";

grant trigger on table "public"."users" to "authenticated";

grant truncate on table "public"."users" to "authenticated";

grant update on table "public"."users" to "authenticated";

grant delete on table "public"."users" to "service_role";

grant insert on table "public"."users" to "service_role";

grant references on table "public"."users" to "service_role";

grant select on table "public"."users" to "service_role";

grant trigger on table "public"."users" to "service_role";

grant truncate on table "public"."users" to "service_role";

grant update on table "public"."users" to "service_role";


