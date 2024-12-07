from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = pymysql.connect(host='localhost',
                           user='root',
                           password='Amar@3142',
                           database='Grampanchayat',
                           cursorclass=pymysql.cursors.DictCursor)
    return conn

@app.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute('SELECT COUNT(*) as total_population FROM members')
        members_population_data = cursor.fetchone()
        members_population = members_population_data['total_population']

        cursor.execute('SELECT COUNT(*) as total_births FROM births')
        births_population_data = cursor.fetchone()
        births_population = births_population_data['total_births']

        total_population = members_population + births_population

        cursor.execute("SELECT COUNT(*) as male_population FROM members WHERE gender = 'male'")
        male_members_population_data = cursor.fetchone()
        male_members_population = male_members_population_data['male_population']

        cursor.execute("SELECT COUNT(*) as male_births FROM births WHERE gender = 'male'")
        male_births_population_data = cursor.fetchone()
        male_births_population = male_births_population_data['male_births']
        male_population = male_members_population + male_births_population

        cursor.execute("SELECT COUNT(*) as female_population FROM members WHERE gender = 'female'")
        female_members_population_data = cursor.fetchone()
        female_members_population = female_members_population_data['female_population']

        cursor.execute("SELECT COUNT(*) as female_births FROM births WHERE gender = 'female'")
        female_births_population_data = cursor.fetchone()
        female_births_population = female_births_population_data['female_births']
        female_population = female_members_population + female_births_population

        cursor.execute("SELECT COUNT(*) as others_population FROM members WHERE gender NOT IN ('male', 'female')")
        others_members_population_data = cursor.fetchone()
        others_members_population = others_members_population_data['others_population']

        cursor.execute("SELECT COUNT(*) as others_births FROM births WHERE gender NOT IN ('male', 'female')")
        others_births_population_data = cursor.fetchone()
        others_births_population = others_births_population_data['others_births']
        others_population = others_members_population + others_births_population

        cursor.execute('SELECT * FROM village WHERE id = 1')
        village_data = cursor.fetchone()

        cursor.execute('SELECT name, dob, gender FROM births')
        births = cursor.fetchall()

        if not village_data:
            village_data = {
                'sarpanch': 'N/A',
                'gramsevak': 'N/A'
            }
    except Exception as e:
        print(f"Error fetching data: {e}")
        total_population = 'Error'
        male_population = 'Error'
        female_population = 'Error'
        others_population = 'Error'
        births = []
        village_data = {
            'sarpanch': 'Error',
            'gramsevak': 'Error'
        }
    finally:
        cursor.close()
        conn.close()

    village_data.update({
        'population': total_population,
        'male_population': male_population,
        'female_population': female_population,
        'others_population': others_population,
        'births': births
    })

    return render_template('dashboard.html', village=village_data)

@app.route('/add_birth_page', methods=['GET', 'POST'])
def add_birth_page():
    if request.method == 'POST':
        baby_name = request.form['baby_name']
        baby_gender = request.form['baby_gender']
        dob = request.form['dob']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO births (name, gender, dob) VALUES (%s, %s, %s)', (baby_name, baby_gender, dob))
            conn.commit()
            flash('Birth record added successfully!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('manage'))

    return render_template('add_birth.html')

@app.route('/remove_birth_page', methods=['GET'])
def remove_birth_page():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute('SELECT * FROM births')
        births = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching birth records: {e}")
        births = []
    finally:
        cursor.close()
        conn.close()

    return render_template('remove_person.html', births=births)

@app.route('/remove_birth/<int:birth_id>', methods=['POST'])
def remove_birth(birth_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM births WHERE id = %s', (birth_id,))
        conn.commit()
        flash('Birth record removed successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('remove_birth_page'))

@app.route('/edit_birth_page/<int:birth_id>', methods=['GET', 'POST'])
def edit_birth_page(birth_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        updated_name = request.form['baby_name']
        updated_gender = request.form['baby_gender']
        updated_dob = request.form['dob']

        try:
            cursor.execute('UPDATE births SET name = %s, gender = %s, dob = %s WHERE id = %s',
                           (updated_name, updated_gender, updated_dob, birth_id))
            conn.commit()
            flash('Birth record updated successfully!', 'success')
            return redirect(url_for('remove_birth_page'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    else:
        try:
            cursor.execute('SELECT * FROM births WHERE id = %s', (birth_id,))
            birth_record = cursor.fetchone()
        except Exception as e:
            flash(f'Error fetching birth record: {e}', 'danger')
            birth_record = None

    cursor.close()
    conn.close()

    return render_template('edit_birth.html', birth=birth_record)

@app.route('/view_population_data', methods=['GET'])
def view_population_data():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute('SELECT * FROM births')
        births = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching population data: {e}")
        births = []
    finally:
        cursor.close()
        conn.close()

    return render_template('population_data.html', births=births)

@app.route('/update_role_page', methods=['GET', 'POST'])
def update_role_page():
    if request.method == 'POST':
        new_sarpanch = request.form['new_sarpanch']
        new_gramsevak = request.form['new_gramsevak']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE village SET sarpanch = %s, gramsevak = %s WHERE id = 1', (new_sarpanch, new_gramsevak))
            conn.commit()
            flash('Roles updated successfully!', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('manage'))

    return render_template('update_role.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hardcoded credentials
        if username == 'Abhi' and password == '1234':
            session['username'] = username
            return redirect(url_for('manage'))
        else:
            flash("Invalid credentials", 'danger')

    return render_template('login.html')

@app.route('/manage')
def manage():
    return render_template('manage.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
