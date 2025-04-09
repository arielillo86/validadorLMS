# app/controllers/main_controller.py
import webbrowser
from ..models.ficha_model import Ficha
from ..models.codigo_model import Codigo

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
        """Versión simplificada con validación estricta"""
        try:
            # Obtener el código de la base de datos
            ficha = Ficha.obtener_por_numero(numero_ficha)
            if not ficha:
                return False, f'Ficha {numero_ficha} no encontrada'
            
            codigo = Codigo.obtener_por_ficha(ficha[0])
            
            # Construcción exacta requerida
            url = f"https://zajuna.sena.edu.co/zajuna/course/management.php?categoryid=1&view=courses&search={numero_ficha}"
            
            if codigo and codigo[0]:  # Validación estricta
                url += f"&courseid={codigo[0]}"
            
            webbrowser.open(url)
            return True, None
            
        except Exception as e:
            return False, f'Error: {str(e)}'