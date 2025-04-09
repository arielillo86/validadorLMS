# app/models/ficha_model.py
from .database import get_db

class Ficha:
    @staticmethod
    def crear(numero):
        with get_db() as db:
            db.execute('INSERT OR IGNORE INTO fichas (numero) VALUES (?)', (numero,))
            db.commit()
    
    @staticmethod
    def obtener_por_numero(numero):
        with get_db() as db:
            return db.execute('SELECT id FROM fichas WHERE numero = ?', (numero,)).fetchone()
    
    @staticmethod
    def obtener_todas():
        with get_db() as db:
            return db.execute('SELECT * FROM fichas').fetchall()
    
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
            ''').fetchone()