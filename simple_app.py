"""
Simple Flask app to serve the loan engine UI and APIs
This bypasses Django ORM connection issues
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
import psycopg2
import csv
import io
from datetime import datetime
import requests

app = Flask(__name__, template_folder='backend/templates', static_folder='backend/static')

# Database connection
def get_db():
    return psycopg2.connect(
        host='localhost',
        port=5432,
        dbname='loan_engine',
        user='loanuser',
        password='loanpass123'
    )

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload-csv/', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'error': 'Only CSV files allowed'}), 400
    
    try:
        # Read CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        conn = get_db()
        cur = conn.cursor()
        
        user_count = 0
        for row in csv_reader:
            cur.execute("""
                INSERT INTO loan_app_userprofile 
                (name, email, age, credit_score, annual_income, employment_status, loan_purpose, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
            """, (
                row['name'],
                row['email'],
                int(row['age']),
                int(row['credit_score']),
                float(row['annual_income']),
                row['employment_status'],
                row.get('loan_purpose', 'Personal'),
                datetime.now()
            ))
            user_count += 1
        
        # Save CSV upload record
        cur.execute("""
            INSERT INTO loan_app_csvupload (file, uploaded_at, status, user_count)
            VALUES (%s, %s, %s, %s)
        """, (file.filename, datetime.now(), 'completed', user_count))
        
        conn.commit()
        
        # Trigger n8n workflow
        try:
            requests.post('http://localhost:5678/webhook/user-matching', 
                         json={'users_uploaded': user_count}, 
                         timeout=2)
        except:
            pass  # Workflow trigger is optional
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'{user_count} users uploaded successfully',
            'user_count': user_count
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/dashboard/')
def dashboard():
    conn = get_db()
    cur = conn.cursor()
    
    # Get statistics
    cur.execute("SELECT COUNT(*) FROM loan_app_userprofile")
    total_users = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM loan_app_loanproduct")
    total_products = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM loan_app_userloanmatch")
    total_matches = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return render_template('dashboard.html', 
                          total_users=total_users,
                          total_products=total_products,
                          total_matches=total_matches)

# API endpoints for n8n
@app.route('/api/users/', methods=['GET'])
def get_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM loan_app_userprofile ORDER BY created_at DESC")
    columns = [desc[0] for desc in cur.description]
    users = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(users)

@app.route('/api/products/', methods=['GET'])
def get_products():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM loan_app_loanproduct")
    columns = [desc[0] for desc in cur.description]
    products = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(products)

@app.route('/api/create-match/', methods=['POST'])
def create_match():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO loan_app_userloanmatch (user_id, product_id, match_score, created_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, product_id) DO UPDATE SET match_score = EXCLUDED.match_score
    """, (data['user_id'], data['product_id'], data['match_score'], datetime.now()))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    print("=" * 60)
    print("ClickPe Loan Engine - Starting...")
    print("=" * 60)
    print(f"🌐 Web Interface: http://localhost:8000")
    print(f"🔧 n8n Interface: http://localhost:5678 (admin/admin123)")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8000, debug=True)
