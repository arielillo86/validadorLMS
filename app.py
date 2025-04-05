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

#@app.route('/')
#def home():
#    global current_index
#    return render_template('index.html', current_number=numbers[current_index] if numbers else None, numbers=numbers)

@app.route('/')
def home():
    global current_index, numbers
    
    if not numbers:
        return render_template('index.html', 
            current_number=None,
            prev_number=None,
            next_number=None,
            numbers=[],
            file_loaded=False
        )
    
    # Lógica lineal (sin circularidad)
    prev_number = numbers[current_index - 1] if current_index > 0 else None
    next_number = numbers[current_index + 1] if current_index < len(numbers) - 1 else None
    
    return render_template('index.html',
        current_number=numbers[current_index],
        prev_number=prev_number,  # None si es el primero
        next_number=next_number,  # None si es el último
        numbers=numbers,
        file_loaded=True
    )


@app.route('/upload', methods=['POST'])
def upload():
    global numbers, current_index
    
    if 'file' not in request.files:
        return "No se seleccionó ningún archivo."
    
    file = request.files['file']
    if file.filename == '':
        return "No se seleccionó ningún archivo."
    
    if file and file.filename.endswith('.txt'):
        numbers = []
        for line in file:
            line = line.strip()
            if line.isdigit():  # Solo acepta números
                numbers.append(int(line))
        
        if not numbers:  # Si el archivo estaba vacío o no tenía números válidos
            return "El archivo no contiene números válidos."
        
        current_index = 0
        return redirect(url_for('home'))
    else:
        return "El archivo debe ser un .txt."

def load_numbers_from_file(file):
    numbers = []
    for line in file:
        line = line.strip()
        if line and line.isdigit():  # Solo líneas con dígitos
            numbers.append(int(line))
    return numbers

@app.route('/previous')
def previous():
    global current_index
    if not numbers:
        return "No hay números en la lista."
    
    # Navegación lineal (no circular)
    if current_index > 0:
        current_index -= 1
    
    # Abrir URL automáticamente
    url = f"https://zajuna.sena.edu.co/zajuna/course/management.php?search={numbers[current_index]}"
    webbrowser.open(url)
    
    return redirect(url_for('home'))  # Redirige para actualizar la vista

@app.route('/next')
def next():
    global current_index
    if not numbers:
        return "No hay números en la lista."
    
    # Navegación lineal (no circular)
    if current_index < len(numbers) - 1:
        current_index += 1
    
    # Abrir URL automáticamente
    url = f"https://zajuna.sena.edu.co/zajuna/course/management.php?search={numbers[current_index]}"
    webbrowser.open(url)
    
    return redirect(url_for('home'))  # Redirige para actualizar la vista

@app.route('/number/<int:number>')
def show_number(number):
    return f"La ficha es: {number}"

## limpia cache navegador
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

if __name__ == '__main__':
    app.run(debug=True)