USE vuelos_db;

-- 1. Total de vuelos por estado
SELECT status, COUNT(*) AS total_vuelos
FROM FACT_Vuelo
GROUP BY status
ORDER BY total_vuelos DESC;

-- 2. Top 5 destinos más frecuentes
SELECT TOP 5 destination_airport, COUNT(*) AS total_vuelos
FROM FACT_Vuelo
GROUP BY destination_airport
ORDER BY total_vuelos DESC;

-- 3. Top 5 aerolíneas con más vuelos
SELECT TOP 5 a.airline_name, COUNT(*) AS total_vuelos
FROM FACT_Vuelo f
JOIN DIM_Aerolinea a ON f.airline_code = a.airline_code
GROUP BY a.airline_name
ORDER BY total_vuelos DESC;

-- 4. Distribución por género de pasajero
SELECT p.passenger_gender, COUNT(*) AS total
FROM FACT_Vuelo f
JOIN DIM_Pasajero p ON f.passenger_id = p.passenger_id
GROUP BY p.passenger_gender
ORDER BY total DESC;

-- 5. Promedio de delay por aerolínea (solo vuelos retrasados)
SELECT a.airline_name, AVG(f.delay_min) AS promedio_delay
FROM FACT_Vuelo f
JOIN DIM_Aerolinea a ON f.airline_code = a.airline_code
WHERE f.status = 'DELAYED'
GROUP BY a.airline_name
ORDER BY promedio_delay DESC;

-- 6. Ingresos totales por aerolínea
SELECT a.airline_name, ROUND(SUM(f.ticket_price_usd_est), 2) AS ingresos_usd
FROM FACT_Vuelo f
JOIN DIM_Aerolinea a ON f.airline_code = a.airline_code
GROUP BY a.airline_name
ORDER BY ingresos_usd DESC;

-- 7. Vuelos por mes
SELECT t.anio, t.mes, COUNT(*) AS total_vuelos
FROM FACT_Vuelo f
JOIN DIM_Tiempo t ON f.departure_datetime = t.fecha_completa
GROUP BY t.anio, t.mes
ORDER BY t.anio, t.mes;

-- 8. Canal de venta más usado
SELECT sales_channel, COUNT(*) AS total
FROM FACT_Vuelo
GROUP BY sales_channel
ORDER BY total DESC;

-- 9. Clase de cabina más vendida
SELECT cabin_class, COUNT(*) AS total
FROM FACT_Vuelo
GROUP BY cabin_class
ORDER BY total DESC;

-- 10. Ruta más frecuente (origen - destino)
SELECT TOP 5
    origin_airport + ' -> ' + destination_airport AS ruta,
    COUNT(*) AS total_vuelos
FROM FACT_Vuelo
GROUP BY origin_airport, destination_airport
ORDER BY total_vuelos DESC;