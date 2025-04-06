from flask import Flask, render_template, request, redirect, url_for, flash, session
import webbrowser
import sqlite3
from contextlib import closing
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_compleja_y_segura_aqui'  # Cambia esto por una clave segura en producción

# 1. Configuración de la Base de Datos
def init_db():
    with closing(sqlite3.connect('database.db')) as db:
        db.execute('''
        CREATE TABLE IF NOT EXISTS fichas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER UNIQUE NOT NULL CHECK(typeof(numero) = 'integer')
        )
        ''')
        
        db.execute('''
        CREATE TABLE IF NOT EXISTS codigos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo INTEGER NOT NULL CHECK(typeof(codigo) = 'integer'),
            ficha_id INTEGER UNIQUE,
            FOREIGN KEY (ficha_id) REFERENCES fichas(id)
        )
        ''')
        db.commit()

def check_tables_exist():
    """Verifica que las tablas necesarias existan"""
    with closing(sqlite3.connect('database.db')) as db:
        tables = db.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('fichas', 'codigos')
        """).fetchall()
        return len(tables) == 2

init_db()

# 2. Funciones para cargar datos
def cargar_fichas_desde_archivo(file):
    try:
        filepath = os.path.join('uploads', 'temp_fichas.txt')
        file.save(filepath)
        
        fichas = []
        with closing(sqlite3.connect('database.db')) as db:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.isdigit():
                        numero = int(line)
                        fichas.append(numero)
                        db.execute('INSERT OR IGNORE INTO fichas (numero) VALUES (?)', (numero,))
            db.commit()
        return fichas
    except Exception as e:
        raise Exception(f"Error al cargar fichas: {str(e)}")

def cargar_codigos_desde_archivo(file):
    try:
        filepath = os.path.join('uploads', 'temp_codigos.txt')
        file.save(filepath)
        
        with closing(sqlite3.connect('database.db')) as db:
            total_fichas = db.execute('SELECT COUNT(*) FROM fichas').fetchone()[0]
            if total_fichas == 0:
                raise ValueError("No hay fichas cargadas. Cargue fichas primero.")
            
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.isdigit():
                        codigo = int(line)
                        ficha_sin_codigo = db.execute('''
                            SELECT f.id FROM fichas f
                            LEFT JOIN codigos c ON f.id = c.ficha_id
                            WHERE c.id IS NULL
                            ORDER BY f.id
                            LIMIT 1
                        ''').fetchone()
                        
                        if ficha_sin_codigo:
                            try:
                                db.execute('INSERT INTO codigos (codigo, ficha_id) VALUES (?, ?)',
                                          (codigo, ficha_sin_codigo[0]))
                            except sqlite3.IntegrityError:
                                continue
            db.commit()
    except Exception as e:
        raise Exception(f"Error al cargar códigos: {str(e)}")

def get_parejas_fichas_codigos():
    """Obtiene todas las fichas con sus códigos"""
    with closing(sqlite3.connect('database.db')) as db:
        return db.execute('''
            SELECT f.numero, c.codigo
            FROM fichas f
            LEFT JOIN codigos c ON f.id = c.ficha_id
            ORDER BY f.numero
        ''').fetchall()

def generar_url_para_ficha(numero_ficha):
    """Genera la URL para una ficha específica"""
    with closing(sqlite3.connect('database.db')) as db:
        codigo = db.execute('''
            SELECT c.codigo FROM codigos c
            JOIN fichas f ON c.ficha_id = f.id
            WHERE f.numero = ?
        ''', (numero_ficha,)).fetchone()
        
        url = f"https://zajuna.sena.edu.co/zajuna/course/management.php?search={numero_ficha}"
        if codigo:
            url += f"&cod={codigo[0]}"
            return url, True
        return url, False

def generar_y_abrir_url(numero_ficha):
    """Versión simplificada con validación estricta"""
    try:
        with closing(sqlite3.connect('database.db')) as db:
            # Consulta directa al código relacionado
            codigo = db.execute('''
                SELECT c.codigo FROM codigos c
                JOIN fichas f ON c.ficha_id = f.id
                WHERE f.numero = ?
            ''', (numero_ficha,)).fetchone()
            
            # Construcción exacta requerida
            url = f"https://zajuna.sena.edu.co/zajuna/course/management.php?categoryid=1&view=courses&search={numero_ficha}"
            
            if codigo and codigo[0]:  # Validación estricta
                url += f"&courseid={codigo[0]}"
            
            #print(f"URL GENERADA: {url}")  # Verificación obligatoria
            webbrowser.open(url)
            return True, None
            
    except Exception as e:
        return False, f'Error: {str(e)}'

# 3. Rutas de Administración
@app.route('/admin')
def admin():
    if not check_tables_exist():
        flash('La base de datos no está configurada correctamente', 'error')
        return redirect(url_for('home'))
    
    return render_template('admin.html', parejas=get_parejas_fichas_codigos())

@app.route('/admin/upload-fichas', methods=['POST'])
def admin_upload_fichas():
    if 'file' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('admin'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('admin'))
    
    try:
        if file and file.filename.endswith('.txt'):
            cargar_fichas_desde_archivo(file)
            flash('Fichas cargadas correctamente', 'success')
        else:
            flash('El archivo debe ser un .txt', 'error')
    except Exception as e:
        flash(f'Error al cargar fichas: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/upload-codigos', methods=['POST'])
def admin_upload_codigos():
    if 'file' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('admin'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('admin'))
    
    try:
        if file and file.filename.endswith('.txt'):
            cargar_codigos_desde_archivo(file)
            flash('Códigos cargados correctamente', 'success')
        else:
            flash('El archivo debe ser un .txt', 'error')
    except Exception as e:
        flash(f'Error al cargar códigos: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

# 4. Rutas Principales (Validación)
@app.route('/')
def home():
    # Obtener de la sesión con valores por defecto
    numbers = session.get('numbers', [])
    current_index = session.get('current_index', 0)
    file_loaded = session.get('file_loaded', False)
    
    current_ficha = numbers[current_index] if numbers else None
    lms_id = None  # Variable para almacenar el código real
    
    if current_ficha:
        # Obtener el código REAL de la base de datos
        with closing(sqlite3.connect('database.db')) as conn:
            resultado = conn.execute('''
                SELECT c.codigo FROM codigos c
                JOIN fichas f ON c.ficha_id = f.id
                WHERE f.numero = ?
            ''', (current_ficha,)).fetchone()
            
            if resultado:
                lms_id = resultado[0]  # Extraer el valor del código
    
    return render_template('index.html',
        current_ficha=current_ficha,  # Número de ficha (ej: 51179)
        lms_id=lms_id,               # Código LMS (ej: 42671) o None
        prev_number=numbers[current_index - 1] if numbers and current_index > 0 else None,
        next_number=numbers[current_index + 1] if numbers and current_index < len(numbers) - 1 else None,
        numbers=numbers,
        current_index=current_index,
        file_loaded=file_loaded
    )

@app.route('/procesar-fichas', methods=['POST'])
def procesar_fichas():
    fichas_texto = request.form.get('fichas', '')
    if not fichas_texto:
        flash('No se ingresaron fichas', 'error')
        return redirect(url_for('home'))
    
    try:
        numbers = []
        for line in fichas_texto.split('\n'):
            line = line.strip()
            if line.isdigit():
                numbers.append(int(line))
        
        if not numbers:
            flash('No se encontraron números válidos', 'error')
            return redirect(url_for('home'))
        
        # Guardar en sesión
        session['numbers'] = numbers
        session['current_index'] = 0
        session['file_loaded'] = True
        
        flash(f'Se cargaron {len(numbers)} fichas para validación', 'success')
        return redirect(url_for('home'))
    
    except Exception as e:
        flash(f'Error al procesar fichas: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/previous')
def previous():
    numbers = session.get('numbers', [])
    if not numbers:
        flash('No hay fichas cargadas para navegar', 'error')
        return redirect(url_for('home'))
    
    current_index = session.get('current_index', 0)
    
    if current_index > 0:
        session['current_index'] = current_index - 1
        current_number = numbers[session['current_index']]
        success, message = generar_y_abrir_url(current_number)
        if not success:
            flash(message, 'warning')
    else:
        flash('¡Primera ficha alcanzada!', 'info')
    
    return redirect(url_for('home'))

@app.route('/next')
def next():
    numbers = session.get('numbers', [])
    if not numbers:
        flash('No hay fichas cargadas para navegar', 'error')
        return redirect(url_for('home'))
    
    current_index = session.get('current_index', 0)
    
    if current_index < len(numbers) - 1:
        session['current_index'] = current_index + 1
        current_number = numbers[session['current_index']]
        success, message = generar_y_abrir_url(current_number)
        if not success:
            flash(message, 'warning')
    else:
        flash('¡Última ficha alcanzada!', 'info')
    
    return redirect(url_for('home'))

@app.route('/number/<int:number>')
def show_number(number):
    with closing(sqlite3.connect('database.db')) as db:
        ficha = db.execute('SELECT id FROM fichas WHERE numero = ?', (number,)).fetchone()
        
        if not ficha:
            flash(f'Ficha {number} no encontrada', 'error')
            return redirect(url_for('home'))
        
        codigo = db.execute('SELECT codigo FROM codigos WHERE ficha_id = ?', (ficha[0],)).fetchone()
        
        return render_template('ficha.html', 
            numero=number,
            codigo=codigo[0] if codigo else None
        )

@app.route('/reset')
def reset():
    """Ruta para limpiar la sesión (útil para desarrollo)"""
    session.clear()
    flash('Sesión reiniciada', 'info')
    return redirect(url_for('home'))

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)