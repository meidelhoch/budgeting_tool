CREATE TABLE IF NOT EXISTS transactions (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  description TEXT NOT NULL,
  amount NUMERIC(10, 2) NOT NULL,
  category_id INTEGER REFERENCES budget_categories(id) ON DELETE SET NULL,
  reimbursed BOOLEAN NOT NULL DEFAULT FALSE,
  reimbursement_amount NUMERIC(10, 2),
  sinking_fund_id INTEGER REFERENCES sinking_funds(id) ON DELETE SET NULL,
  card TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS sinking_funds (
    id SERIAL PRIMARY KEY,
    fund_name TEXT UNIQUE NOT NULL
);

CREATE TABLE sinking_fund_transactions (
    id SERIAL PRIMARY KEY,
    fund_id INTEGER REFERENCES sinking_funds(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS budget_categories (
    id SERIAL PRIMARY KEY,
    category_name TEXT UNIQUE NOT NULL,
    monthly_budget NUMERIC(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS income (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL
);