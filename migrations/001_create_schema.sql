CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  full_name VARCHAR(100),
  bio TEXT,
  deleted_at TIMESTAMP NULL
);

CREATE TABLE skills (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE user_skills (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  skill_id INT REFERENCES skills(id) ON DELETE CASCADE
);

CREATE TABLE service_requests (
  id SERIAL PRIMARY KEY,
  requester_id INT REFERENCES users(id) ON DELETE CASCADE,
  provider_id INT REFERENCES users(id) ON DELETE CASCADE,
  skill_id INT REFERENCES skills(id),
  time TIMESTAMP NOT NULL,
  duration INT NOT NULL,
  credit_cost INT NOT NULL,
  status VARCHAR(20) CHECK (status IN ('pending', 'accepted', 'rejected', 'completed')) DEFAULT 'pending',
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE reviews (
  id SERIAL PRIMARY KEY,
  service_request_id INT REFERENCES service_requests(id) ON DELETE CASCADE,
  reviewer_id INT REFERENCES users(id),
  reviewee_id INT REFERENCES users(id),
  rating INT CHECK (rating BETWEEN 1 AND 5),
  comments TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
