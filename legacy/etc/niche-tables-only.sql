

CREATE TABLE averagingperiodtypes (
    averagingperiodtypeid integer NOT NULL,
    averagingperiodtype character varying,
    averagingperioddays bigint
);


ALTER TABLE averagingperiodtypes OWNER TO paleo;

--
-- TOC entry 191 (class 1259 OID 16639)
-- Name: averagingperiodtypes_averagingperiodtypeid_seq; Type: SEQUENCE; Schema: public; Owner: paleo
--

CREATE SEQUENCE averagingperiodtypes_averagingperiodtypeid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE averagingperiodtypes_averagingperiodtypeid_seq OWNER TO paleo;

--
-- TOC entry 2191 (class 0 OID 0)
-- Dependencies: 191
-- Name: averagingperiodtypes_averagingperiodtypeid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: paleo
--

ALTER SEQUENCE averagingperiodtypes_averagingperiodtypeid_seq OWNED BY averagingperiodtypes.averagingperiodtypeid;


--
-- TOC entry 182 (class 1259 OID 16587)
-- Name: rasterindex; Type: TABLE; Schema: public; Owner: paleo
--

CREATE TABLE rasterindex (
    recordid integer NOT NULL,
    sourceid integer,
    resolution double precision,
    variableid integer,
    yearsbp integer,
    lastupdate timestamp without time zone DEFAULT now(),
    "tableName" text,
);


ALTER TABLE rasterindex OWNER TO paleo;

--
-- TOC entry 181 (class 1259 OID 16585)
-- Name: rasterindex_recordid_seq; Type: SEQUENCE; Schema: public; Owner: paleo
--

CREATE SEQUENCE rasterindex_recordid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rasterindex_recordid_seq OWNER TO paleo;

--
-- TOC entry 2192 (class 0 OID 0)
-- Dependencies: 181
-- Name: rasterindex_recordid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: paleo
--

ALTER SEQUENCE rasterindex_recordid_seq OWNED BY rasterindex.recordid;


--
-- TOC entry 184 (class 1259 OID 16596)
-- Name: sources; Type: TABLE; Schema: public; Owner: paleo
--

CREATE TABLE sources (
    sourceid integer NOT NULL,
    producer text,
    model text,
    scenario text,
    productversion text,
    producturl character varying,
    lastupdate timestamp without time zone DEFAULT now()
);


ALTER TABLE sources OWNER TO paleo;

--
-- TOC entry 183 (class 1259 OID 16594)
-- Name: sources_sourceid_seq; Type: SEQUENCE; Schema: public; Owner: paleo
--

CREATE SEQUENCE sources_sourceid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE sources_sourceid_seq OWNER TO paleo;

--
-- TOC entry 2193 (class 0 OID 0)
-- Dependencies: 183
-- Name: sources_sourceid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: paleo
--

ALTER SEQUENCE sources_sourceid_seq OWNED BY sources.sourceid;


--
-- TOC entry 190 (class 1259 OID 16630)
-- Name: variableperiodtypes; Type: TABLE; Schema: public; Owner: paleo
--

CREATE TABLE variableperiodtypes (
    variableperiodtypeid integer NOT NULL,
    variableperiodtype character varying
);


ALTER TABLE variableperiodtypes OWNER TO paleo;

--
-- TOC entry 189 (class 1259 OID 16628)
-- Name: variableperiodtypes_variableperiodtypeid_seq; Type: SEQUENCE; Schema: public; Owner: paleo
--

CREATE SEQUENCE variableperiodtypes_variableperiodtypeid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE variableperiodtypes_variableperiodtypeid_seq OWNER TO paleo;

--
-- TOC entry 2194 (class 0 OID 0)
-- Dependencies: 189
-- Name: variableperiodtypes_variableperiodtypeid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: paleo
--

ALTER SEQUENCE variableperiodtypes_variableperiodtypeid_seq OWNED BY variableperiodtypes.variableperiodtypeid;


--
-- TOC entry 194 (class 1259 OID 16652)
-- Name: variables; Type: TABLE; Schema: public; Owner: paleo
--

CREATE TABLE variables (
    variableid integer NOT NULL,
    variabletype integer,
    variableunits integer,
    variableperiod double precision,
    variableperiodtype integer,
    variableaveraging double precision,
    variableaveragingtype integer,
    variabledescription character varying,
    lastupdate timestamp without time zone DEFAULT now()
);


ALTER TABLE variables OWNER TO paleo;

--
-- TOC entry 193 (class 1259 OID 16650)
-- Name: variables_variableid_seq; Type: SEQUENCE; Schema: public; Owner: paleo
--

CREATE SEQUENCE variables_variableid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE variables_variableid_seq OWNER TO paleo;

--
-- TOC entry 2195 (class 0 OID 0)
-- Dependencies: 193
-- Name: variables_variableid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: paleo
--

ALTER SEQUENCE variables_variableid_seq OWNED BY variables.variableid;


--
-- TOC entry 186 (class 1259 OID 16608)
-- Name: variabletypes; Type: TABLE; Schema: public; Owner: paleo
--

CREATE TABLE variabletypes (
    variabletypeid integer NOT NULL,
    variabletype character varying,
    variabletypeabbreviation text
);


ALTER TABLE variabletypes OWNER TO paleo;

--
-- TOC entry 185 (class 1259 OID 16606)
-- Name: variabletypes_variabletypeid_seq; Type: SEQUENCE; Schema: public; Owner: paleo
--

CREATE SEQUENCE variabletypes_variabletypeid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE variabletypes_variabletypeid_seq OWNER TO paleo;

--
-- TOC entry 2196 (class 0 OID 0)
-- Dependencies: 185
-- Name: variabletypes_variabletypeid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: paleo
--

ALTER SEQUENCE variabletypes_variabletypeid_seq OWNED BY variabletypes.variabletypeid;


--
-- TOC entry 188 (class 1259 OID 16619)
-- Name: variableunits; Type: TABLE; Schema: public; Owner: paleo
--

CREATE TABLE variableunits (
    variableunitid integer NOT NULL,
    variableunit text,
    variableunitabbreviation character varying
);


ALTER TABLE variableunits OWNER TO paleo;

--
-- TOC entry 187 (class 1259 OID 16617)
-- Name: variableunits_variableunitid_seq; Type: SEQUENCE; Schema: public; Owner: paleo
--

CREATE SEQUENCE variableunits_variableunitid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE variableunits_variableunitid_seq OWNER TO paleo;

--
-- TOC entry 2197 (class 0 OID 0)
-- Dependencies: 187
-- Name: variableunits_variableunitid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: paleo
--

ALTER SEQUENCE variableunits_variableunitid_seq OWNED BY variableunits.variableunitid;


--
-- TOC entry 2032 (class 2604 OID 16644)
-- Name: averagingperiodtypeid; Type: DEFAULT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY averagingperiodtypes ALTER COLUMN averagingperiodtypeid SET DEFAULT nextval('averagingperiodtypes_averagingperiodtypeid_seq'::regclass);


--
-- TOC entry 2024 (class 2604 OID 16590)
-- Name: recordid; Type: DEFAULT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY rasterindex ALTER COLUMN recordid SET DEFAULT nextval('rasterindex_recordid_seq'::regclass);


--
-- TOC entry 2027 (class 2604 OID 16599)
-- Name: sourceid; Type: DEFAULT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY sources ALTER COLUMN sourceid SET DEFAULT nextval('sources_sourceid_seq'::regclass);


--
-- TOC entry 2031 (class 2604 OID 16633)
-- Name: variableperiodtypeid; Type: DEFAULT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY variableperiodtypes ALTER COLUMN variableperiodtypeid SET DEFAULT nextval('variableperiodtypes_variableperiodtypeid_seq'::regclass);


--
-- TOC entry 2033 (class 2604 OID 16655)
-- Name: variableid; Type: DEFAULT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY variables ALTER COLUMN variableid SET DEFAULT nextval('variables_variableid_seq'::regclass);


--
-- TOC entry 2029 (class 2604 OID 16611)
-- Name: variabletypeid; Type: DEFAULT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY variabletypes ALTER COLUMN variabletypeid SET DEFAULT nextval('variabletypes_variabletypeid_seq'::regclass);


--
-- TOC entry 2030 (class 2604 OID 16622)
-- Name: variableunitid; Type: DEFAULT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY variableunits ALTER COLUMN variableunitid SET DEFAULT nextval('variableunits_variableunitid_seq'::regclass);


--
-- TOC entry 2180 (class 0 OID 16641)
-- Dependencies: 192
-- Data for Name: averagingperiodtypes; Type: TABLE DATA; Schema: public; Owner: paleo
--

COPY averagingperiodtypes (averagingperiodtypeid, averagingperiodtype, averagingperioddays) FROM stdin;
2	Week	7
3	Month	30
4	Quarter	90
5	Year	365
6	Decade	3650
7	Century	36500
\.


--
-- TOC entry 2198 (class 0 OID 0)
-- Dependencies: 191
-- Name: averagingperiodtypes_averagingperiodtypeid_seq; Type: SEQUENCE SET; Schema: public; Owner: paleo
--

SELECT pg_catalog.setval('averagingperiodtypes_averagingperiodtypeid_seq', 8, true);


--
-- TOC entry 2170 (class 0 OID 16587)
-- Dependencies: 182
-- Data for Name: rasterindex; Type: TABLE DATA; Schema: public; Owner: paleo
--

COPY rasterindex (recordid, sourceid, resolution, variableid, yearsbp, lastupdate, "tableName") FROM stdin;
\.


--
-- TOC entry 2199 (class 0 OID 0)
-- Dependencies: 181
-- Name: rasterindex_recordid_seq; Type: SEQUENCE SET; Schema: public; Owner: paleo
--

SELECT pg_catalog.setval('rasterindex_recordid_seq', 1, true);


--
-- TOC entry 2172 (class 0 OID 16596)
-- Dependencies: 184
-- Data for Name: sources; Type: TABLE DATA; Schema: public; Owner: paleo
--

COPY sources (sourceid, producer, model, scenario, productversion, producturl, lastupdate) FROM stdin;
1	Community Earth System Model (CESM)	Community Climate System Model (CCSM)		3.0	http://www.cesm.ucar.edu/models/ccsm3.0/	2016-06-08 09:27:34.234064
2	Community Earth System Model (CESM)	Community Climate System Model (CCSM)		4.0	http://www.cesm.ucar.edu/models/ccsm4.0/	2016-06-08 09:27:34.234064
3	Worldclim	Worldclim		1.4	http://www.worldclim.org/download	2016-06-08 09:27:34.234064
4	PRISM Climate Group	PRISM			http://www.prism.oregonstate.edu/	2016-06-08 09:27:34.234064
6	Community Earth System Model	Community Climate System Model (CCSM)		3.0 [North America Downscaled]	http://www.cesm.ucar.edu/models/ccsm3.0/	2016-06-13 12:41:20.371648
\.


--
-- TOC entry 2200 (class 0 OID 0)
-- Dependencies: 183
-- Name: sources_sourceid_seq; Type: SEQUENCE SET; Schema: public; Owner: paleo
--

SELECT pg_catalog.setval('sources_sourceid_seq', 6, true);


--
-- TOC entry 2178 (class 0 OID 16630)
-- Dependencies: 190
-- Data for Name: variableperiodtypes; Type: TABLE DATA; Schema: public; Owner: paleo
--

COPY variableperiodtypes (variableperiodtypeid, variableperiodtype) FROM stdin;
1	hour
2	day
3	week
4	month
5	quarter
6	year
7	decade
8	century
\.


--
-- TOC entry 2201 (class 0 OID 0)
-- Dependencies: 189
-- Name: variableperiodtypes_variableperiodtypeid_seq; Type: SEQUENCE SET; Schema: public; Owner: paleo
--

SELECT pg_catalog.setval('variableperiodtypes_variableperiodtypeid_seq', 9, true);


--
-- TOC entry 2182 (class 0 OID 16652)
-- Dependencies: 194
-- Data for Name: variables; Type: TABLE DATA; Schema: public; Owner: paleo
--

COPY variables (variableid, variabletype, variableunits, variableperiod, variableperiodtype, variableaveraging, variableaveragingtype, variabledescription, lastupdate) FROM stdin;
9	23	2	1	4	1	6	January Maximum Temperature [C] (Decadal Average)	2016-06-13 11:40:43.160664
10	24	2	1	4	1	6	JanuaryMinimum Temperature  [C]  (Decadal Average)	2016-06-13 11:40:43.160664
11	22	2	1	4	1	6	January Mean Temperature  [C]  (Decadal Average)	2016-06-13 11:40:43.160664
12	25	7	1	4	1	6	January Precipitation [cm] (Decadal Average)	2016-06-13 11:40:43.160664
13	23	2	7	4	1	6	July Maximum Temperature  [C] (Decadal Average)	2016-06-13 11:40:43.160664
14	24	2	7	4	1	6	July Minimum Temperature  [C] (Decadal Average)	2016-06-13 11:40:43.160664
15	22	2	7	4	1	6	July Mean Temperature  [C] (Decadal Average)	2016-06-13 11:40:43.160664
16	25	7	7	4	1	6	July Precipitation [cm] (Decadal Average)	2016-06-13 11:40:43.160664
\.


--
-- TOC entry 2202 (class 0 OID 0)
-- Dependencies: 193
-- Name: variables_variableid_seq; Type: SEQUENCE SET; Schema: public; Owner: paleo
--

SELECT pg_catalog.setval('variables_variableid_seq', 16, true);


--
-- TOC entry 2174 (class 0 OID 16608)
-- Dependencies: 186
-- Data for Name: variabletypes; Type: TABLE DATA; Schema: public; Owner: paleo
--

COPY variabletypes (variabletypeid, variabletype, variabletypeabbreviation) FROM stdin;
22	Mean Temperature	Tavg
23	Maximum Temperature	Tmax
24	Minimum Temperature	Tmin
25	Precipitation	Prcp
26	Diurnal Temperature Range	BIO2
27	Isothermality	BIO3
28	Temperature Seasonality	BIO4
29	Maximum Temperature of Warmest Month	BIO5
30	Minimum Temperature of Coldest Month	BIO6
31	Annual Temperature Range	BIO7
32	Mean Temperature of Wettest Quarter	BIO8
33	Mean Temperature of Driest Quarter	BIO9
34	Mean Temperature of Warmest Quarter	BIO10
35	Mean Temperature of Coldest Quarter	BIO11
36	Precipitation of Wettest Month	BIO13
37	Precipitation of Driest Month	BIO14
38	Precipitation Seasonality	BIO15
39	Precipitation of Wettest Quarter	BIO16
40	Precipitation of Driest Quarter	BIO17
41	Precipitation of Warmest Quarter	BIO18
42	Precipitation of Coldest Quarter	BIO19
\.


--
-- TOC entry 2203 (class 0 OID 0)
-- Dependencies: 185
-- Name: variabletypes_variabletypeid_seq; Type: SEQUENCE SET; Schema: public; Owner: paleo
--

SELECT pg_catalog.setval('variabletypes_variabletypeid_seq', 43, true);


--
-- TOC entry 2176 (class 0 OID 16619)
-- Dependencies: 188
-- Data for Name: variableunits; Type: TABLE DATA; Schema: public; Owner: paleo
--

COPY variableunits (variableunitid, variableunit, variableunitabbreviation) FROM stdin;
1	Degrees Fahrenheit	F
2	Degrees Celsius	C
3	Degrees Kelvin	K
4	Percent	%
6	Millimeters	mm
7	Centimeters	cm
8	Inches	in
\.


--
-- TOC entry 2204 (class 0 OID 0)
-- Dependencies: 187
-- Name: variableunits_variableunitid_seq; Type: SEQUENCE SET; Schema: public; Owner: paleo
--

SELECT pg_catalog.setval('variableunits_variableunitid_seq', 9, true);


--
-- TOC entry 2046 (class 2606 OID 16649)
-- Name: averagingperiodtypes_pkey; Type: CONSTRAINT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY averagingperiodtypes
    ADD CONSTRAINT averagingperiodtypes_pkey PRIMARY KEY (averagingperiodtypeid);


--
-- TOC entry 2036 (class 2606 OID 16593)
-- Name: rasterindex_pkey; Type: CONSTRAINT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY rasterindex
    ADD CONSTRAINT rasterindex_pkey PRIMARY KEY (recordid);


--
-- TOC entry 2038 (class 2606 OID 16605)
-- Name: sources_pkey; Type: CONSTRAINT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY sources
    ADD CONSTRAINT sources_pkey PRIMARY KEY (sourceid);


--
-- TOC entry 2044 (class 2606 OID 16638)
-- Name: variableperiodtypes_pkey; Type: CONSTRAINT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY variableperiodtypes
    ADD CONSTRAINT variableperiodtypes_pkey PRIMARY KEY (variableperiodtypeid);


--
-- TOC entry 2048 (class 2606 OID 16661)
-- Name: variables_pkey; Type: CONSTRAINT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY variables
    ADD CONSTRAINT variables_pkey PRIMARY KEY (variableid);


--
-- TOC entry 2040 (class 2606 OID 16616)
-- Name: variabletypes_pkey; Type: CONSTRAINT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY variabletypes
    ADD CONSTRAINT variabletypes_pkey PRIMARY KEY (variabletypeid);


--
-- TOC entry 2042 (class 2606 OID 16627)
-- Name: variableunits_pkey; Type: CONSTRAINT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY variableunits
    ADD CONSTRAINT variableunits_pkey PRIMARY KEY (variableunitid);


--
-- TOC entry 2050 (class 2606 OID 16687)
-- Name: rasterindex_sourceid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY rasterindex
    ADD CONSTRAINT rasterindex_sourceid_fkey FOREIGN KEY (sourceid) REFERENCES sources(sourceid);


--
-- TOC entry 2049 (class 2606 OID 16682)
-- Name: rasterindex_variableid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY rasterindex
    ADD CONSTRAINT rasterindex_variableid_fkey FOREIGN KEY (variableid) REFERENCES variables(variableid);


--
-- TOC entry 2052 (class 2606 OID 16667)
-- Name: variables_variableaveragingtype_fkey; Type: FK CONSTRAINT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY variables
    ADD CONSTRAINT variables_variableaveragingtype_fkey FOREIGN KEY (variableaveragingtype) REFERENCES averagingperiodtypes(averagingperiodtypeid);


--
-- TOC entry 2053 (class 2606 OID 16672)
-- Name: variables_variableperiodtype_fkey; Type: FK CONSTRAINT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY variables
    ADD CONSTRAINT variables_variableperiodtype_fkey FOREIGN KEY (variableperiodtype) REFERENCES variableperiodtypes(variableperiodtypeid);


--
-- TOC entry 2051 (class 2606 OID 16662)
-- Name: variables_variabletype_fkey; Type: FK CONSTRAINT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY variables
    ADD CONSTRAINT variables_variabletype_fkey FOREIGN KEY (variabletype) REFERENCES variabletypes(variabletypeid);


--
-- TOC entry 2054 (class 2606 OID 16677)
-- Name: variables_variableunits_fkey; Type: FK CONSTRAINT; Schema: public; Owner: paleo
--

ALTER TABLE ONLY variables
    ADD CONSTRAINT variables_variableunits_fkey FOREIGN KEY (variableunits) REFERENCES variableunits(variableunitid);


--
-- TOC entry 2189 (class 0 OID 0)
-- Dependencies: 7
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2016-06-15 09:37:23 CDT

--
-- PostgreSQL database dump complete
--
