# Grupo 1 – Inventario de Procesadores

**2P – Tarea 5: Aplicación completa con Docker Compose y límites de recursos**  
**Asignatura:** Arquitectura de Computadoras  
**Universidad:** Universidad Tecnológica de Honduras (UTH)  
**Componente asignado:** Procesadores  
**Fecha de entrega:** 15 de noviembre de 2026, antes de las 11:00 a. m.

## 1. ¿De qué trata el proyecto?

Este proyecto amplía la API REST de procesadores que desarrollamos en la Tarea 3. Ahora podemos consultar y registrar procesadores desde una página web, almacenar los registros en SQLite y ejecutar la aplicación mediante Docker Compose.

También realizamos pruebas de aislamiento y control de recursos de Linux con Docker, `stress-ng`, cgroups y namespaces.

La solución cuenta con **dos servicios principales**:

- **`web`:** nginx sirve `index.html` y `app.js` y reenvía las solicitudes `/api/` al servicio de la API.
- **`api`:** Flask con Gunicorn atiende las solicitudes y almacena los procesadores en SQLite.

Docker Compose conecta ambos servicios por la red `red-g1` y monta el volumen `g1-inventario-datos` para conservar el archivo `/datos/inventario.db`.

## 2. Tecnologías utilizadas

- Python 3.12, Flask 3.1.2 y Gunicorn 23.0.0.
- SQLite para guardar el inventario.
- HTML, CSS y JavaScript para la interfaz.
- nginx para servir la web y actuar como proxy inverso.
- Docker, Docker Compose y Docker Hub.
- Ubuntu 24.04 y `stress-ng` para las pruebas de recursos.

## 3. Repositorios

**Código fuente (GitHub):**  
https://github.com/raraudales-glitch/Aplicaci-n-completa-con-Docker-Compose-y-l-mites-de-recursos

**Imagen de la API (Docker Hub):**  
https://hub.docker.com/r/ashurrov/g1-cpus-api

**Imagen publicada:** `ashurrov/g1-cpus-api:1.0`

## 4. Estructura del proyecto

```text
g1-inventario/
├── api/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── Dockerfile.prod
│   └── .dockerignore
├── web/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── index.html
│   └── app.js
├── estres/
│   └── Dockerfile
├── compose.yaml
├── .gitignore
└── README.md
```

`api/Dockerfile` corresponde a la práctica anterior. En Docker Compose usamos **`api/Dockerfile.prod`**, con usuario `app`, Gunicorn y `HEALTHCHECK`.

> El archivo `inventario-respaldo.db` es una copia local opcional. No debe subirse a GitHub.

## 5. Requisitos para ejecutarlo

1. Tener Docker Desktop instalado, iniciado y configurado para contenedores Linux.
2. Tener Git instalado para clonar el repositorio.
3. Tener disponible el **puerto 8081** del equipo. Si otro programa lo utiliza, habrá que liberarlo antes de iniciar esta tarea.
4. Usar PowerShell o una terminal compatible.

## 6. Clonar el repositorio de GitHub

En PowerShell, entrar a la ubicación deseada y clonar:

```powershell
cd "$env:USERPROFILE\Desktop"
git clone https://github.com/raraudales-glitch/Aplicaci-n-completa-con-Docker-Compose-y-l-mites-de-recursos.git g1-inventario
cd g1-inventario
```

Si ya clonaste este proyecto, **no necesitas clonarlo de nuevo**. Para actualizar tu copia local, primero revisa si tienes cambios propios y después, si corresponde, utiliza `git pull --ff-only`.

## 7. Iniciar la aplicación con Docker Compose

Dentro de la carpeta que contiene `compose.yaml`:

```powershell
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

En el resultado de `docker compose ps` se espera:

- Servicio **`api`** en estado `healthy`.
- Servicio **`web`** en ejecución y publicado en `8081:80`.

Abrir la página en el navegador:

**http://localhost:8081**

La API utiliza el puerto `5000` **solo dentro de la red Docker**. El navegador accede a ella por nginx, a través de `http://localhost:8081/api/`.

### 7.1 Funciones de la página

- Mostrar los procesadores almacenados.
- Actualizar la tabla del inventario.
- Registrar procesadores nuevos con marca, modelo, núcleos, hilos y frecuencia máxima.

### 7.2 Consultar las rutas desde PowerShell

Estado de la API:

```powershell
Invoke-RestMethod -Uri "http://localhost:8081/api/estado"
```

Listado:

```powershell
Invoke-RestMethod -Uri "http://localhost:8081/api/cpus" | Format-Table id, marca, modelo -AutoSize
```

Consulta de un procesador por su ID:

```powershell
Invoke-RestMethod -Uri "http://localhost:8081/api/cpus/1"
```

Registro de prueba mediante POST:

```powershell
$cpu = @{
    marca = "AMD"
    modelo = "Ryzen 9 7950X"
    caracteristicas = @{
        nucleos = 16
        hilos = 32
        frecuencia_maxima = "5.7 GHz"
    }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://localhost:8081/api/cpus" `
    -Method POST `
    -ContentType "application/json" `
    -Body $cpu
```

**Atención:** cada POST exitoso crea un registro nuevo. No repitas la prueba si quieres evitar duplicados.

## 8. Configuración exigida por la Tarea 5

El archivo `compose.yaml` establece:

- Servicios `api` y `web`.
- Red Docker `red-g1`.
- Volumen `datos`, denominado `g1-inventario-datos`, montado en `/datos`.
- Servicio `web` publicado en `8081:80`; la API no publica un puerto al equipo.
- `depends_on` con `condition: service_healthy`.
- `healthcheck` de la API a `/api/estado` cada 10 segundos.
- `restart: unless-stopped` para la API.
- Límite de la API de **0.50 CPU** y **128M de memoria**.

En `api/Dockerfile.prod` usamos un usuario `app` sin privilegios, volumen `/datos` y Gunicorn con dos workers.

### 8.1 Verificar que la API no corre como root

```powershell
docker compose exec api id
```

El UID debe ser distinto de `0`. En nuestras pruebas se obtuvo `uid=999(app)`.

## 9. Pruebas de la práctica (10 puntos)

Los siguientes apartados corresponden a los diez pasos solicitados en la guía. **Los resultados deben comprobarse en la computadora de quien ejecute la práctica.** No debe entregarse como propia una captura generada en otro equipo.

### Paso 1. SQLite y registro POST

La API utiliza `DB_PATH=/datos/inventario.db`. Consultar el inventario con `GET /api/cpus` y registrar un componente desde el formulario o mediante `POST /api/cpus`.

### Paso 2. Dockerfile de producción

Construir y revisar la imagen:

```powershell
docker build -f .\api\Dockerfile.prod -t g1-cpus-api:prod .\api
docker images g1-cpus-api
docker compose exec api id
```

Verificar usuario `app`, Gunicorn, directorio `/datos` y `HEALTHCHECK`.

### Paso 3. Web y proxy nginx

Abrir `http://localhost:8081`, comprobar la tabla, el botón **Actualizar** y el formulario. Verificar que nginx reenvía `/api/` a `http://api:5000`:

```powershell
Invoke-RestMethod -Uri "http://localhost:8081/api/estado"
```

### Paso 4. Compose, red y volumen

```powershell
docker compose config --quiet
docker compose up -d --build
docker compose ps
docker network inspect red-g1
docker volume inspect g1-inventario-datos
```

Comprobar que el servicio `web` espera a que la API esté `healthy` y que únicamente publica el puerto 8081.

### Paso 5. Límites de CPU y memoria de la API

Revisar en `compose.yaml` los valores `cpus: "0.50"` y `memory: 128M` y comprobar el estado:

```powershell
docker inspect --format '{{.HostConfig.NanoCpus}} {{.HostConfig.Memory}}' g1-inventario-api-1
docker stats --no-stream g1-inventario-api-1
```

Los límites efectivos también se pueden comprobar mediante los archivos de cgroups cuando estén disponibles.

### Paso 6. Levantar la aplicación y registrar tres procesadores

```powershell
docker compose up -d --build
docker compose ps
```

Registrar **tres procesadores desde la página** y tomar una captura de la tabla y el estado de los servicios. En nuestras pruebas la tabla llegó a tener nueve procesadores: cinco iniciales y cuatro agregados.

### Paso 7. Usuario sin privilegios y persistencia

```powershell
docker compose exec api id
docker compose down
docker compose up -d
docker compose ps
Invoke-RestMethod -Uri "http://localhost:8081/api/cpus" | Format-Table id, marca, modelo -AutoSize
```

**`docker compose down` conserva el volumen y los registros.**

**Advertencia: el comando siguiente elimina el volumen y los registros añadidos.** Antes de probarlo, respalda el archivo SQLite fuera del volumen. No lo ejecutes en un proyecto con datos que no puedas perder.

Crear respaldo SQLite y copiarlo a Windows:

```powershell
docker compose exec -T api python -c "import sqlite3; a=sqlite3.connect('/datos/inventario.db'); b=sqlite3.connect('/datos/respaldo.db'); a.backup(b); b.close(); a.close()"
docker compose cp api:/datos/respaldo.db .\inventario-respaldo.db
Get-Item .\inventario-respaldo.db
```

Solo después de comprobar el respaldo:

```powershell
docker compose down -v
docker compose up -d
Invoke-RestMethod -Uri "http://localhost:8081/api/cpus" | Format-Table id, marca, modelo -AutoSize
```

Al recrear el volumen, la aplicación carga nuevamente los cinco procesadores iniciales. Los registros adicionales desaparecen hasta que se restauren desde el respaldo.

Para restaurar la copia (si se necesita):

```powershell
docker compose cp .\inventario-respaldo.db api:/datos/inventario-restaurado.db
docker compose exec -T api python -c "import sqlite3; a=sqlite3.connect('/datos/inventario-restaurado.db'); b=sqlite3.connect('/datos/inventario.db'); a.backup(b); b.close(); a.close()"
```

### Paso 8. Imagen de estrés y `docker stats`

Construir:

```powershell
docker build -t g1/estres:1.0 .\estres
```

Ejecutar con los límites de la guía:

```powershell
docker run -d --name g1-estres --cpus=1.5 --memory=512m --pids-limit=100 g1/estres:1.0
docker stats g1-estres
```

Para salir de `docker stats`, presionar **Ctrl + C**. La imagen de estrés ejecuta una carga con un tiempo limitado de **300 segundos**. Si el contenedor ya existe y terminó, usar `docker start g1-estres` antes de consultar archivos dentro de él.

**Medición obtenida en nuestra práctica (una captura específica, no valor garantizado):** CPU 148.90 %, memoria 284.3 MiB de 512 MiB y 5 PIDs.

### Paso 9. `docker inspect`, cgroups, actualización y namespaces

Si el contenedor de estrés está detenido, iniciarlo:

```powershell
docker start g1-estres
```

Consultar la configuración de Docker:

```powershell
docker inspect --format 'NanoCpus={{.HostConfig.NanoCpus}} Memory={{.HostConfig.Memory}} PidsLimit={{.HostConfig.PidsLimit}}' g1-estres
```

Consultar los límites que aplica Linux:

```powershell
docker exec g1-estres cat /sys/fs/cgroup/cpu.max
docker exec g1-estres cat /sys/fs/cgroup/memory.max
docker exec g1-estres cat /sys/fs/cgroup/pids.max
```

Con `--cpus=1.5`, en nuestras pruebas `cpu.max` mostró `150000 100000`, lo que equivale a 1.5 CPUs. La memoria mostró `536870912` bytes (512 MiB) y el límite de PIDs mostró `100`.

Reducir la cuota de CPU sin recrear el contenedor:

```powershell
docker update --cpus=0.5 g1-estres
docker exec g1-estres cat /sys/fs/cgroup/cpu.max
docker inspect --format '{{.HostConfig.NanoCpus}}' g1-estres
docker stats --no-stream g1-estres
```

Si terminó la carga, ejecutar primero `docker start g1-estres`. Con el límite nuevo, obtuvimos `cpu.max = 50000 100000` y un consumo de 49.68 % de CPU bajo carga.

Observar el aislamiento:

```powershell
docker exec g1-estres ls -l /proc/self/ns
docker exec g1-estres hostname
docker exec g1-estres ps -e
```

Cuatro namespaces que deben explicarse en el informe:

| Namespace | Aislamiento |
|---|---|
| `pid` | Vista y numeración de procesos. |
| `net` | Interfaces y recursos de red. |
| `mnt` | Puntos de montaje. |
| `uts` | Nombre del host y del dominio. |

### Paso 10. Docker Hub y ejecución en otra computadora

**Publicación realizada:**

```powershell
docker tag g1-cpus-api:prod ashurrov/g1-cpus-api:1.0
docker push ashurrov/g1-cpus-api:1.0
```

**Prueba pendiente en el equipo de otro integrante:**

```powershell
docker pull ashurrov/g1-cpus-api:1.0
docker run -d --name g1-api-remota -p 5001:5000 -v g1-datos-remotos:/datos ashurrov/g1-cpus-api:1.0
docker ps --filter "name=g1-api-remota"
Invoke-RestMethod -Uri "http://localhost:5001/api/estado"
Invoke-RestMethod -Uri "http://localhost:5001/api/cpus" | Format-Table id, marca, modelo -AutoSize
```

Si el puerto 5001 estuviera ocupado en el otro equipo, habría que identificar qué lo usa antes de repetir la prueba. El equipo receptor necesita Docker Desktop con contenedores Linux.

La prueba se considera completada cuando el otro integrante proporciona evidencia de `docker pull`, `docker run` y una respuesta válida de la API.

## 10. Detener o volver a iniciar los servicios

Detener los contenedores **conservando los datos**:

```powershell
docker compose down
```

Reiniciar:

```powershell
docker compose up -d
```

Verificar:

```powershell
docker compose ps
```

**No utilizar `docker compose down -v` salvo en la prueba específica y con respaldo verificado.**

## 11. Estado de avance

- API Flask con SQLite y POST: probado.
- nginx y Docker Compose: probados.
- Servicio API en `healthy` y usuario `app` sin privilegios: probado.
- Persistencia con `down` y pérdida controlada con `down -v`: probadas; base de datos restaurada.
- Pruebas de `stress-ng`, `docker stats`, `docker inspect`, cgroups, `docker update` y namespaces: realizadas.
- Imagen `ashurrov/g1-cpus-api:1.0` publicada en Docker Hub.
- **Pendiente:** descarga y ejecución de la imagen en la computadora de otro integrante.
- **Opcional:** punto extra de SQL Server en Compose, si el grupo decide implementarlo.

---

**Grupo 1 – Procesadores | Arquitectura de Computadoras | UTH**
