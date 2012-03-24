BEGIN;
CREATE TABLE "documents_document" (
    "id" serial NOT NULL PRIMARY KEY,
    "title" varchar(200) NOT NULL,
    "url" varchar(200) NOT NULL,
    "content" varchar(20000) NOT NULL,
    "symbol" varchar(10) NOT NULL,
    "date" date NOT NULL
)
;
CREATE TABLE "documents_stocktick" (
    "id" serial NOT NULL PRIMARY KEY,
    "symbol" varchar(10) NOT NULL,
    "date" date NOT NULL,
    "open" double precision NOT NULL,
    "close" double precision NOT NULL,
    "high" double precision NOT NULL,
    "low" double precision NOT NULL,
    "volume" double precision NOT NULL,
    UNIQUE( symbol, date)
)
;
CREATE TABLE "documents_stockinfo" (
    "id" serial NOT NULL PRIMARY KEY,
    "symbol" varchar(10) NOT NULL UNIQUE,
    "isindex" boolean NOT NULL,
    "name" varchar(200) NOT NULL,
    "sector" varchar(200) NOT NULL,
    "week52high" double precision NOT NULL,
    "week52low" double precision NOT NULL
)
;
COMMIT;
