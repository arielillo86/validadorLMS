# app/controllers/main_controller.py
import webbrowser
from app.models.ficha_model import Ficha
from app.models.codigo_model import Codigo

class MainController:
    @staticmethod
    def procesar_fichas(fichas_texto):
        numbers = []
        for line in fichas_texto.split('\n'):
            line = line.strip()
            if line.isdigit():
                numbers.append(int(line))
                Ficha.crear(int(line))
        return numbers
    
    @staticmethod
    def generar_y_abrir_url(numero_ficha):
        """Versión mejorada que:
        - Siempre abre el navegador
        - Maneja el caso cuando no existe la ficha
        - Evita errores de NoneType
        """
        try:
            # 1. Construye URL base (siempre se genera)
            url = f"https://zajuna.sena.edu.co/zajuna/course/management.php?categoryid=1&view=courses&search={numero_ficha}"
            mensaje = None
            
            # 2. Intenta enriquecer la URL si existe la ficha
            ficha = Ficha.obtener_por_numero(numero_ficha)
            if not ficha:
                mensaje = f"Ficha {numero_ficha} no encontrada en BD local"
            else:
                try:
                    codigo = Codigo.obtener_por_ficha(ficha[0])
                    if codigo and codigo[0]:
                        url += f"&courseid={codigo[0]}"
                except Exception as db_error:
                    print(f"Error al obtener código: {db_error}")
            
            # 3. Abre el navegador SIEMPRE
            print(f"URL generada: {url}")
            webbrowser.open(url, new=2)
            
            # 4. Retorna resultado (éxito + URL) o (fallo + mensaje)
            return (True, url) if mensaje is None else (False, mensaje)
            
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            print(error_msg)
            return False, error_msg