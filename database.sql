-- Database Dump
-- Date: 2026-04-08T22:30:33.196420

-- Table: users
INSERT INTO users VALUES ('1', 'alice', 'alice@example.com', '2026-04-08 18:23:19');
INSERT INTO users VALUES ('2', 'bob', 'bob@example.com', '2026-04-08 18:23:19');
INSERT INTO users VALUES ('3', 'charlie', 'c@test.com', '2026-04-08 18:56:23');

-- Table: notes
INSERT INTO notes VALUES ('1', 'None', 'setup', '"Installed SQLite database toolkit" tags:test', '', '2026-04-08 18:23:19');
INSERT INTO notes VALUES ('2', 'None', 'todo', '"Learn Qwen fine-tuning" tags:ai,learning', '', '2026-04-08 18:23:19');
INSERT INTO notes VALUES ('3', 'None', 'API Test', 'Created via REST API', '', '2026-04-08 18:56:23');
INSERT INTO notes VALUES ('4', 'None', 'complete task 1', 'show everything', 'None', '2026-04-08 19:03:18');
INSERT INTO notes VALUES ('5', 'None', 'test-note', 'created via ai assistant', 'None', '2026-04-08 19:05:54');
INSERT INTO notes VALUES ('6', 'None', 'test-ai-note', 'created by ai assistant automatically', 'None', '2026-04-08 19:15:27');

-- Table: projects
INSERT INTO projects VALUES ('1', 'myapp', '"Cool AI project"', 'active', '2026-04-08 18:23:19');

-- Table: tasks
INSERT INTO tasks VALUES ('1', '1', 'build frontend', '1', '0', '2026-04-08 18:23:19');
INSERT INTO tasks VALUES ('2', '1', 'setup database', '1', '0', '2026-04-08 18:23:19');
INSERT INTO tasks VALUES ('3', '1', 'Test API', '0', '5', '2026-04-08 18:56:24');
INSERT INTO tasks VALUES ('4', '1', 'Fix critical login bug', '0', '5', '2026-04-08 20:18:07');
INSERT INTO tasks VALUES ('5', '1', 'Add new feature later', '0', '2', '2026-04-08 20:18:08');
INSERT INTO tasks VALUES ('6', '1', 'Important database update', '0', '3', '2026-04-08 20:18:08');
INSERT INTO tasks VALUES ('7', '1', 'Maybe add dark mode', '0', '2', '2026-04-08 20:18:08');

