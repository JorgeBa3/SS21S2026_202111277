USE vuelos_db;
GO

-- =============================================================
-- DIMENSIONES
-- =============================================================

CREATE TABLE DIM_Aerolinea (
    id_aerolinea    INT IDENTITY(1,1) PRIMARY KEY,
    airline_code    VARCHAR(10)  NOT NULL,
    airline_name    VARCHAR(100) NOT NULL
);

CREATE TABLE DIM_Aeropuerto (
    id_aeropuerto   INT IDENTITY(1,1) PRIMARY KEY,
    codigo_iata     VARCHAR(10)  NOT NULL
);

CREATE TABLE DIM_Pasajero (
    id_pasajero             INT IDENTITY(1,1) PRIMARY KEY,
    passenger_id            VARCHAR(50)  NOT NULL,
    passenger_gender        VARCHAR(10),
    passenger_age           FLOAT,
    passenger_nationality   VARCHAR(10)
);

CREATE TABLE DIM_Tiempo (
    id_tiempo           INT IDENTITY(1,1) PRIMARY KEY,
    fecha_completa      DATETIME,
    anio                INT,
    mes                 INT,
    dia                 INT,
    hora                INT
);

-- =============================================================
-- TABLA DE HECHOS
-- =============================================================

CREATE TABLE FACT_Vuelo (
    id_vuelo                INT IDENTITY(1,1) PRIMARY KEY,
    record_id               INT,
    flight_number           VARCHAR(20),
    id_aerolinea            INT FOREIGN KEY REFERENCES DIM_Aerolinea(id_aerolinea),
    id_origen               INT FOREIGN KEY REFERENCES DIM_Aeropuerto(id_aeropuerto),
    id_destino              INT FOREIGN KEY REFERENCES DIM_Aeropuerto(id_aeropuerto),
    id_tiempo_salida        INT FOREIGN KEY REFERENCES DIM_Tiempo(id_tiempo),
    id_pasajero             INT FOREIGN KEY REFERENCES DIM_Pasajero(id_pasajero),
    arrival_datetime        DATETIME,
    duration_min            FLOAT,
    status                  VARCHAR(20),
    delay_min               FLOAT,
    aircraft_type           VARCHAR(20),
    cabin_class             VARCHAR(20),
    seat                    VARCHAR(10),
    booking_datetime        DATETIME,
    sales_channel           VARCHAR(20),
    payment_method          VARCHAR(20),
    ticket_price            FLOAT,
    currency                VARCHAR(10),
    ticket_price_usd_est    FLOAT,
    bags_total              INT,
    bags_checked            INT
);
GO

USE vuelos_db;
ALTER TABLE DIM_Pasajero ALTER COLUMN passenger_nationality VARCHAR(50);
ALTER TABLE DIM_Pasajero ALTER COLUMN passenger_id VARCHAR(50);


USE vuelos_db;
DROP TABLE FACT_Vuelo;

CREATE TABLE FACT_Vuelo (
    id_vuelo                INT IDENTITY(1,1) PRIMARY KEY,
    record_id               INT,
    flight_number           VARCHAR(20),
    airline_code            VARCHAR(10),
    origin_airport          VARCHAR(10),
    destination_airport     VARCHAR(10),
    departure_datetime      DATETIME,
    arrival_datetime        DATETIME,
    duration_min            FLOAT,
    status                  VARCHAR(20),
    delay_min               FLOAT,
    aircraft_type           VARCHAR(20),
    cabin_class             VARCHAR(20),
    seat                    VARCHAR(10),
    passenger_id            VARCHAR(50),
    booking_datetime        DATETIME,
    sales_channel           VARCHAR(20),
    payment_method          VARCHAR(20),
    ticket_price            FLOAT,
    currency                VARCHAR(10),
    ticket_price_usd_est    FLOAT,
    bags_total              INT,
    bags_checked            INT
);


USE vuelos_db;

SELECT 'DIM_Aerolinea'  AS tabla, COUNT(*) AS registros FROM DIM_Aerolinea
UNION ALL
SELECT 'DIM_Aeropuerto', COUNT(*) FROM DIM_Aeropuerto
UNION ALL
SELECT 'DIM_Pasajero',   COUNT(*) FROM DIM_Pasajero
UNION ALL
SELECT 'DIM_Tiempo',     COUNT(*) FROM DIM_Tiempo
UNION ALL
SELECT 'FACT_Vuelo',     COUNT(*) FROM FACT_Vuelo;

TRUNCATE TABLE FACT_Vuelo;
TRUNCATE TABLE DIM_Aerolinea;
TRUNCATE TABLE DIM_Aeropuerto;
TRUNCATE TABLE DIM_Pasajero;
TRUNCATE TABLE DIM_Tiempo;