from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import sqlite3
from weasyprint import HTML
from datetime import datetime
import io

app = Flask(__name__)
DATABASE = 'hseq_5s.db'
app.secret_key = '12345'  # Replace with a strong, random key

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create HSEQ table with correct columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hseq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            organisation TEXT,
            category TEXT,
            responsible_team TEXT,
            value INTEGER,
            health_safety_index INTEGER DEFAULT 0,
            emergency_preparedness INTEGER DEFAULT 0,
            first_aid INTEGER DEFAULT 0,
            absenteeism INTEGER DEFAULT 0,
            employee_wellness INTEGER DEFAULT 0,
            accident_cases INTEGER DEFAULT 0,
            safety_training INTEGER DEFAULT 0,
            equipment_usage INTEGER DEFAULT 0,
            safety_audits INTEGER DEFAULT 0,
            risk_management INTEGER DEFAULT 0,
            defect_rate INTEGER DEFAULT 0,
            compliance INTEGER DEFAULT 0,
            customer_feedback INTEGER DEFAULT 0,
            inspection_frequency INTEGER DEFAULT 0,
            process_efficiency INTEGER DEFAULT 0,
            energy_efficiency INTEGER DEFAULT 0,
            waste_management INTEGER DEFAULT 0,
            emissions_monitoring INTEGER DEFAULT 0,
            water_usage INTEGER DEFAULT 0,
            regulation_compliance INTEGER DEFAULT 0
        );
    ''')

    # Create 5S table with correct structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS five_s (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            category TEXT,
            responsible_team TEXT,
            value INTEGER,
            sort INTEGER DEFAULT 0,
            straighten INTEGER DEFAULT 0,
            shine INTEGER DEFAULT 0,
            standardize INTEGER DEFAULT 0,
            sustain INTEGER DEFAULT 0,
            unnecessary_items_removed INTEGER DEFAULT 0,
            red_tagged_items INTEGER DEFAULT 0,
            repaired_items_kept INTEGER DEFAULT 0,
            housekeeping_done INTEGER DEFAULT 0,
            facility_inspection INTEGER DEFAULT 0,
            everything_in_place INTEGER DEFAULT 0,
            labeling_done INTEGER DEFAULT 0,
            tool_outlines INTEGER DEFAULT 0,
            aisle_markings INTEGER DEFAULT 0,
            pallet_zones INTEGER DEFAULT 0,
            cleaning_done INTEGER DEFAULT 0,
            root_cause_analysis INTEGER DEFAULT 0,
            equipment_maintenance INTEGER DEFAULT 0,
            zone_division INTEGER DEFAULT 0,
            visual_controls INTEGER DEFAULT 0,
            set_standards INTEGER DEFAULT 0,
            inspection_methods INTEGER DEFAULT 0,
            commitment_to_steps INTEGER DEFAULT 0,
            evaluations_done INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            department TEXT NOT NULL,
            financial_impact REAL NOT NULL,
            location TEXT NOT NULL
        )
    ''')

    # Rename the table from incidents to incidentreport to avoid conflicts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidentreport (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,  -- Injury, Near Miss, etc.
            department TEXT NOT NULL,
            injured_job_title TEXT,
            injured_age INTEGER,
            injured_gender TEXT,
            body_part_affected TEXT,
            time_of_day TEXT,
            time_into_shift TEXT,
            machine_equipment TEXT,
            operation TEXT,
            causation TEXT,
            location TEXT,
            financial_impact REAL,
            reportable BOOLEAN DEFAULT 0,
            description TEXT
        )
    ''')

    # Create Teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create Persons table linked to Teams (missing in your code)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            team_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('DROP TABLE IF EXISTS incidentreport')

    # Create tables to store incidents
    cursor.execute('''
        CREATE TABLE incidentreport (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,  -- Injury, Near Miss, etc.
            department TEXT NOT NULL,
            injured_job_title TEXT,
            injured_age INTEGER,
            injured_gender TEXT,
            body_part_affected TEXT,
            time_of_day TEXT,
            time_into_shift TEXT,
            machine_equipment TEXT,
            operation TEXT,
            causation TEXT,
            location TEXT,
            financial_impact REAL,
            reportable BOOLEAN DEFAULT 0,
            description TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Add demo data
def add_demo_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Add demo teams
    cursor.executemany('INSERT OR IGNORE INTO teams (name) VALUES (?)', [
        ('Team Alpha',), ('Team Beta',), ('Team Gamma',)
    ])

    # Add demo HSEQ records for all categories and subcategories
    hseq_data = [
        ('2025-01-01', 'Completed', 'Company A', 'Health', 'Team Alpha', 90,
        5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),

        ('2025-01-05', 'In Progress', 'Company B', 'Safety', 'Team Beta', 85,
        0, 0, 0, 0, 0, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),

        ('2025-01-10', 'Completed', 'Company A', 'Quality', 'Team Gamma', 80,
        4, 5, 3, 1, 2, 0, 0, 3, 4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),

        ('2025-01-12', 'In Progress', 'Company C', 'Environment', 'Team Alpha', 95,
        5, 4, 3, 4, 5, 0, 2, 0, 0, 0, 0, 0, 3, 4, 5, 1, 0, 0, 2, 4),

        ('2025-01-15', 'Completed', 'Company A', 'Health', 'Team Beta', 88,
        4, 3, 2, 5, 1, 0, 2, 3, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),

        ('2025-01-18', 'In Progress', 'Company B', 'Safety', 'Team Gamma', 82,
        3, 2, 4, 1, 0, 4, 3, 2, 3, 1, 2, 0, 0, 0, 1, 3, 2, 0, 0, 0),

        ('2025-01-22', 'Completed', 'Company C', 'Quality', 'Team Alpha', 85,
        5, 4, 3, 2, 3, 0, 0, 4, 2, 1, 0, 0, 0, 1, 0, 1, 2, 0, 0, 0),

        ('2025-01-25', 'In Progress', 'Company A', 'Environment', 'Team Beta', 78,
        4, 2, 3, 1, 4, 0, 1, 3, 0, 0, 3, 0, 2, 0, 3, 1, 2, 4, 1, 0),

        ('2025-01-28', 'Completed', 'Company B', 'Health', 'Team Gamma', 93,
        5, 4, 2, 3, 3, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),

        ('2025-02-01', 'In Progress', 'Company A', 'Safety', 'Team Alpha', 86,
        0, 0, 5, 3, 4, 2, 4, 3, 2, 1, 0, 0, 3, 1, 1, 2, 0, 3, 4, 0),

        ('2025-02-04', 'Completed', 'Company C', 'Quality', 'Team Beta', 89,
        4, 5, 3, 4, 4, 0, 1, 3, 2, 3, 5, 5, 5, 1, 1, 3, 0, 0, 0, 0),

        ('2025-02-07', 'In Progress', 'Company B', 'Environment', 'Team Gamma', 80,
        5, 2, 3, 3, 5, 1, 1, 0, 2, 1, 4, 0, 0, 0, 2, 2, 3, 3, 1, 1),

        ('2025-02-10', 'Completed', 'Company A', 'Health', 'Team Alpha', 92,
        5, 4, 3, 2, 3, 0, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 3),

        ('2025-02-13', 'In Progress', 'Company C', 'Safety', 'Team Beta', 75,
        3, 4, 2, 1, 3, 0, 2, 3, 2, 0, 3, 2, 0, 1, 1, 3, 2, 0, 0, 1),

        ('2025-02-16', 'Completed', 'Company B', 'Quality', 'Team Gamma', 87,
        4, 5, 2, 3, 2, 0, 3, 2, 3, 0, 4, 1, 0, 0, 0, 3, 1, 2, 0, 0),

        ('2025-02-19', 'In Progress', 'Company A', 'Environment', 'Team Alpha', 78,
        3, 4, 2, 1, 5, 1, 0, 3, 2, 0, 0, 4, 1, 0, 1, 3, 3, 2, 2, 1),

        ('2025-02-22', 'Completed', 'Company C', 'Health', 'Team Beta', 95,
        5, 5, 4, 3, 4, 0, 0, 0, 0, 0, 3, 5, 5, 0, 1, 3, 2, 0, 2, 0),

        ('2025-02-25', 'In Progress', 'Company B', 'Safety', 'Team Gamma', 84,
        3, 4, 2, 2, 3, 0, 0, 0, 1, 1, 4, 0, 0, 2, 1, 0, 0, 1, 3, 2)
]
    cursor.executemany('''
        INSERT INTO hseq 
        (date, status, organisation, category, responsible_team, value, 
        health_safety_index, emergency_preparedness, first_aid, absenteeism, 
        employee_wellness, accident_cases, safety_training, equipment_usage, 
        safety_audits, risk_management, defect_rate, compliance, customer_feedback, 
        inspection_frequency, process_efficiency, energy_efficiency, waste_management, 
        emissions_monitoring, water_usage, regulation_compliance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', hseq_data)

    # Add demo 5S records with all subcategories
    five_s_data = [
        ('2025-01-10', 'Completed', 'Sort', 'Team Gamma', 85, 5, 4, 3, 2, 1),
        ('2025-01-12', 'In Progress', 'Shine', 'Team Alpha', 75, 4, 3, 5, 2, 1),
        ('2025-01-15', 'Completed', 'Straighten', 'Team Beta', 90, 4, 5, 4, 3, 2),
        ('2025-01-20', 'Completed', 'Standardize', 'Team Gamma', 80, 5, 4, 3, 4, 3),
        ('2025-01-22', 'In Progress', 'Sustain', 'Team Alpha', 70, 3, 4, 3, 5, 2),
        ('2025-01-25', 'Completed', 'Sort', 'Team Beta', 88, 4, 5, 3, 2, 1),
        ('2025-01-28', 'In Progress', 'Shine', 'Team Gamma', 79, 3, 3, 4, 2, 1),
        ('2025-02-02', 'Completed', 'Straighten', 'Team Alpha', 92, 5, 5, 4, 3, 2),
        ('2025-02-04', 'In Progress', 'Standardize', 'Team Beta', 80, 4, 3, 5, 3, 2),
        ('2025-02-07', 'Completed', 'Sustain', 'Team Gamma', 77, 4, 4, 3, 2, 3),
        ('2025-02-10', 'In Progress', 'Sort', 'Team Alpha', 85, 5, 4, 2, 3, 1),
        ('2025-02-14', 'Completed', 'Shine', 'Team Beta', 90, 5, 4, 3, 4, 2),
        ('2025-02-16', 'In Progress', 'Straighten', 'Team Gamma', 78, 4, 5, 2, 3, 2),
        ('2025-02-18', 'Completed', 'Standardize', 'Team Alpha', 85, 4, 3, 4, 5, 3),
        ('2025-02-20', 'In Progress', 'Sustain', 'Team Beta', 72, 3, 4, 5, 2, 2),
        ('2025-02-22', 'Completed', 'Sort', 'Team Gamma', 90, 5, 4, 3, 2, 1),
        ('2025-02-24', 'Completed', 'Shine', 'Team Alpha', 80, 3, 3, 4, 2, 3),
        ('2025-02-26', 'In Progress', 'Straighten', 'Team Beta', 75, 4, 5, 3, 2, 1),
        ('2025-03-01', 'Completed', 'Standardize', 'Team Gamma', 83, 5, 4, 3, 3, 2),
        ('2025-03-03', 'In Progress', 'Sustain', 'Team Alpha', 80, 4, 4, 3, 2, 3)
    ]
    cursor.executemany('''
        INSERT INTO five_s
        (date, status, category, responsible_team, value, sort, straighten, shine, standardize, sustain)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', five_s_data)

    # Add demo persons linked to teams
    persons_data = [
        ('Alice Johnson', 'alice.johnson@example.com', 1),
        ('Bob Smith', 'bob.smith@example.com', 1),
        ('Charlie Brown', 'charlie.brown@example.com', 2),
        ('David White', 'david.white@example.com', 2),
        ('Eve Black', 'eve.black@example.com', 3),
        ('Frank Green', 'frank.green@example.com', 3)
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO persons (name, email, team_id)
        VALUES (?, ?, ?)
    ''', persons_data)

    conn.commit()
    conn.close()

# Call these functions when the app starts
init_db()
add_demo_data()

print("All necessary tables and demo data have been set up.")

@app.route('/add_five_s', methods=['GET', 'POST'])
def add_five_s():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    five_s_subcategories = {
        'Sort': ['unnecessary_items_removed', 'red_tagged_items', 'repaired_items_kept', 'housekeeping_done', 'facility_inspection'],
        'Straighten': ['everything_in_place', 'labeling_done', 'tool_outlines', 'aisle_markings', 'pallet_zones'],
        'Shine': ['cleaning_done', 'root_cause_analysis', 'equipment_maintenance', 'zone_division'],
        'Standardize': ['visual_controls', 'set_standards', 'inspection_methods'],
        'Sustain': ['commitment_to_steps', 'evaluations_done']
    }

    cursor.execute('SELECT name FROM teams')
    teams = [row[0] for row in cursor.fetchall()]
    conn.close()

    error = None  # Initialize error variable
    success = False

    if request.method == 'POST':
        category = request.form.get('category')
        responsible_team = request.form.get('responsible_team')
        install_date = request.form.get('install_date')
        status = request.form.get('status')

        if category not in five_s_subcategories:
            error = "Invalid category selected."
            return render_template('add_five_s.html', categories=five_s_subcategories, teams=teams, error=error)

        selected_fields = five_s_subcategories[category]
        values = {key: int(request.form.get(key, 0)) for key in selected_fields}
        total_value = sum(values.values())

        # Columns for the five_s table
        columns = ['category', 'date', 'status', 'responsible_team', 'value'] + selected_fields
        placeholders = ", ".join(['?'] * len(columns))
        columns_str = ", ".join(columns)

        # Prepare the SQL query with correct number of placeholders
        sql = f'''
            INSERT INTO five_s ({columns_str})
            VALUES ({placeholders})
        '''
        
        data_values = [category, install_date, status, responsible_team, total_value] + list(values.values())

        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute(sql, data_values)
            conn.commit()
            success = True
            error = None  # Clear the error if the insertion was successful
        except sqlite3.Error as e:
            error = f"Database error: {str(e)}"
            success = False
        finally:
            conn.close()

        return render_template('add_five_s.html', categories=five_s_subcategories, teams=teams, success=success, error=error)

    return render_template('add_five_s.html', categories=five_s_subcategories, teams=teams)

@app.route('/generate_report')
def generate_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Oikea sarakenimi käytössä (date eikä install_date)
    cursor.execute('SELECT * FROM hseq WHERE date BETWEEN ? AND ? ORDER BY date DESC', (start_date, end_date))
    hseq_reports = cursor.fetchall()

    cursor.execute('SELECT * FROM five_s WHERE date BETWEEN ? AND ? ORDER BY date DESC', (start_date, end_date))
    five_s_reports = cursor.fetchall()

    conn.close()

    # Raportin data
    data = {
        "title": "HSEQ and 5S Report",
        "start_date": start_date,
        "end_date": end_date,
        "hseq_reports": hseq_reports,
        "five_s_reports": five_s_reports
    }

    # HTML-template raportille
    html_content = render_template('report_template.html', data=data)

    # Muunnetaan HTML PDF:ksi
    pdf = HTML(string=html_content).write_pdf()

    # Lähetä PDF käyttäjälle
    response = send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"Report_{start_date}_to_{end_date}.pdf"
    )

    return response

@app.route('/')
def dashboard():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch latest HSEQ and 5S reports
    cursor.execute('SELECT date, status, organisation, category, responsible_team, value FROM hseq ORDER BY id DESC LIMIT 5')
    hseq_reports = cursor.fetchall()

    cursor.execute('SELECT date, status, category, responsible_team, value FROM five_s ORDER BY id DESC LIMIT 5')
    five_s_reports = cursor.fetchall()

    # HSEQ breakdown by status
    cursor.execute('SELECT status, COUNT(*) FROM hseq GROUP BY status')
    hseq_chart_data = [{"label": row[0], "value": row[1]} for row in cursor.fetchall()]
    hseq_chart_labels = [item["label"] for item in hseq_chart_data]
    hseq_chart_values = [item["value"] for item in hseq_chart_data]

    # 5S breakdown by category
    cursor.execute('SELECT category, COUNT(*) FROM five_s GROUP BY category')
    five_s_chart_data = [{"label": row[0], "value": row[1]} for row in cursor.fetchall()]
    five_s_chart_labels = [item["label"] for item in five_s_chart_data]
    five_s_chart_values = [item["value"] for item in five_s_chart_data]

    # HSEQ subcategory averages
    cursor.execute('''
        SELECT AVG(health_safety_index), AVG(emergency_preparedness), AVG(first_aid), AVG(absenteeism),
            AVG(employee_wellness), AVG(accident_cases), AVG(safety_training), AVG(equipment_usage),
            AVG(safety_audits), AVG(risk_management), AVG(defect_rate), AVG(compliance), AVG(customer_feedback),
            AVG(inspection_frequency), AVG(process_efficiency), AVG(energy_efficiency), AVG(waste_management),
            AVG(emissions_monitoring), AVG(water_usage), AVG(regulation_compliance)
        FROM hseq
    ''')
    hseq_subcategory_values = cursor.fetchone()

    print("HSEQ Subcategory Values:", hseq_subcategory_values)  # Debugging print

    # 5S subcategory averages
    cursor.execute('''
        SELECT AVG(sort), AVG(straighten), AVG(shine), AVG(standardize), AVG(sustain),
            AVG(unnecessary_items_removed), AVG(red_tagged_items), AVG(repaired_items_kept),
            AVG(housekeeping_done), AVG(facility_inspection), AVG(everything_in_place), AVG(labeling_done),
            AVG(tool_outlines), AVG(aisle_markings), AVG(pallet_zones), AVG(cleaning_done),
            AVG(root_cause_analysis), AVG(equipment_maintenance), AVG(zone_division), AVG(visual_controls),
            AVG(set_standards), AVG(inspection_methods), AVG(commitment_to_steps), AVG(evaluations_done)
        FROM five_s
    ''')
    five_s_subcategory_values = cursor.fetchone()

    print("5S Subcategory Values:", five_s_subcategory_values)  # Debugging print

    # HSEQ Category averages (fallback if no data)
    cursor.execute('SELECT AVG(value) FROM hseq WHERE category="Health"')
    hseq_health_avg = cursor.fetchone()[0] or 0

    cursor.execute('SELECT AVG(value) FROM hseq WHERE category="Safety"')
    hseq_safety_avg = cursor.fetchone()[0] or 0

    cursor.execute('SELECT AVG(value) FROM hseq WHERE category="Quality"')
    hseq_quality_avg = cursor.fetchone()[0] or 0

    cursor.execute('SELECT AVG(value) FROM hseq WHERE category="Environment"')
    hseq_environment_avg = cursor.fetchone()[0] or 0

    hseq_category_values = [hseq_health_avg, hseq_safety_avg, hseq_quality_avg, hseq_environment_avg]

    # 5S Category averages (fallback if no data)
    cursor.execute('SELECT AVG(value) FROM five_s WHERE category="Sort"')
    five_s_sort_avg = cursor.fetchone()[0] or 0

    cursor.execute('SELECT AVG(value) FROM five_s WHERE category="Straighten"')
    five_s_straighten_avg = cursor.fetchone()[0] or 0

    cursor.execute('SELECT AVG(value) FROM five_s WHERE category="Shine"')
    five_s_shine_avg = cursor.fetchone()[0] or 0

    cursor.execute('SELECT AVG(value) FROM five_s WHERE category="Standardize"')
    five_s_standardize_avg = cursor.fetchone()[0] or 0

    cursor.execute('SELECT AVG(value) FROM five_s WHERE category="Sustain"')
    five_s_sustain_avg = cursor.fetchone()[0] or 0

    five_s_category_values = [five_s_sort_avg, five_s_straighten_avg, five_s_shine_avg, five_s_standardize_avg, five_s_sustain_avg]

    # Fetch HSEQ monthly averages
    cursor.execute('SELECT strftime("%Y-%m", date) AS month, AVG(value) FROM hseq GROUP BY month ORDER BY month DESC LIMIT 12')
    hseq_monthly_data = cursor.fetchall()
    hseq_monthly_labels = [row[0] for row in hseq_monthly_data]
    hseq_monthly_values = [round(row[1], 2) for row in hseq_monthly_data]

    # Fetch 5S monthly averages
    cursor.execute('SELECT strftime("%Y-%m", date) AS month, AVG(value) FROM five_s GROUP BY month ORDER BY month DESC LIMIT 12')
    five_s_monthly_data = cursor.fetchall()
    five_s_monthly_labels = [row[0] for row in five_s_monthly_data]
    five_s_monthly_values = [round(row[1], 2) for row in five_s_monthly_data]

    conn.close()

    # Handle undefined or empty data and provide fallback data
    hseq_category_values = hseq_category_values or [0, 0, 0, 0]
    five_s_category_values = five_s_category_values or [0, 0, 0, 0, 0]
    hseq_subcategory_values = hseq_subcategory_values or [0] * 20
    five_s_subcategory_values = five_s_subcategory_values or [0] * 24

    return render_template(
        'dashboard.html',
        hseq_reports=hseq_reports,
        five_s_reports=five_s_reports,
        hseq_chart_labels=hseq_chart_labels if hseq_chart_labels else [],
        hseq_chart_values=hseq_chart_values if hseq_chart_values else [],
        five_s_chart_labels=five_s_chart_labels if five_s_chart_labels else [],
        five_s_chart_values=five_s_chart_values if five_s_chart_values else [],
        hseq_monthly_labels=hseq_monthly_labels if hseq_monthly_labels else [],
        hseq_monthly_values=hseq_monthly_values if hseq_monthly_values else [],
        five_s_monthly_labels=five_s_monthly_labels if five_s_monthly_labels else [],
        five_s_monthly_values=five_s_monthly_values if five_s_monthly_values else [],
        hseq_category_values=hseq_category_values,
        five_s_category_values=five_s_category_values,
        hseq_subcategory_values=hseq_subcategory_values,
        five_s_subcategory_values=five_s_subcategory_values,
        hseq_subcategory_labels=[
            'Health Safety Index', 'Emergency Preparedness', 'First Aid', 'Absenteeism', 'Employee Wellness',
            'Accident Cases', 'Safety Training', 'Equipment Usage', 'Safety Audits', 'Risk Management',
            'Defect Rate', 'Compliance', 'Customer Feedback', 'Inspection Frequency', 'Process Efficiency',
            'Energy Efficiency', 'Waste Management', 'Emissions Monitoring', 'Water Usage', 'Regulation Compliance'
        ],
        five_s_subcategory_labels=[
            'Sort', 'Straighten', 'Shine', 'Standardize', 'Sustain', 'Unnecessary Items Removed', 'Red Tagged Items',
            'Repaired Items Kept', 'Housekeeping Done', 'Facility Inspection', 'Everything in Place', 'Labeling Done',
            'Tool Outlines', 'Aisle Markings', 'Pallet Zones', 'Cleaning Done', 'Root Cause Analysis',
            'Equipment Maintenance', 'Zone Division', 'Visual Controls', 'Set Standards', 'Inspection Methods',
            'Commitment to Steps', 'Evaluations Done'
        ]
    )

@app.route('/hseq')
def hseq():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM hseq')
    hseq_reports = cursor.fetchall()
    conn.close()
    return render_template('hseq.html', hseq_reports=hseq_reports)

@app.route('/add_hseq', methods=['GET', 'POST'])
def add_hseq():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    hseq_categories = {
        'Health': [
            'health_safety_index', 
            'emergency_preparedness', 
            'first_aid', 
            'absenteeism', 
            'employee_wellness'
        ],
        'Safety': [
            'accident_cases', 
            'safety_training', 
            'equipment_usage', 
            'safety_audits', 
            'risk_management'
        ],
        'Quality': [
            'defect_rate', 
            'compliance', 
            'customer_feedback', 
            'inspection_frequency', 
            'process_efficiency'
        ],
        'Environment': [
            'energy_efficiency', 
            'waste_management', 
            'emissions_monitoring', 
            'water_usage', 
            'regulation_compliance'
        ]
    }

    cursor.execute('SELECT name FROM teams')
    teams = [row[0] for row in cursor.fetchall()]
    success = False
    error = None

    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        responsible_team = request.form.get('responsible_team', '').strip()
        install_date = request.form.get('install_date', '').strip()
        status = request.form.get('status', '').strip()  # Get status from form

        if not category or not responsible_team or not install_date or not status:
            error = "Please fill all required fields."
            return render_template('add_hseq.html', categories=hseq_categories, teams=teams, error=error)

        selected_fields = hseq_categories[category]
        values = {key: int(request.form.get(key, 0)) for key in selected_fields}
        total_value = sum(values.values())

        columns = ", ".join(['category', 'date', 'responsible_team', 'status', 'value'] + selected_fields)
        placeholders = ", ".join(['?'] * (len(selected_fields) + 5))  # 5 includes category, date, team, status, value

        sql = f'''
            INSERT INTO hseq ({columns})
            VALUES ({placeholders})
        '''
        
        data_values = [category, install_date, responsible_team, status, total_value] + list(values.values())

        try:
            cursor.execute(sql, data_values)
            conn.commit()
            success = True
        except sqlite3.IntegrityError as e:
            error = f"Database error: {e}"
        finally:
            conn.close()

    return render_template('add_hseq.html', categories=hseq_categories, teams=teams, success=success, error=error)

@app.route('/teams', methods=['GET', 'POST'])
def manage_teams():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Handle adding a new team
    if request.method == 'POST' and 'team_name' in request.form:
        team_name = request.form['team_name']
        try:
            cursor.execute('INSERT INTO teams (name) VALUES (?)', (team_name,))
            conn.commit()
        except sqlite3.IntegrityError:
            # Handle duplicate team names
            return render_template(
                'teams.html',
                teams=cursor.execute('SELECT * FROM teams').fetchall(),
                persons=cursor.execute('SELECT * FROM persons').fetchall(),
                error=f"Team '{team_name}' already exists."
            )

    # Handle adding a person to a team
    if request.method == 'POST' and 'person_name' in request.form:
        person_name = request.form['person_name']
        email = request.form['email']
        team_id = request.form['team_id']
        cursor.execute('INSERT INTO persons (name, email, team_id) VALUES (?, ?, ?)', 
                       (person_name, email, team_id))
        conn.commit()

    # Fetch all teams and persons for display
    cursor.execute('SELECT * FROM teams')
    teams = cursor.fetchall()

    cursor.execute('SELECT persons.id, persons.name, persons.email, teams.name AS team_name FROM persons JOIN teams ON persons.team_id = teams.id')
    persons = cursor.fetchall()

    conn.close()

    return render_template('teams.html', teams=teams, persons=persons)

@app.route('/delete_team/<int:team_id>', methods=['POST'])
def delete_team(team_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM teams WHERE id = ?', (team_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_teams'))

@app.route('/add_person', methods=['GET', 'POST'])
def add_person():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch all teams for the dropdown
    cursor.execute('SELECT * FROM teams')
    teams = cursor.fetchall()

    if request.method == 'POST':
        person_name = request.form['person_name']
        email = request.form['email']
        team_id = request.form['team_id']

        cursor.execute('INSERT INTO persons (name, email, team_id) VALUES (?, ?, ?)', 
                       (person_name, email, team_id))
        conn.commit()
        conn.close()
        return redirect(url_for('add_person'))

    conn.close()
    return render_template('add_person.html', teams=teams)

@app.route('/delete_person/<int:person_id>', methods=['POST'])
def delete_person(person_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM persons WHERE id = ?', (person_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('add_person'))

@app.route('/5s')
def five_s():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM five_s')
    five_s_reports = cursor.fetchall()
    conn.close()
    return render_template('five_s.html', five_s_reports=five_s_reports)

@app.route('/generate_pdf')
def generate_pdf():
    import datetime  # Ensure datetime is available

    # Example data to pass to the template
    data = {
        "title": "HSEQ and 5S Report",
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "records": [
            {"name": "Safety Check", "status": "Completed", "value": 85},
            {"name": "Environmental Audit", "status": "In Progress", "value": 72},
            {"name": "Warehouse Cleaning", "status": "Completed", "value": 90},
        ]
    }

    # Render HTML content using a template
    html_content = render_template('report_template.html', data=data)

    # Generate PDF using WeasyPrint
    pdf = HTML(string=html_content).write_pdf()

    # Return PDF as a downloadable response
    response = Response(pdf, content_type='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=report.pdf'
    return response

@app.route('/edit_five_s/<int:five_s_id>', methods=['GET', 'POST'])
def edit_five_s(five_s_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch the existing 5S data for the selected ID
    cursor.execute('SELECT * FROM five_s WHERE id = ?', (five_s_id,))
    five_s_entry = cursor.fetchone()

    if not five_s_entry:
        return "5S entry not found", 404

    if request.method == 'POST':
        # Get updated data from the form
        date = request.form['date']
        status = request.form['status']
        category = request.form['category']
        responsible_team = request.form['responsible_team']
        value = request.form['value']
        sort = request.form['sort']
        straighten = request.form['straighten']
        shine = request.form['shine']
        standardize = request.form['standardize']
        sustain = request.form['sustain']

        # Update the record in the database
        cursor.execute('''
            UPDATE five_s 
            SET date = ?, status = ?, category = ?, responsible_team = ?, value = ?, 
                sort = ?, straighten = ?, shine = ?, standardize = ?, sustain = ?
            WHERE id = ?
        ''', (date, status, category, responsible_team, value, sort, straighten, shine, 
              standardize, sustain, five_s_id))

        conn.commit()
        conn.close()

        return redirect(url_for('five_s'))  # Redirect back to the list view

    conn.close()

    return render_template('edit_five_s.html', five_s_entry=five_s_entry)

@app.route('/edit_hseq/<int:hseq_id>', methods=['GET', 'POST'])
def edit_hseq(hseq_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch the existing HSQE data for the selected ID
    cursor.execute('SELECT * FROM hseq WHERE id = ?', (hseq_id,))
    hseq_entry = cursor.fetchone()

    if request.method == 'POST':
        status = request.form['status']
        category = request.form['category']
        responsible_team = request.form['responsible_team']
        value = request.form['value']
        health_safety_index = request.form['health_safety_index']
        # Collect other values similarly...

        # Update the HSQE entry
        cursor.execute('''
            UPDATE hseq
            SET date = ?, status = ?, category = ?, responsible_team = ?, value = ?, 
                health_safety_index = ?, emergency_preparedness = ?, first_aid = ?, absenteeism = ?, 
                employee_wellness = ?, accident_cases = ?, safety_training = ?, equipment_usage = ?, 
                safety_audits = ?, risk_management = ?, defect_rate = ?, compliance = ?, customer_feedback = ?, 
                inspection_frequency = ?, process_efficiency = ?, energy_efficiency = ?, waste_management = ?, 
                emissions_monitoring = ?, water_usage = ?, regulation_compliance = ?
            WHERE id = ?
        ''', (request.form['date'], status, category, responsible_team, value, 
              health_safety_index, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, hseq_id))

        conn.commit()
        conn.close()

        return redirect(url_for('hseq'))  # Redirect back to the list view

    conn.close()

    return render_template('edit_hseq.html', hseq_entry=hseq_entry)

@app.route('/add_incident', methods=['GET', 'POST'])
def add_incident():
    if request.method == 'POST':
        try:
            date = request.form['date']  # Keep date as a string
            incident_type = request.form['type']
            department = request.form['department']
            injured_job_title = request.form.get('injured_job_title', None)
            injured_age = request.form.get('injured_age', None)
            injured_gender = request.form.get('injured_gender', None)
            body_part_affected = request.form.get('body_part_affected', None)
            time_of_day = request.form.get('time_of_day', None)
            time_into_shift = request.form.get('time_into_shift', None)
            machine_equipment = request.form.get('machine_equipment', None)
            operation = request.form.get('operation', None)
            causation = request.form.get('causation', None)
            location = request.form['location']
            financial_impact = float(request.form.get('financial_impact', 0))
            reportable = int(request.form.get('reportable', 0))
            description = request.form.get('description', None)

            # Insert data into the database
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO incidentreport (
                    date, type, department, injured_job_title, injured_age, 
                    injured_gender, body_part_affected, time_of_day, time_into_shift, 
                    machine_equipment, operation, causation, location, financial_impact, 
                    reportable, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date, incident_type, department, injured_job_title, injured_age, 
                  injured_gender, body_part_affected, time_of_day, time_into_shift, 
                  machine_equipment, operation, causation, location, financial_impact, 
                  reportable, description))
            conn.commit()
            conn.close()

            flash('Incident added successfully!', 'success')
            return redirect(url_for('incident_dashboard'))

        except ValueError as e:
            logging.error(f"An error occurred: {e}")
            flash(f"Invalid data provided: {e}", 'danger')
            return redirect(url_for('add_incident'))
    return render_template('add_incident.html')

@app.route('/view_incident/<int:id>')
def view_incident(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM incidentreport WHERE id = ?', (id,))
    incident = cursor.fetchone()
    conn.close()

    if incident is None:
        flash("Incident not found.", "danger")
        return redirect(url_for('incident_dashboard'))

    # Convert the tuple to a dictionary to be used in the template
    incident_dict = {
        "date": incident[1],
        "type": incident[2],
        "department": incident[3],
        "injured_job_title": incident[4],
        "injured_age": incident[5],
        "injured_gender": incident[6],
        "body_part_affected": incident[7],
        "time_of_day": incident[8],
        "time_into_shift": incident[9],
        "machine_equipment": incident[10],
        "operation": incident[11],
        "causation": incident[12],
        "location": incident[13],
        "financial_impact": incident[14],
        "description": incident[16]
    }

    return render_template('view_incident.html', incident=incident_dict)

@app.route('/delete_incident/<int:incident_id>', methods=['POST'])
def delete_incident(incident_id):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM incidentreport WHERE id = ?', (incident_id,))
        conn.commit()
        conn.close()
        flash('Incident deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting incident: {e}', 'danger')
    return redirect(url_for('dashboard_incident'))

@app.route('/dashboard_incident')
def dashboard_incident():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Incident Types Count
    cursor.execute('SELECT type, COUNT(*) FROM incidentreport GROUP BY type')
    incident_data = cursor.fetchall()
    incident_type_labels = [row[0] for row in incident_data]
    incident_type_counts = [row[1] for row in incident_data]

    # Financial Impact Data
    cursor.execute('SELECT date, SUM(financial_impact) FROM incidentreport GROUP BY date')
    financial_data = cursor.fetchall()
    incident_dates = [row[0] for row in financial_data]
    financial_impacts = [row[1] for row in financial_data]

    conn.close()

    return render_template('incidentdashboard.html',
                        incident_type_labels=incident_type_labels,
                        incident_type_counts=incident_type_counts,
                        incident_dates=incident_dates,
                        financial_impacts=financial_impacts)

@app.route('/delete_hseq/<int:hseq_id>', methods=['GET', 'POST'])
def delete_hseq(hseq_id):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM hseq WHERE id = ?', (hseq_id,))
        conn.commit()
        conn.close()
        flash('HSEQ entry deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting entry: {e}', 'danger')
    return redirect(url_for('hseq'))

@app.route('/delete_five_s/<int:five_s_id>', methods=['GET', 'POST'])
def delete_five_s(five_s_id):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM five_s WHERE id = ?', (five_s_id,))
        conn.commit()
        conn.close()
        flash('5S entry deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting 5S entry: {e}', 'danger')
    return redirect(url_for('five_s'))

@app.route('/incident-dashboard')
def incident_dashboard():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch incident report data
    cursor.execute('SELECT date, type, department, financial_impact, location, id FROM incidentreport ORDER BY date DESC')
    incident_reports = cursor.fetchall()

    # Fetch incident type counts for pie chart
    cursor.execute('SELECT type, COUNT(*) FROM incidentreport GROUP BY type')
    incident_data = cursor.fetchall()
    incident_type_labels = [row[0] for row in incident_data] if incident_data else []
    incident_type_counts = [row[1] for row in incident_data] if incident_data else []

    # Fetch financial impact data for bar chart
    cursor.execute('SELECT date, SUM(financial_impact) FROM incidentreport GROUP BY date ORDER BY date')
    financial_data = cursor.fetchall()
    incident_dates = [row[0] for row in financial_data] if financial_data else []
    financial_impacts = [row[1] for row in financial_data] if financial_data else []

    conn.close()

    return render_template(
        'incidentdashboard.html',
        incident_reports=incident_reports,
        incident_type_labels=incident_type_labels or [],
        incident_type_counts=incident_type_counts or [],
        incident_dates=incident_dates or [],
        financial_impacts=financial_impacts or []
    )

import logging

logging.basicConfig(level=logging.DEBUG)

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"An error occurred: {str(e)}")
    return "An unexpected error occurred. Check the logs for more details.", 500

hseq_category_values = [0, 0, 0, 0]  # Add a fallback if data is missing
five_s_category_values = [0, 0, 0, 0, 0]  # Add fallback data for 5S
hseq_subcategory_values = [0] * 20  # Fallback for HSEQ subcategory values
five_s_subcategory_values = [0] * 24  # Fallback for 5S subcategory values

# Now print the values
print("HSEQ Category Values:", hseq_category_values)
print("5S Category Values:", five_s_category_values)
print("HSEQ Subcategory Values:", hseq_subcategory_values)
print("5S Subcategory Values:", five_s_subcategory_values)

if __name__ == '__main__':
    init_db()  # Ensure database schema is initialized properly
    add_demo_data()  # Add demo data
    app.run(debug=True)