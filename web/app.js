
const API_URL = "/api/cpus";

const tabla = document.getElementById("tablaProcesadores");
const total = document.getElementById("totalProcesadores");
const botonActualizar = document.getElementById("btnActualizar");
const botonRegistrar = document.getElementById("btnRegistrar");
const formulario = document.getElementById("formProcesador");
const mensaje = document.getElementById("mensaje");

function mostrarMensaje(texto, tipo) {
    mensaje.textContent = texto;
    mensaje.className = `mensaje ${tipo}`;
}

async function cargarProcesadores() {
    botonActualizar.disabled = true;
    total.textContent = "Cargando inventario...";

    try {
        const respuesta = await fetch(API_URL, {
            cache: "no-store"
        });

        if (!respuesta.ok) {
            throw new Error("No se pudo consultar el inventario");
        }

        const procesadores = await respuesta.json();

        if (!Array.isArray(procesadores)) {
            throw new Error("La respuesta de la API no es válida");
        }

        tabla.replaceChildren();

        if (procesadores.length === 0) {
            const fila = document.createElement("tr");
            const celda = document.createElement("td");

            celda.colSpan = 6;
            celda.textContent = "No hay procesadores registrados";

            fila.appendChild(celda);
            tabla.appendChild(fila);
        }

        procesadores.forEach((cpu) => {
            const fila = document.createElement("tr");

            const valores = [
                cpu.id,
                cpu.marca,
                cpu.modelo,
                cpu.caracteristicas.nucleos,
                cpu.caracteristicas.hilos,
                cpu.caracteristicas.frecuencia_maxima
            ];

            valores.forEach((valor) => {
                const celda = document.createElement("td");
                celda.textContent = String(valor);
                fila.appendChild(celda);
            });

            tabla.appendChild(fila);
        });

        total.textContent =
            `Total de procesadores registrados: ${procesadores.length}`;

    } catch (error) {
        total.textContent = "Error al cargar el inventario";

        tabla.replaceChildren();

        const fila = document.createElement("tr");
        const celda = document.createElement("td");

        celda.colSpan = 6;
        celda.textContent =
            "No se pudo establecer conexión con la API.";

        fila.appendChild(celda);
        tabla.appendChild(fila);

        console.error(error);

    } finally {
        botonActualizar.disabled = false;
    }
}

async function registrarProcesador(evento) {
    evento.preventDefault();

    const procesador = {
        marca: document.getElementById("marca").value.trim(),
        modelo: document.getElementById("modelo").value.trim(),
        caracteristicas: {
            nucleos: Number(
                document.getElementById("nucleos").value
            ),
            hilos: Number(
                document.getElementById("hilos").value
            ),
            frecuencia_maxima: document.getElementById(
                "frecuencia"
            ).value.trim()
        }
    };

    botonRegistrar.disabled = true;
    mostrarMensaje("Registrando procesador...", "");

    try {
        const respuesta = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(procesador)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                resultado.error || "No se pudo registrar"
            );
        }

        mostrarMensaje(
            "Procesador registrado correctamente.",
            "exito"
        );

        formulario.reset();

        await cargarProcesadores();

    } catch (error) {
        mostrarMensaje(error.message, "error");
        console.error(error);

    } finally {
        botonRegistrar.disabled = false;
    }
}

botonActualizar.addEventListener(
    "click",
    cargarProcesadores
);

formulario.addEventListener(
    "submit",
    registrarProcesador
);

document.addEventListener(
    "DOMContentLoaded",
    cargarProcesadores
);
