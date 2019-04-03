
---
-- schema
CREATE TABLE regions (
  id integer PRIMARY KEY AUTOINCREMENT,
  name varchar(64) NOT NULL
);

CREATE TABLE cities (
  id integer PRIMARY KEY AUTOINCREMENT,
  region integer REFERENCES regions(id),
  name varchar(64) NOT NULL
);

CREATE TABLE comments (
  id integer PRIMARY KEY AUTOINCREMENT,
  sname varchar(128) NOT NULL,
  fname varchar(128) NOT NULL,
  pname varchar(128),
  city integer REFERENCES cities(id),
  phone varchar(10),
  email varchar(128),
  comment text
);

---
-- data
INSERT INTO regions(id, name) VALUES (1, 'Краснодарский край');
INSERT INTO regions(id, name) VALUES (2, 'Ставропольский край');
INSERT INTO regions(id, name) VALUES (3, 'Ростовская область');
INSERT INTO cities(region, name) VALUES (1, 'Краснодар');
INSERT INTO cities(region, name) VALUES (1, 'Кропоткин');
INSERT INTO cities(region, name) VALUES (1, 'Славянск');
INSERT INTO cities(region, name) VALUES (2, 'Ставрополь');
INSERT INTO cities(region, name) VALUES (2, 'Пятигорск');
INSERT INTO cities(region, name) VALUES (2, 'Кисловодск');
INSERT INTO cities(region, name) VALUES (2, 'Михайловск');
INSERT INTO cities(region, name) VALUES (3, 'Ростов');
INSERT INTO cities(region, name) VALUES (3, 'Шахты');
INSERT INTO cities(region, name) VALUES (3, 'Батайск');
