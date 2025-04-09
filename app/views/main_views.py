# app/views/main_views.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..controllers.main_controller import MainController
from ..models.ficha_model import Ficha
from ..models.codigo_model import Codigo

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    numbers = session.get('numbers', [])
    current_index = session.get('current_index', 0)
    file_loaded = session.get('file_loaded', False)
    
    current_ficha = numbers[current_index] if numbers else None
    lms_id = None
    
    if current_ficha:
        ficha = Ficha.obtener_por_numero(current_ficha)
        if ficha:
            codigo = Codigo.obtener_por_ficha(ficha[0])
            if codigo:
                lms_id = codigo[0]
    
    return render_template('index.html',
        current_ficha=current_ficha,
        lms_id=lms_id,
        prev_number=numbers[current_index - 1] if numbers and current_index > 0 else None,
        next_number=numbers[current_index + 1] if numbers and current_index < len(numbers) - 1 else None,
        numbers=numbers,
        current_index=current_index,
        file_loaded=file_loaded
    )

# Resto de las rutas (procesar_fichas, previous, next, show_number, reset)...

@main_bp.route('/procesar-fichas', methods=['POST'])
def procesar_fichas():
    fichas_texto = request.form.get('fichas', '')
    if not fichas_texto:
        flash('No se ingresaron fichas', 'error')
        return redirect(url_for('main.home'))
    
    try:
        numbers = []
        for line in fichas_texto.split('\n'):
            line = line.strip()
            if line.isdigit():
                numbers.append(int(line))
        
        if not numbers:
            flash('No se encontraron números válidos', 'error')
            return redirect(url_for('main.home'))
        
        # Guardar en sesión
        session['numbers'] = numbers
        session['current_index'] = 0
        session['file_loaded'] = True
        
        flash(f'Se cargaron {len(numbers)} fichas para validación', 'success')
        return redirect(url_for('main.home'))
    
    except Exception as e:
        flash(f'Error al procesar fichas: {str(e)}', 'error')
        return redirect(url_for('main.home'))

@main_bp.route('/previous')
def previous():
    numbers = session.get('numbers', [])
    if not numbers:
        flash('No hay fichas cargadas para navegar', 'error')
        return redirect(url_for('main.home'))
    
    current_index = session.get('current_index', 0)
    
    if current_index > 0:
        session['current_index'] = current_index - 1
        current_number = numbers[session['current_index']]
        success, message = MainController.generar_y_abrir_url(current_number)
        if not success:
            flash(message, 'warning')
    else:
        flash('¡Primera ficha alcanzada!', 'info')
    
    return redirect(url_for('main.home'))

@main_bp.route('/next')
def next():
    numbers = session.get('numbers', [])
    if not numbers:
        flash('No hay fichas cargadas para navegar', 'error')
        return redirect(url_for('main.home'))
    
    current_index = session.get('current_index', 0)
    
    if current_index < len(numbers) - 1:
        session['current_index'] = current_index + 1
        current_number = numbers[session['current_index']]
        success, message = MainController.generar_y_abrir_url(current_number)
        if not success:
            flash(message, 'warning')
    else:
        flash('¡Última ficha alcanzada!', 'info')
    
    return redirect(url_for('main.home'))

@main_bp.route('/number/<int:number>')
def show_number(number):
    with closing(sqlite3.connect('database.db')) as db:
        ficha = db.execute('SELECT id FROM fichas WHERE numero = ?', (number,)).fetchone()
        
        if not ficha:
            flash(f'Ficha {number} no encontrada', 'error')
            return redirect(url_for('main.home'))
        
        codigo = db.execute('SELECT codigo FROM codigos WHERE ficha_id = ?', (ficha[0],)).fetchone()
        
        return render_template('ficha.html', 
            numero=number,
            codigo=codigo[0] if codigo else None
        )

@main_bp.route('/reset')
def reset():
    """Ruta para limpiar la sesión (útil para desarrollo)"""
    session.clear()
    flash('Sesión reiniciada', 'info')
    return redirect(url_for('main.home'))