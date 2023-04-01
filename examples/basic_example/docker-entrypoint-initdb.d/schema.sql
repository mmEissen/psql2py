CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    birthday DATE NOT NULL
);

CREATE TABLE comments (
    comment_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL references users(user_id),
    content text NOT NULL
);