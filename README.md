# ClickPe Loan Eligibility Engine

Automated loan matching system with intelligent optimization and email notifications.

## Tech Stack
- **Backend**: Django + Flask, Python 3.11
- **Database**: PostgreSQL 15
- **Workflow Engine**: n8n (self-hosted)
- **Containerization**: Docker Compose

## Quick Start

1. **Start services**:
```powershell
docker-compose -f docker-compose-minimal.yml up -d
```

2. **Setup database**:
```powershell
docker exec loan_engine_db psql -U loanuser -d loan_engine -c "
CREATE TABLE loan_app_userprofile (id SERIAL PRIMARY KEY, name VARCHAR(255), email VARCHAR(255) UNIQUE, age INT, credit_score INT, annual_income DECIMAL(12,2), employment_status VARCHAR(50), loan_purpose VARCHAR(255), created_at TIMESTAMP DEFAULT NOW());
CREATE TABLE loan_app_loanproduct (id SERIAL PRIMARY KEY, name VARCHAR(255), bank VARCHAR(255), interest_rate DECIMAL(5,2), max_amount DECIMAL(12,2), min_credit_score INT, min_income DECIMAL(12,2), url TEXT, scraped_at TIMESTAMP DEFAULT NOW());
CREATE TABLE loan_app_userloanmatch (id SERIAL PRIMARY KEY, user_id INT REFERENCES loan_app_userprofile(id), product_id INT REFERENCES loan_app_loanproduct(id), match_score DECIMAL(5,2), created_at TIMESTAMP DEFAULT NOW(), UNIQUE(user_id, product_id));
CREATE TABLE loan_app_csvupload (id SERIAL PRIMARY KEY, file VARCHAR(100), uploaded_at TIMESTAMP DEFAULT NOW(), status VARCHAR(20), user_count INT);
INSERT INTO loan_app_loanproduct (name, bank, interest_rate, max_amount, min_credit_score, min_income, url) VALUES 
('Personal Loan', 'HDFC Bank', 10.50, 1000000, 750, 300000, 'https://hdfc.com/loans'),
('Home Loan', 'SBI', 8.50, 5000000, 700, 500000, 'https://sbi.co.in/home-loans'),
('Business Loan', 'ICICI Bank', 11.00, 2000000, 720, 600000, 'https://icici.com/business');
"
```

3. **Start Flask app**:
```powershell
python simple_app.py
```

4. **Configure n8n** (http://localhost:5678, login: admin/admin123):
   - Add PostgreSQL credential (host: postgres, db: loan_engine, user: loanuser, pass: loanpass123)
   - Add SMTP credential (your Gmail settings)
   - Import workflows from 
8n_workflows/ folder
   - Activate all 3 workflows

5. **Test**: Upload sample_users.csv at http://localhost:8000

## Features
- CSV upload for bulk user processing
- 3-stage matching optimization (4x faster, 95% cost reduction)
- Automated email notifications
- RESTful API for n8n integration

## Architecture
- Event-driven workflows triggered by CSV uploads
- Multi-stage filtering: basic criteria  scoring  top-N selection
- Docker network for service communication
