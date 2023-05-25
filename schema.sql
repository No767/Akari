--
-- PostgreSQL database dump
--

-- Dumped from database version 15.3 (Debian 15.3-1.pgdg110+1)
-- Dumped by pg_dump version 15.3 (Debian 15.3-1.pgdg110+1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: Guild; Type: TABLE; Schema: public; Owner: Akari
--

CREATE TABLE public."Guild" (
    id bigint NOT NULL,
    name text NOT NULL
);


ALTER TABLE public."Guild" OWNER TO "Akari";

--
-- Name: Tag; Type: TABLE; Schema: public; Owner: Akari
--

CREATE TABLE public."Tag" (
    id text NOT NULL,
    user_id bigint NOT NULL,
    guild_id bigint NOT NULL,
    name text NOT NULL,
    aliases text[],
    content text NOT NULL,
    created_at timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public."Tag" OWNER TO "Akari";

--
-- Name: User; Type: TABLE; Schema: public; Owner: Akari
--

CREATE TABLE public."User" (
    id bigint NOT NULL
);


ALTER TABLE public."User" OWNER TO "Akari";

--
-- Name: Guild Guild_pkey; Type: CONSTRAINT; Schema: public; Owner: Akari
--

ALTER TABLE ONLY public."Guild"
    ADD CONSTRAINT "Guild_pkey" PRIMARY KEY (id);


--
-- Name: Tag Tag_pkey; Type: CONSTRAINT; Schema: public; Owner: Akari
--

ALTER TABLE ONLY public."Tag"
    ADD CONSTRAINT "Tag_pkey" PRIMARY KEY (id);


--
-- Name: User User_pkey; Type: CONSTRAINT; Schema: public; Owner: Akari
--

ALTER TABLE ONLY public."User"
    ADD CONSTRAINT "User_pkey" PRIMARY KEY (id);


--
-- Name: Guild_id_key; Type: INDEX; Schema: public; Owner: Akari
--

CREATE UNIQUE INDEX "Guild_id_key" ON public."Guild" USING btree (id);


--
-- Name: User_id_key; Type: INDEX; Schema: public; Owner: Akari
--

CREATE UNIQUE INDEX "User_id_key" ON public."User" USING btree (id);


--
-- Name: Tag Tag_guild_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Akari
--

ALTER TABLE ONLY public."Tag"
    ADD CONSTRAINT "Tag_guild_id_fkey" FOREIGN KEY (guild_id) REFERENCES public."Guild"(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: Tag Tag_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: Akari
--

ALTER TABLE ONLY public."Tag"
    ADD CONSTRAINT "Tag_user_id_fkey" FOREIGN KEY (user_id) REFERENCES public."User"(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

