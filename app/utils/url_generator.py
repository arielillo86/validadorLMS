# app/utils/url_generator.py
def generar_url_zajuna(numero_ficha, codigo=None):
    base_url = "https://zajuna.sena.edu.co/zajuna/course/management.php"
    params = {
        'categoryid': 1,
        'view': 'courses',
        'search': numero_ficha
    }
    
    if codigo:
        params['courseid'] = codigo
    
    query_string = '&'.join(f"{k}={v}" for k, v in params.items())
    return f"{base_url}?{query_string}"