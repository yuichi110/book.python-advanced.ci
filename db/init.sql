CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE TABLE IF NOT EXISTS item
(
    id uuid DEFAULT uuid_generate_v4(),
    name text
);