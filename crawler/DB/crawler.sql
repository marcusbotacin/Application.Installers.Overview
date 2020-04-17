-- Giovanni Bertao
-- UNICAMP 2018
--
-- Database SQL file

PRAGMA foreign_keys=ON;
PRAGMA temp_store=MEMORY;
PRAGMA journal_mode=MEMORY;
PRAGMA synchronous=OFF;
BEGIN TRANSACTION;

-- Downloads
CREATE TABLE Downloads(
MD5 TEXT,
NAME TEXT,
DATE TEXT,
RANK TEXT,
SITE TEXT);

COMMIT;
