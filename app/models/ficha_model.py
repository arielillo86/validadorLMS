# app/models/ficha_model.py
from .database import get_db
from contextlib import contextmanager
import sqlite3

class Ficha:
    @staticmethod
    @contextmanager
    def _bulk_insert_context():
        """Contexto para operaciones masivas optimizadas"""
        db = get_db()
        try:
            # Configuración para máxima velocidad
            db.executescript("""
            PRAGMA journal_mode = MEMORY;
            PRAGMA synchronous = OFF;
            PRAGMA temp_store = MEMORY;
            PRAGMA cache_size = -10000;  # 10MB cache
            BEGIN TRANSACTION;
            """)
            yield db
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            # Restaura configuración segura
            db.executescript("""
            PRAGMA journal_mode = WAL;
            PRAGMA synchronous = NORMAL;
            """)

    @staticmethod
    def crear_masivo(numeros):
        """Inserta múltiples fichas en una sola operación"""
        with Ficha._bulk_insert_context() as db:
            db.executemany(
                "INSERT OR IGNORE INTO fichas (numero) VALUES (?)",
                [(n,) for n in numeros]
            )

    @staticmethod
    def crear(numero):
        """Para inserciones individuales (menos eficiente)"""
        with get_db() as db:
            db.execute("INSERT OR IGNORE INTO fichas (numero) VALUES (?)", (numero,))
            db.commit()
    
    # Métodos de consulta (optimizados con índices)
    @staticmethod
    def obtener_por_numero(numero):
        with get_db() as db:
            return db.execute('''
                SELECT id FROM fichas 
                WHERE numero = ? 
                LIMIT 1
            ''', (numero,)).fetchone()
    
    @staticmethod
    def obtener_todas():
        with get_db() as db:
            return db.execute('''
                SELECT * FROM fichas 
                ORDER BY numero
            ''').fetchall()
    
    @staticmethod
    def contar():
        with get_db() as db:
            return db.execute('SELECT COUNT(*) FROM fichas').fetchone()[0]
    
    @staticmethod
    def obtener_sin_codigo():
        with get_db() as db:
            return db.execute('''
                SELECT f.id FROM fichas f
                LEFT JOIN codigos c ON f.id = c.ficha_id
                WHERE c.id IS NULL
                ORDER BY f.id
                LIMIT 1
            ''').fetchone()