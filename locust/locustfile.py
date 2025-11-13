
from locust import HttpUser, task, between, SequentialTaskSet
import json
import random

# Credenciales de prueba
USERS = [
    {"username": "johnd", "password": "foo"},
    {"username": "admin", "password": "admin"},
    {"username": "janed", "password": "ddd"}
]

# Tareas de ejemplo para TODOs
TODO_TASKS = [
    "Implementar nueva funcionalidad",
    "Revisar código",
    "Escribir documentación",
    "Hacer code review",
    "Optimizar rendimiento",
    "Corregir bugs",
    "Actualizar dependencias",
    "Crear tests unitarios",
    "Refactorizar módulo",
    "Deploy a producción"
]


class UserBehavior(SequentialTaskSet):
    """
    Comportamiento secuencial de un usuario:
    1. Login
    2. Ver TODOs
    3. Crear TODOs
    4. Eliminar TODOs
    5. Logout
    """
    
    def on_start(self):
        """Se ejecuta cuando inicia el usuario"""
        self.token = None
        self.todos = []
        self.credentials = random.choice(USERS)
    
    @task
    def login(self):
        """Realizar login y obtener token JWT"""
        response = self.client.post(
            "/login",
            json={
                "username": self.credentials["username"],
                "password": self.credentials["password"]
            },
            headers={"Content-Type": "application/json"},
            name="01-Login"
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("accessToken")
            print(f"✓ Login exitoso: {self.credentials['username']}")
        else:
            print(f"✗ Login fallido: {response.status_code}")

class WebsiteUser(HttpUser):
    """Usuario que simula navegación en el sitio web"""
    tasks = [UserBehavior]
    wait_time = between(1, 3)  # Espera entre 1 y 3 segundos entre tareas
    
    # Headers comunes para todas las peticiones
    def on_start(self):
        self.client.headers.update({
            "User-Agent": "Locust Load Test",
            "Accept": "application/json"
        })

