# app/controllers/admin_controller.py
import os
from app.models.ficha_model import Ficha
from app.models.codigo_model import Codigo
from flask import current_app

class AdminController:
    @staticmethod
    def cargar_fichas(file):
        try:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_fichas.txt')
            file.save(filepath)
            
            fichas = []
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.isdigit():
                        numero = int(line)
                        fichas.append(numero)
                        Ficha.crear(numero)
            return fichas
        except Exception as e:
            raise Exception(f"Error al cargar fichas: {str(e)}")

    @staticmethod
    def cargar_codigos(file):
        try:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_codigos.txt')
            file.save(filepath)
            
            if Ficha.contar() == 0:
                raise ValueError("No hay fichas cargadas. Cargue fichas primero.")
            
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.isdigit():
                        codigo = int(line)
                        ficha_sin_codigo = Ficha.obtener_sin_codigo()
                        if ficha_sin_codigo:
                            Codigo.crear(codigo, ficha_sin_codigo[0])
            return True
        except Exception as e:
            raise Exception(f"Error al cargar códigos: {str(e)}")