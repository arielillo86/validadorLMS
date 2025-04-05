from flask import Flask, render_template, request, redirect, url_for, flash
import webbrowser
import sqlite3
from contextlib import closing
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Configuración inicial
numbers = []
current_index = 0

# 1. Configuración de la Base de Datos
def init_db():
    with closing(sqlite3.connect('database.db')) as db:
        # Tabla de fichas
        db.execute('''
        CREATE TABLE IF NOT EXISTS fichas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER UNIQUE NOT NULL CHECK(typeof(numero) = 'integer')
        )
        ''')
        
        # Tabla de códigos
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
    global numbers
    numbers = []
    try:
        filepath = os.path.join('uploads', 'temp_fichas.txt')
        file.save(filepath)
        
        with closing(sqlite3.connect('database.db')) as db:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.isdigit():
                        numero = int(line)
                        numbers.append(numero)
                        db.execute('INSERT OR IGNORE INTO fichas (numero) VALUES (?)', (numero,))
            db.commit()
        return numbers
    except Exception as e:
        raise Exception(f"Error al cargar fichas: {str(e)}")

def cargar_codigos_desde_archivo(file):
    try:
        filepath = os.path.join('uploads', 'temp_codigos.txt')
        file.save(filepath)
        
        with closing(sqlite3.connect('database.db')) as db:
            # Verificar si hay fichas disponibles
            total_fichas = db.execute('SELECT COUNT(*) FROM fichas').fetchone()[0]
            if total_fichas == 0:
                raise ValueError("No hay fichas cargadas. Cargue fichas primero.")
            
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.isdigit():
                        codigo = int(line)
                        # Asignar a la primera ficha sin código
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
                                continue  # Ignorar códigos duplicados
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

# 3. Rutas principales
@app.route('/')
def home():
    global current_index, numbers
    
    if not numbers:
        return render_template('index.html', 
            current_number=None,
            prev_number=None,
            next_number=None,
            numbers=[],
            file_loaded=False,
            parejas=[]
        )
    
    if not check_tables_exist():
        flash('La base de datos no está configurada correctamente', 'error')
        return redirect(url_for('home'))
    
    prev_number = numbers[current_index - 1] if current_index > 0 else None
    next_number = numbers[current_index + 1] if current_index < len(numbers) - 1 else None
    
    # Obtener código actual si existe
    current_code = None
    if numbers:
        with closing(sqlite3.connect('database.db')) as db:
            current_code = db.execute('''
                SELECT c.codigo FROM codigos c
                JOIN fichas f ON c.ficha_id = f.id
                WHERE f.numero = ?
            ''', (numbers[current_index],)).fetchone()
    
    return render_template('index.html',
        current_number=numbers[current_index],
        current_code=current_code[0] if current_code else None,
        prev_number=prev_number,
        next_number=next_number,
        numbers=numbers,
        file_loaded=True,
        parejas=get_parejas_fichas_codigos()
    )

@app.route('/upload-fichas', methods=['POST'])
def upload_fichas():
    if 'file' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('home'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('home'))
    
    try:
        if file and file.filename.endswith('.txt'):
            cargar_fichas_desde_archivo(file)
            flash('Fichas cargadas correctamente', 'success')
        else:
            flash('El archivo debe ser un .txt', 'error')
    except Exception as e:
        flash(f'Error al cargar fichas: {str(e)}', 'error')
    
    return redirect(url_for('home'))

@app.route('/upload-codigos', methods=['POST'])
def upload_codigos():
    if 'file' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('home'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('home'))
    
    try:
        if file and file.filename.endswith('.txt'):
            cargar_codigos_desde_archivo(file)
            flash('Códigos cargados correctamente', 'success')
        else:
            flash('El archivo debe ser un .txt', 'error')
    except Exception as e:
        flash(f'Error al cargar códigos: {str(e)}', 'error')
    
    return redirect(url_for('home'))

# Nueva ruta para procesar fichas en lista vertical
@app.route('/procesar-fichas', methods=['POST'])
def procesar_fichas():
    global numbers, current_index
    
    fichas_texto = request.form.get('fichas', '')
    if not fichas_texto:
        flash('No se ingresaron fichas', 'error')
        return redirect(url_for('home'))
    
    try:
        # Procesar fichas en lista vertical (una por línea)
        numbers = []
        for line in fichas_texto.split('\n'):
            line = line.strip()
            if line.isdigit():
                numbers.append(int(line))
        
        current_index = 0
        
        if not numbers:
            flash('No se encontraron números válidos', 'error')
            return redirect(url_for('home'))
        
        flash(f'Se cargaron {len(numbers)} fichas para validación', 'success')
        return redirect(url_for('home'))
    
    except Exception as e:
        flash(f'Error al procesar fichas: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/previous')
def previous():
    global current_index
    if not numbers:
        flash('No hay números en la lista', 'error')
        return redirect(url_for('home'))
    
    if current_index > 0:
        current_index -= 1
    else:
        flash('¡Primera ficha alcanzada!', 'info')
    
    # Generar URL con código si existe
    with closing(sqlite3.connect('database.db')) as db:
        resultado = db.execute('''
            SELECT c.codigo FROM codigos c
            JOIN fichas f ON c.ficha_id = f.id
            WHERE f.numero = ?
        ''', (numbers[current_index],)).fetchone()
    
    url = f"https://zajuna.sena.edu.co/zajuna/course/management.php?search={numbers[current_index]}"
    if resultado:
        url += f"&cod={resultado[0]}"
    
    webbrowser.open(url)
    return redirect(url_for('home'))

@app.route('/next')
def next():
    global current_index
    if not numbers:
        flash('No hay números en la lista', 'error')
        return redirect(url_for('home'))
    
    if current_index < len(numbers) - 1:
        current_index += 1
    else:
        flash('¡Última ficha alcanzada!', 'info')
    
    # Generar URL con código si existe
    with closing(sqlite3.connect('database.db')) as db:
        resultado = db.execute('''
            SELECT c.codigo FROM codigos c
            JOIN fichas f ON c.ficha_id = f.id
            WHERE f.numero = ?
        ''', (numbers[current_index],)).fetchone()
    
    url = f"https://zajuna.sena.edu.co/zajuna/course/management.php?search={numbers[current_index]}"
    if resultado:
        url += f"&cod={resultado[0]}"
    
    webbrowser.open(url)
    return redirect(url_for('home'))

@app.route('/number/<int:number>')
def show_number(number):
    """Muestra los detalles de una ficha específica"""
    with closing(sqlite3.connect('database.db')) as db:
        # Verificar si la ficha existe
        ficha = db.execute('SELECT id FROM fichas WHERE numero = ?', (number,)).fetchone()
        
        if not ficha:
            flash(f'Ficha {number} no encontrada', 'error')
            return redirect(url_for('home'))
        
        # Obtener el código asociado si existe
        codigo = db.execute('SELECT codigo FROM codigos WHERE ficha_id = ?', (ficha[0],)).fetchone()
        
        return render_template('ficha.html', 
            numero=number,
            codigo=codigo[0] if codigo else None
        )

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)