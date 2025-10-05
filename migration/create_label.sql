-- Table: public.labels

-- DROP TABLE IF EXISTS public.labels;

CREATE TABLE IF NOT EXISTS public.labels
(
    id integer NOT NULL DEFAULT nextval('labels_id_seq'::regclass),
    user_id integer NOT NULL,
    celestial_object text COLLATE pg_catalog."default" NOT NULL,
    title text COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default",
    coordinates jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT labels_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.labels
    OWNER to nasa_user;

GRANT ALL ON TABLE public.labels TO nasa_user;