# app/views/admin_views.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..controllers.admin_controller import AdminController
from ..models.database import check_tables_exist
from ..models.codigo_model import Codigo

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def admin():
    if not check_tables_exist():
        flash('La base de datos no está configurada correctamente', 'error')
        return redirect(url_for('main.home'))
    
    return render_template('admin.html', parejas=Codigo.obtener_parejas())

@admin_bp.route('/upload-fichas', methods=['POST'])
def admin_upload_fichas():
    if 'file' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('admin.admin'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('admin.admin'))
    
    try:
        if file and file.filename.endswith('.txt'):
            AdminController.cargar_fichas(file)
            flash('Fichas cargadas correctamente', 'success')
        else:
            flash('El archivo debe ser un .txt', 'error')
    except Exception as e:
        flash(f'Error al cargar fichas: {str(e)}', 'error')
    
    return redirect(url_for('admin.admin'))

# Similar para admin_upload_codigos...

@admin_bp.route('/upload-codigos', methods=['POST'])
def admin_upload_codigos():
    if 'file' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('admin.admin'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('admin.admin'))
    
    try:
        if file and file.filename.endswith('.txt'):
            AdminController.cargar_codigos(file)
            flash('Códigos cargados correctamente', 'success')
        else:
            flash('El archivo debe ser un .txt', 'error')
    except Exception as e:
        flash(f'Error al cargar códigos: {str(e)}', 'error')
    
    return redirect(url_for('admin.admin'))