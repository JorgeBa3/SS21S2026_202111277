# Manual Técnico y de Implementación - Proyecto 1 SG-Food

## Datos del Estudiante
**Nombre:** Jorge Alejandro De León Batres  
**Carnet:** 202111277  
**Curso:** Seminario de Sistemas 2  

---

## 1. Introducción y Objetivos
El presente documento detalla la implementación técnica del flujo completo de Inteligencia de Negocios para el proyecto SG-Food. El objetivo principal es consolidar información proveniente de múltiples fuentes heterogéneas (Base de datos transaccional en la nube, archivos Excel y archivos planos) hacia un Data Warehouse (DW) estructurado y, posteriormente, implementar un modelo analítico multidimensional utilizando SQL Server Integration Services (SSIS) y SQL Server Analysis Services (SSAS).

---

## 2. Configuración del Entorno y Conexiones Origen

Para iniciar el flujo de extracción, se configuró la conexión hacia la base de datos transaccional alojada en la nube (`SGFoodOLTP`).

**Conectando a la DB en la nube:** Se utilizaron las credenciales de lectura proporcionadas para el usuario `sgfood_reader`.  
![alt text](image.png)

**Validación de Origen:** Antes de iniciar la extracción, se verificó mediante una consulta SQL que la fuente principal contuviera exactamente los 1000 registros transaccionales esperados para garantizar la integridad inicial de los datos.  
![alt text](image-1.png)

---

## 3. Desarrollo del Flujo ETL (Integration Services - SSIS)

Se creó un proyecto de Integración de Servicios en Visual Studio para orquestar la extracción, transformación y carga (ETL) hacia el Data Warehouse local.

**Extensiones instaladas:** Se validó la correcta instalación de las herramientas de Data Tools para Integration y Analysis Services.  
![alt text](image-2.png)

**Creación del Proyecto:** ![alt text](image-3.png)  
![alt text](image-4.png)

### 3.1 Administradores de Conexiones
Se configuraron los orígenes de datos. Para evitar errores de compatibilidad con versiones recientes de SQL Server, se ajustó el proveedor OLE DB.

**Configuración de conexión:** ![alt text](image-5.png)

**Cambio de proveedor a Microsoft OLE DB Driver for SQL Server:** Este cambio garantiza una conexión estable y segura hacia el destino de nuestro Data Warehouse.  
![alt text](image-6.png)  
![alt text](image-7.png)

### 3.2 Flujo de Trabajo (Pipeline Principal)
El flujo de control se diseñó de manera secuencial: primero se ejecutan las tareas de limpieza, luego la carga de dimensiones (catálogos únicos) y finalmente la carga de la tabla de hechos.

**Flujo de Control General:** ![alt text](image-8.png)

Para la carga de datos, se configuraron los destinos OLE DB apuntando a las tablas dimensionales y de hechos de nuestra base de datos local.  
**Agregar el destino y su conexión:** ![alt text](image-9.png)  
![alt text](image-10.png)

### 3.3 Integración de Fuentes Heterogéneas (Excel y Archivos Planos)
Para cumplir con el requerimiento de orígenes múltiples, se implementó la lectura de archivos externos (Excel `.xlsx` y de texto). Se aplicaron transformaciones de conversión de datos para unificar tipos, "Unión de Todo" (Union All) para consolidar los flujos, estandarización a mayúsculas y limpieza de duplicados (Sort).

**Carga de Excel e integración al Pipeline:** ![alt text](image-29.png)  

**Agregar Excel Source:** ![alt text](image-30.png)  

**Pipeline actualizada (Dimensiones y Hechos):** *En este flujo de datos se aplican las Búsquedas (Lookups) para reemplazar las llaves naturales por las Llaves Subrogadas (SK_) antes de insertar en la Fact Table.* ![alt text](image-31.png)

---

## 4. Modelo Analítico Multidimensional (Analysis Services - SSAS)

Una vez poblado el Data Warehouse, se construyó el modelo analítico para permitir consultas OLAP eficientes sobre las ventas e inventarios de SG-Food.

### 4.1 Orígenes de Datos y Vistas (DSV)
Se estableció la conexión desde SSAS hacia el Data Warehouse local que se acaba de cargar con SSIS.

**Nueva conexión SSAS:** ![alt text](image-12.png)  

**Definición del Origen de datos:** ![alt text](image-11.png)  
![alt text](image-13.png)

**Vistas de origen de datos (Data Source View):** Se definió el modelo dimensional lógico (Esquema de Estrella/Constelación), enlazando la tabla de hechos con sus respectivas dimensiones mediante las llaves subrogadas.  
![alt text](image-14.png)

### 4.2 Creación del Cubo OLAP
Se construyó el cubo seleccionando los grupos de medida pertinentes derivados de la Fact Table (Cantidad Vendida, Importe Neto, Costos, Existencias de Inventario).

**Proceso de creación del Cubo:** ![alt text](image-15.png)  
![alt text](image-16.png)  
![alt text](image-17.png)  
![alt text](image-18.png)  
![alt text](image-19.png)  
![alt text](image-20.png)  
![alt text](image-21.png)

### 4.3 Diseño de Dimensiones y Jerarquías
Para facilitar el análisis intuitivo por parte de los usuarios finales (Drill-down y Roll-up), se configuraron atributos y jerarquías personalizadas en las dimensiones.

**1. Dimensión y Jerarquía de Tiempo:** Atributos clave organizados lógicamente (Año -> Mes -> Día).  
![alt text](image-22.png)  
![alt text](image-23.png)

**2. Dimensión y Jerarquía de Productos:** Niveles configurados: Categoría -> Subcategoría -> Producto.  
![alt text](image-24.png)  
![alt text](image-25.png)

**3. Dimensión y Jerarquía de Geografía:** Niveles configurados: Departamento -> Municipio.  
![alt text](image-26.png)

**4. Dimensión y Jerarquía de Clientes / Segmentación:** Niveles configurados: Canal de Venta -> Segmento -> Cliente.  
![alt text](image-27.png)

### 4.4 Procesamiento del Cubo
Finalmente, se realizó el despliegue (Deploy) y procesamiento (Process Full) del proyecto de SSAS hacia el servidor de Analysis Services local, calculando las agregaciones y dejando el cubo listo para ser consultado.

**Procesar cubo (Éxito):** ![alt text](image-28.png)

---

## 5. Guía de Ejecución

Para replicar y ejecutar este flujo desde cero, siga los siguientes pasos:
1. Ejecutar el script SQL de creación de la base de datos destino (Data Warehouse) en una instancia local de SQL Server.
2. Abrir el proyecto de Integration Services (`.dtproj`), verificar las cadenas de conexión en el Connection Manager para que apunten a sus rutas y servidores locales.
3. Ejecutar el paquete principal (Control Flow) pulsando "Iniciar" (Start) en Visual Studio. Validar que todas las tareas culminen con el indicador verde.
4. Abrir el proyecto de Analysis Services (`.dwproj`).
5. Dar clic derecho sobre el proyecto en el Explorador de Soluciones y seleccionar **"Procesar"**.
6. Abrir Excel o SSMS, conectarse al servidor de Analysis Services local y explorar el cubo generado.