from flask import Flask, render_template, request, redirect, url_for
import webbrowser

app = Flask(__name__)

# Lista de números (inicialmente vacía)
numbers = []
current_index = 0  # Índice actual en la lista

# Función para cargar la lista de números desde un archivo
def load_numbers_from_file(file):
    numbers = [int(line.strip()) for line in file if line.strip()]
    return numbers

@app.route('/')
def home():
    global current_index
    return render_template('index.html', current_number=numbers[current_index] if numbers else None, numbers=numbers)

@app.route('/upload', methods=['POST'])
def upload():

    global numbers, current_index
    # Verificar si se envió un archivo
    if 'file' not in request.files:
        return "No se seleccionó ningún archivo."
    
    file = request.files['file']
    # Verificar si el archivo tiene un nombre válido
    if file.filename == '':
        return "No se seleccionó ningún archivo."
    
    # Cargar la lista de números desde el archivo
    if file and file.filename.endswith('.txt'):
        numbers = load_numbers_from_file(file)
        current_index = 0  # Reiniciar el índice
        return redirect(url_for('home'))
    else:
        return "El archivo debe ser un archivo de texto (.txt)."



@app.route('/generate_url')
def generate_url():
    global current_index
    # Obtener el número ingresado por el usuario
    number = request.args.get('number', type=int)
    
    if number is not None:
        # Generar la URL
        url = f"https://zajuna.sena.edu.co/zajuna/course/management.php?search={number}"
        
        # Abrir la URL en el navegador
        webbrowser.open(url)
        
        return f"Ficha {number}: <a href='{url}'>{url}</a>"
    else:
        return "Por favor, ingresa un número válido."

@app.route('/previous')
def previous():
    global current_index
    if not numbers:
        return "No hay números en la lista."
    
    # Ir al número anterior en la lista
    if current_index > 0:
        current_index -= 1
    else:
        current_index = len(numbers) - 1  # Volver al último si es el primero
    
    # Generar la URL para el número anterior
    url = f"https://zajuna.sena.edu.co/zajuna/course/management.php?search={numbers[current_index]}"
    webbrowser.open(url)
    
    return render_template('index.html', current_number=numbers[current_index], numbers=numbers)

@app.route('/next')
def next():
    global current_index
    if not numbers:
        return "No hay números en la lista."
            
    # Ir al siguiente número en la lista
    if current_index < len(numbers) - 1:
        current_index += 1
    else:
        current_index = 0  # Volver al primero si es el último
    
    # Generar la URL para el siguiente número
    url = f"https://zajuna.sena.edu.co/zajuna/course/management.php?search={numbers[current_index]}"
    webbrowser.open(url)
    
    return render_template('index.html', current_number=numbers[current_index], numbers=numbers)

@app.route('/number/<int:number>')
def show_number(number):
    return f"La ficha es: {number}"

if __name__ == '__main__':
    app.run(debug=True)