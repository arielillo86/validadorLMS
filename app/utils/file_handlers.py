# app/utils/file_handlers.py
import os
from flask import current_app

def guardar_archivo_temporal(file, prefijo='temp'):
    try:
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], f'{prefijo}_{file.filename}')
        file.save(filepath)
        return filepath
    except Exception as e:
        raise Exception(f"Error al guardar archivo: {str(e)}")