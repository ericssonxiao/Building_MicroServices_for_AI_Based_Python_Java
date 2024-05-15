CREATE DATABASE notes;

\c notes;
DROP TABLE IF EXISTS notes CASCADE;
CREATE TABLE notes (
    id BIGSERIAL PRIMARY KEY,
    title varchar(100),
    content varchar(500),
    completed BOOLEAN
);
