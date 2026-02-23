# API REST Django + Firebase - Gestión de Tareas

API REST completa para gestionar tareas usando Django, Django REST Framework y Firebase como base de datos.

## 📋 Operaciones Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/tareas/` | Listar todas las tareas |
| GET | `/api/tareas/{id}/` | Obtener una tarea por ID |
| POST | `/api/tareas/` | Crear una nueva tarea |
| PUT | `/api/tareas/{id}/` | Actualizar una tarea |
| DELETE | `/api/tareas/{id}/` | Eliminar una tarea |

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/samuelPuerto66/put-get-delete-post.git
cd put-get-delete-post
```

### 2. Crear un entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Firebase
- Descarga tu `serviceAccountKey.json` desde [Firebase Console](https://console.firebase.google.com/)
- Colócalo en: `backend/backend/serviceAccountKey.json`

### 5. Crear archivo `.env`
Crea un archivo `.env` en `backend/backend/`:
```
FIREBASE_KEYS_PATH=backend/serviceAccountKey.json
FIREBASE_WEB_API_KEY=Tu_Firebase_Web_API_Key
```

### 6. Ejecutar migraciones
```bash
python manage.py migrate
```

### 7. Iniciar el servidor
```bash
python manage.py runserver
```

La API estará disponible en: `http://127.0.0.1:8000/`

## 📝 Ejemplos de Uso

### Crear una tarea (POST)
```bash
curl -X POST http://127.0.0.1:8000/api/tareas/ \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Mi primera tarea",
    "descripcion": "Descripción de la tarea",
    "estado": "pendiente"
  }'
```

### Obtener todas las tareas (GET)
```bash
curl http://127.0.0.1:8000/api/tareas/
```

### Obtener una tarea por ID (GET)
```bash
curl http://127.0.0.1:8000/api/tareas/{id}/
```

### Actualizar una tarea (PUT)
```bash
curl -X PUT http://127.0.0.1:8000/api/tareas/{id}/ \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Tarea actualizada",
    "descripcion": "Nueva descripción",
    "estado": "en_progreso"
  }'
```

### Eliminar una tarea (DELETE)
```bash
curl -X DELETE http://127.0.0.1:8000/api/tareas/{id}/
```

## 📦 Dependencias Principales

- **Django**: Framework web
- **djangorestframework**: API REST
- **firebase-admin**: SDK de Firebase
- **python-dotenv**: Variables de entorno

## 📂 Estructura del Proyecto

```
proyecto/
├── api_tareas/           # App de tareas
│   ├── views.py          # Vistas (GET, POST, PUT, DELETE)
│   ├── serializers.py    # Validación de datos
│   ├── urls.py           # Rutas de la API
│   └── ...
├── backend/
│   └── backend/
│       ├── settings.py   # Configuración Django
│       ├── urls.py       # Rutas principales
│       ├── firebase_config.py  # Configuración Firebase
│       └── ...
├── manage.py             # CLI de Django
├── requirements.txt      # Dependencias
└── README.md            # Este archivo
```

## ⚙️ Validaciones

Las siguientes validaciones se aplican al crear/actualizar tareas:

- **titulo**: Máximo 100 caracteres, mínimo 5 caracteres (requerido)
- **descripcion**: Requerido
- **estado**: Debe ser uno de: `pendiente`, `en_progreso`, `completada` (default: `pendiente`)

## 🔐 Notas de Seguridad

⚠️ **NO subir a GitHub:**
- `serviceAccountKey.json`
- `.env`
- `venv/` (virtual environment)

Estos archivos están en `.gitignore` por seguridad.

## 📞 Soporte

Para más información sobre Django REST Framework: https://www.django-rest-framework.org/
Para más información sobre Firebase: https://firebase.google.com/docs

---

**Creado con ❤️ usando Django + Firebase**
