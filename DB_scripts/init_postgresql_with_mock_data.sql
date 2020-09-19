\c wonderline;
INSERT INTO _user (
    id,
    access_level,
    name,
    avatar_src,
    create_time,
    signature,
    profile_lq_src,
    profile_src,
    follower_nb
) VALUES (
    'user_001',
    'everyone',
    'Jon Snow',
    'avatar.png',
    to_timestamp(1596134528628::numeric/1000),
    'The king of the North, Danny is my QUEEN!',
    'bkg.png',
    'bkg.png',
    6
);

INSERT INTO _user (
    id,
    access_level,
    name,
    avatar_src,
    create_time,
    signature,
    profile_lq_src,
    profile_src,
    follower_nb
) VALUES (
    'user_002',
    'everyone',
    'Daenerys Targaryen',
    'avatar.png',
    to_timestamp(1596134628628::numeric/1000),
    'How many times must I say no before you understand?',
    'bkg.png',
    'bkg.png',
    3
);

INSERT INTO _user (
    id,
    access_level,
    name,
    avatar_src,
    create_time,
    signature,
    profile_lq_src,
    profile_src,
    follower_nb
) VALUES (
    'user_003',
    'everyone',
    'Red Dragon',
    'avatar.png',
    to_timestamp(1596134728628::numeric/1000),
    '',
    'bkg.png',
    'bkg.png',
    2
);

INSERT INTO _user (
    id,
    access_level,
    name,
    avatar_src,
    create_time,
    signature,
    profile_lq_src,
    profile_src,
    follower_nb
) VALUES (
    'user_004',
    'everyone',
    'Blue Dragon',
    'avatar.png',
    to_timestamp(1596137528628::numeric/1000),
    '',
    'bkg.png',
    'bkg.png',
    3
);

INSERT INTO _user (
    id,
    access_level,
    name,
    avatar_src,
    create_time,
    signature,
    profile_lq_src,
    profile_src,
    follower_nb
) VALUES (
    'user_005',
    'everyone',
    'Samwell Tarly',
    'avatar.png',
    to_timestamp(1596138528628::numeric/1000),
    'Do you ever find anyone in your dream?',
    'bkg.jpeg',
    'bkg.jpeg',
    1
);

INSERT INTO _user (
    id,
    access_level,
    name,
    avatar_src,
    create_time,
    signature,
    profile_lq_src,
    profile_src,
    follower_nb
) VALUES (
    'user_006',
    'everyone',
    'Cersei Lannister',
    'avatar.png',
    to_timestamp(1596139528628::numeric/1000),
    'You want a queen, earn her',
    'bkg.jpeg',
    'bkg.jpeg',
    1
);

INSERT INTO _user (
    id,
    access_level,
    name,
    avatar_src,
    create_time,
    signature,
    profile_lq_src,
    profile_src,
    follower_nb
) VALUES (
    'user_007',
    'everyone',
    'Night King',
    'avatar.png',
    to_timestamp(1596142528628::numeric/1000),
    'Winter has come',
    'bkg.jpeg',
    'bkg.jpeg',
    5
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_001',
    'user_002',
    to_timestamp(1596142628628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_001',
    'user_003',
    to_timestamp(1596142728628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_001',
    'user_004',
    to_timestamp(1596142828628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_001',
    'user_005',
    to_timestamp(1596142928628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_001',
    'user_006',
    to_timestamp(1596143028628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_001',
    'user_007',
    to_timestamp(1596143128628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_002',
    'user_001',
    to_timestamp(1596143228628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_002',
    'user_003',
    to_timestamp(1596143328628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_002',
    'user_004',
    to_timestamp(1596143428628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_003',
    'user_002',
    to_timestamp(1596143528628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_003',
    'user_004',
    to_timestamp(1596143628628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_004',
    'user_002',
    to_timestamp(1596143728628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_004',
    'user_003',
    to_timestamp(1596143828628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_004',
    'user_007',
    to_timestamp(1596143928628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_005',
    'user_001',
    to_timestamp(1596144028628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_006',
    'user_002',
    to_timestamp(1596144128628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_007',
    'user_001',
    to_timestamp(1596144228628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_007',
    'user_002',
    to_timestamp(1596144328628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_007',
    'user_003',
    to_timestamp(1596144428628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_007',
    'user_004',
    to_timestamp(1596144528628::numeric/1000)
);

INSERT INTO Followed (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_007',
    'user_005',
    to_timestamp(1596144628628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_001',
    'user_002',
    to_timestamp(1596142628628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_001',
    'user_005',
    to_timestamp(1596144028628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_001',
    'user_007',
    to_timestamp(1596144228628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_002',
    'user_001',
    to_timestamp(1596142628628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_002',
    'user_003',
    to_timestamp(1596143528628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_002',
    'user_004',
    to_timestamp(1596143728628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_002',
    'user_006',
    to_timestamp(1596144128628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_002',
    'user_007',
    to_timestamp(1596144328628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_003',
    'user_002',
    to_timestamp(1596143328628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_003',
    'user_004',
    to_timestamp(1596143828628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_003',
    'user_007',
    to_timestamp(1596144428628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_004',
    'user_001',
    to_timestamp(1596142828628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_004',
    'user_002',
    to_timestamp(1596143428628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_004',
    'user_003',
    to_timestamp(1596143628628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_004',
    'user_007',
    to_timestamp(1596144528628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_005',
    'user_001',
    to_timestamp(1596142928628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_005',
    'user_007',
    to_timestamp(1596144628628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_006',
    'user_001',
    to_timestamp(1596143028628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_007',
    'user_001',
    to_timestamp(1596143128628::numeric/1000)
);

INSERT INTO Following (
    from_id,
    to_id,
    follow_time
) VALUES (
    'user_007',
    'user_004',
    to_timestamp(1596143928628::numeric/1000)
);