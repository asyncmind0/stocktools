CREATE TABLE IF NOT EXISTS indices (sym text, name text,
UNIQUE(sym) ON CONFLICT REPLACE);

CREATE TABLE IF NOT EXISTS analytics
(sym text, name text, sector text, week52high real,
week52low real, last_price real, UNIQUE(sym) ON CONFLICT REPLACE);

CREATE TABLE IF NOT EXISTS stocks
(sym text, date integer, open real, close real,
high real, low real, volume real, UNIQUE(sym,date)
ON CONFLICT REPLACE);

CREATE TABLE IF NOT EXISTS users
(
id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
firstname varchar(20),
lastname varchar(20)
);

CREATE TABLE IF NOT EXISTS portfolios
(
id INT AUTO_INCREMENT PRIMARY KEY NOT NULL ,
userid INT,
name varchar(20),
FOREIGN KEY(userid) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS trades
(
id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
portfolioid int,
sym text,
date integer,
cost real,
fee real,
quantity real,
FOREIGN KEY(portfolioid) REFERENCES portfolios(id)
);


CREATE VIRTUAL TABLE  fts USING FTS3(sym , name );
