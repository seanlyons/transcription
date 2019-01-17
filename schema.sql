-- source tweets. contains a subset of the data returned from the twitter api.
CREATE TABLE
IF NOT EXISTS tw_tweets (
    id integer PRIMARY KEY,
    tw_created_at integer,
    tw_id UNSIGNED BIG INT,
    tw_full_text text,
    tw_api_content text,	-- the full json response body from the api, so we can retrofit data instead of reconsuming it for later features.
    tw_user UNSIGNED BIG INTEGER,
    UNIQUE(tw_id)
);

-- metadata about twitter users who've posted tweets which have gotten favorited.
CREATE TABLE
IF NOT EXISTS tw_users (
    id integer PRIMARY KEY,
    added_by integer,
    tw_id UNSIGNED BIG INT,
    tw_screen_name varchar(64),
    tw_description text,
    tw_name varchar(64),
    tw_profile_image_url text,
    UNIQUE(tw_id)
);

-- conical users can favorite tweets- once a tweet is in the system (tw_tweets) it's unique.
-- favorites have a unique combination key of user:tw_tweets, so there can be many favorites per user, and many favorites per tweet.
CREATE TABLE
IF NOT EXISTS favorites (
    id integer PRIMARY KEY,
    owner integer,
    added integer,
    contextual_id UNSIGNED BIG INT,
    favorite_type integer,
	tags text,			--comma-separated list of tags- alphanum only.
    UNIQUE(owner, favorite_type, contextual_id)
);

-- conical user accounts
CREATE TABLE
IF NOT EXISTS users (
    id integer PRIMARY KEY,
    email text,
    password_hash text,
    password_hash_method text,
    UNIQUE(email)
);

-- entities (images, videos) contained within tweets that have been favorited get ingested, hashed and served from local.
CREATE TABLE
IF NOT EXISTS tw_entities (
    id integer PRIMARY KEY,
    tweet_id UNSIGNED BIG INT,
    media_type text,
    media_url text,
    media_preview text,
    dims_ratio decimal(3,3),
    local_hash text,
    UNIQUE(media_url)
);

-- like tw_tweets, but for mefi posts
CREATE TABLE
IF NOT EXISTS mefi_posts (
    id integer PRIMARY KEY,
    post_id text,
    post_title text,
    post_author text,
    post_text text,
    full_html text,
    UNIQUE(post_id)
);

-- like tw_tweets, but for mefi tweets
CREATE TABLE
IF NOT EXISTS mefi_comments (
    id integer PRIMARY KEY,
    post_id text,
    comment_id UNSIGNED BIG INT,
    comment_author text,
    comment_text text,
    comment_timestamp integer,
    UNIQUE(comment_id)
);

-- CREATE UNIQUE INDEX tw_entities_url_idx ON tw_entities (media_url);
CREATE UNIQUE INDEX tw_entities_local_idx ON tw_entities (local_hash);
