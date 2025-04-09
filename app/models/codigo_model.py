# app/models/codigo_model.py
from .database import get_db

class Codigo:
    @staticmethod
    def crear(codigo, ficha_id):
        with get_db() as db:
            db.execute('INSERT INTO codigos (codigo, ficha_id) VALUES (?, ?)',
                      (codigo, ficha_id))
            db.commit()
    
    @staticmethod
    def obtener_por_ficha(ficha_id):
        with get_db() as db:
            return db.execute('SELECT codigo FROM codigos WHERE ficha_id = ?', 
                           (ficha_id,)).fetchone()
    
    @staticmethod
    def obtener_parejas():
        """Obtiene todas las fichas con sus códigos"""
        with get_db() as db:
            return db.execute('''
                SELECT f.numero, c.codigo
                FROM fichas f
                LEFT JOIN codigos c ON f.id = c.ficha_id
                ORDER BY f.numero
            ''').fetchall()