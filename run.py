from app import create_app

# Nombre de variable exacto que busca Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)