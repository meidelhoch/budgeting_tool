CREATE TABLE IF NOT EXISTS transactions (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  description TEXT NOT NULL,
  amount NUMERIC(10, 2) NOT NULL,
  category TEXT NOT NULL,
  reimbursed BOOLEAN NOT NULL DEFAULT FALSE,
  reimbursement_amount NUMERIC(10, 2) DEFAULT NULL,
  card TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS sinking_funds (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
);

CREATE TABLE sinking_fund_transactions (
    id SERIAL PRIMARY KEY,
    fund_id INTEGER REFERENCES sinking_funds(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
);