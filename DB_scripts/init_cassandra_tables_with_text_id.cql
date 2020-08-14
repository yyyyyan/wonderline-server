CREATE KEYSPACE IF NOT EXISTS wonderline WITH replication = {'class':'SimpleStrategy','replication_factor':1};

USE wonderline;

CREATE TYPE IF NOT EXISTS reply (
    reply_id text,
    user_id text,
    create_time timestamp,
    content text,
    liked_nb smallint,
);

CREATE TYPE IF NOT EXISTS reduced_photo (
    photo_id text,
    trip_id text,
    owner text,
    access_level text,
    status text,
    location text,
    country text,
    create_time timestamp,
    upload_time timestamp,
    width smallint,
    height smallint,
    low_quality_src text,
    src text,
    liked_nb smallint
);

CREATE TYPE IF NOT EXISTS rearranged_photo (
    photo frozen<reduced_photo>,
    ratio_type text
);

CREATE TABLE IF NOT EXISTS comment (
    comment_id text,
    user_id text,
    create_time timestamp,
    content text,
    liked_nb smallint,
    reply_nb smallint,
    replies set<frozen<reply>>,
    PRIMARY KEY ((comment_id), create_time)
) WITH CLUSTERING ORDER BY (create_time DESC);

CREATE TABLE IF NOT EXISTS comments_by_photo (
    photo_id text,
    comment_id text,
    user_id text,
    create_time timestamp,
    content text,
    liked_nb smallint,
    reply_nb smallint,
    replies set<frozen<reply>>,
    PRIMARY KEY ((photo_id), create_time, comment_id)
) WITH CLUSTERING ORDER BY (create_time DESC);


CREATE TABLE IF NOT EXISTS photo (
    photo_id text,
    trip_id text,
    owner text,
    access_level text,
    status text,
    location text,
    country text,
    create_time timestamp,
    upload_time timestamp,
    width smallint,
    height smallint,
    low_quality_src text,
    src text,
    liked_nb smallint,
    high_quality_src text,
    liked_users set<text>,
    mentioned_users set<text>,
    comment_nb smallint,
    comments set<text>,
    PRIMARY KEY (photo_id)
);

CREATE TABLE IF NOT EXISTS trip (
    trip_id text,
    access_level text,
    status text,
    name text,
    description text,
    users set<text>,
    create_time timestamp,
    begin_time timestamp,
    end_time timestamp,
    photo_nb smallint,
    cover_photo reduced_photo,
    liked_nb smallint,
    shared_nb smallint,
    saved_nb smallint,
    PRIMARY KEY (trip_id)
);

CREATE TABLE IF NOT EXISTS trips_by_user (
    user_id text,
    trip_id text,
    access_level text,
    name text,
    description text,
    users set<text>,
    create_time timestamp,
    begin_time timestamp,
    end_time timestamp,
    photo_nb smallint,
    cover_photo text,
    PRIMARY KEY ((user_id), create_time, trip_id),
) WITH CLUSTERING ORDER BY (create_time DESC);

CREATE TABLE IF NOT EXISTS photos_by_trip (
    trip_id text,
    photo_id text,
    owner text,
    access_level text,
    location text,
    country text,
    create_time timestamp,
    upload_time timestamp,
    width smallint,
    height smallint,
    low_quality_src text,
    src text,
    liked_nb smallint,
    PRIMARY KEY ((trip_id), create_time, photo_id)
) WITH CLUSTERING ORDER BY (create_time DESC);

CREATE TABLE IF NOT EXISTS albums_by_user (
    user_id text,
    create_time timestamp,
    album_id text,
    access_level text,
    cover_photos set<frozen<rearranged_photo>>,
    PRIMARY KEY ((user_id), create_time, album_id)
) WITH CLUSTERING ORDER BY (create_time DESC);

CREATE TABLE IF NOT EXISTS mentions_by_user (
    user_id text,
    create_time timestamp,
    mention_id text,
    access_level text,
    photo frozen<reduced_photo>,
    PRIMARY KEY ((user_id), create_time, mention_id)
) WITH CLUSTERING ORDER BY (create_time DESC);

CREATE TABLE IF NOT EXISTS highlights_by_user (
    user_id text,
    create_time timestamp,
    highlight_id text,
    access_level text,
    cover_photo frozen<reduced_photo>,
    description text,
    PRIMARY KEY ((user_id), create_time, highlight_id)
);