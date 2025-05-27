-- Insert users with bcrypt hashed passwords (all passwords are 'password123')
INSERT INTO users (username, email, password_hash, full_name, bio)
VALUES
  ('alice', 'alice@example.com', '$2b$12$K3JNi5xUQxov9m.EZFDZGegl2/uSNJtJGHCaNDZQ.FnKOzKGnFEJ.', 'Alice A.', 'Bio for Alice'),
  ('bob', 'bob@example.com', '$2b$12$K3JNi5xUQxov9m.EZFDZGegl2/uSNJtJGHCaNDZQ.FnKOzKGnFEJ.', 'Bob B.', 'Bio for Bob'),
  ('carol', 'carol@example.com', '$2b$12$K3JNi5xUQxov9m.EZFDZGegl2/uSNJtJGHCaNDZQ.FnKOzKGnFEJ.', 'Carol C.', 'Bio for Carol'),
  ('dave', 'dave@example.com', '$2b$12$K3JNi5xUQxov9m.EZFDZGegl2/uSNJtJGHCaNDZQ.FnKOzKGnFEJ.', 'Dave D.', 'Bio for Dave'),
  ('eve', 'eve@example.com', '$2b$12$K3JNi5xUQxov9m.EZFDZGegl2/uSNJtJGHCaNDZQ.FnKOzKGnFEJ.', 'Eve E.', 'Bio for Eve');

-- Insert skills
INSERT INTO skills (name)
VALUES
  ('UX Design'),
  ('French Tutoring'),
  ('JavaScript Programming'),
  ('Guitar Lessons'),
  ('Plumbing');

-- Assign skills to users
INSERT INTO user_skills (user_id, skill_id)
VALUES
  (1, 1),
  (2, 2),
  (3, 3),
  (4, 4),
  (5, 5);
