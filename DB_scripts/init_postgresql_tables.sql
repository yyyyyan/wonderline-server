CREATE DATABASE wonderline;
\c wonderline;

/* User is reserved word in PostgreSQL*/
CREATE TABLE _User (
    id TEXT,
    email VARCHAR (254) UNIQUE NOT NULL,
    password CHAR(144) NOT NULL,
    access_level VARCHAR(255) DEFAULT 'everyone',
    name VARCHAR(255) NOT NULL,
    avatar_src TEXT DEFAULT '',
    create_time TIMESTAMP WITH TIME ZONE NOT NULL,
    signature TEXT,
    profile_lq_src TEXT,
    profile_src TEXT,
    follower_nb INTEGER DEFAULT 0,
    PRIMARY KEY (id)
);
CREATE INDEX index_create_time
ON _User (create_time);

/*
A is following B -> from_id = id(A), to_id = id(B)
*/
CREATE TABLE Following (
    from_id TEXT NOT NULL,
    to_id TEXT NOT NULL,
    follow_time TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (from_id) REFERENCES _User(id),
    FOREIGN KEY (to_id) REFERENCES _User(id),
    PRIMARY KEY(from_id, to_id)
);
CREATE INDEX index_from_id
ON Following (from_id);

/*
A is followed by B -> from_id = id(A), to_id = id(B)
*/
CREATE TABLE Followed (
    from_id TEXT NOT NULL,
    to_id TEXT NOT NULL,
    follow_time TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (from_id) REFERENCES _User(id),
    FOREIGN KEY (to_id) REFERENCES _User(id),
    PRIMARY KEY(from_id, to_id)
);
CREATE INDEX index_to_id
ON Followed (from_id);