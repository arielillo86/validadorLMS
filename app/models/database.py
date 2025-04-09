import sqlite3
import os
from contextlib import closing
from flask import current_app, g

def get_db():
    """
    Obtiene una conexión a la base de datos con manejo de contexto.
    Usa el objeto 'g' de Flask para almacenar la conexión durante el request.
    """
    if not hasattr(current_app, 'config'):
        raise RuntimeError("Application context not available")
    
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            timeout=30,  # Aumenta timeout para evitar bloqueos
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # Para acceso a columnas por nombre
    return g.db

def close_db(e=None):
    """
    Cierra la conexión a la base de datos al finalizar el request.
    Se registra como teardown_appcontext.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    """Inicializa la base de datos y registra manejadores de contexto"""
    with app.app_context():
        # Configuración de directorios
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        db_dir = os.path.dirname(app.config['DATABASE'])
        if db_dir:  # Si DATABASE incluye path
            os.makedirs(db_dir, exist_ok=True)
        
        # Creación de tablas con manejo de transacciones
        db = get_db()
        try:
            with closing(db.cursor()) as cursor:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS fichas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero INTEGER UNIQUE NOT NULL CHECK(typeof(numero) = 'integer')
                )''')
                
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS codigos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo INTEGER NOT NULL CHECK(typeof(codigo) = 'integer'),
                    ficha_id INTEGER UNIQUE,
                    FOREIGN KEY (ficha_id) REFERENCES fichas(id)
                )''')
            db.commit()
        except sqlite3.Error as e:
            db.rollback()
            raise RuntimeError(f"Error inicializando DB: {str(e)}")
    
    # Registra el cierre automático de conexiones
    app.teardown_appcontext(close_db)

def check_tables_exist():
    """Verifica que las tablas necesarias existan con manejo de errores"""
    try:
        with closing(get_db().cursor()) as cursor:
            tables = cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('fichas', 'codigos')
            """).fetchall()
            return len(tables) == 2
    except sqlite3.Error as e:
        current_app.logger.error(f"Error verificando tablas: {str(e)}")
        return False