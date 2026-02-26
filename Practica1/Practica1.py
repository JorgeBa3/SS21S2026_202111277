import pandas as pd

# =============================================================
# FASE 1: EXTRACCION
# =============================================================

df = pd.read_csv('dataset_vuelos_crudo.csv')

print("Shape:", df.shape)
print(df.info())
print(df.isnull().sum())


# =============================================================
# FASE 2: TRANSFORMACION
# =============================================================

# --- FECHAS ---
# El dataset tiene dos formatos mezclados:
#   Formato A: DD/MM/YYYY HH:MM       (ej: 20/01/2024 10:14)
#   Formato B: MM-DD-YYYY HH:MM AM/PM (ej: 03-15-2025 01:58 PM)
# Se intenta primero con formato A; donde queda NaT se intenta con formato B.

def parsear_fecha(serie):
    resultado = pd.to_datetime(serie, format='%d/%m/%Y %H:%M', errors='coerce')
    mascara = resultado.isnull()
    resultado[mascara] = pd.to_datetime(serie[mascara], format='%m-%d-%Y %I:%M %p', errors='coerce')
    return resultado

df['departure_datetime'] = parsear_fecha(df['departure_datetime'])
df['arrival_datetime']   = parsear_fecha(df['arrival_datetime'])
df['booking_datetime']   = parsear_fecha(df['booking_datetime'])

print("\nNaT por columna de fecha:")
print("departure_datetime:", df['departure_datetime'].isnull().sum())
print("arrival_datetime:  ", df['arrival_datetime'].isnull().sum())  # 560 = vuelos cancelados, esperado
print("booking_datetime:  ", df['booking_datetime'].isnull().sum())


# --- TICKET PRICE ---
# Algunos valores usan coma como separador decimal (ej: 77,60)
# Se reemplaza la coma y se convierte a float

df['ticket_price'] = pd.to_numeric(df['ticket_price'].str.replace(',', '.'), errors='coerce')


# --- TEXTO: AEROLINEAS Y AEROPUERTOS ---
# Hay inconsistencias de mayusculas/minusculas (Ryanair vs RYANAIR, jfk vs JFK)
# Se estandariza todo a mayusculas

df['airline_name']          = df['airline_name'].str.upper().str.strip()
df['origin_airport']        = df['origin_airport'].str.upper().str.strip()
df['destination_airport']   = df['destination_airport'].str.upper().str.strip()


# --- PASSENGER GENDER ---
# 12 variantes distintas: M, m, Masculino, masculino, F, f, Femenino, femenino,
#                         X, x, NoBinario, nobinario
# Se mapean a 3 valores estandar: M, F, X

mapa_genero = {
    'M': 'M', 'm': 'M', 'Masculino': 'M', 'masculino': 'M',
    'F': 'F', 'f': 'F', 'Femenino': 'F', 'femenino': 'F',
    'X': 'X', 'x': 'X', 'NoBinario': 'X', 'nobinario': 'X'
}

df['passenger_gender'] = df['passenger_gender'].map(mapa_genero)


# --- NULOS ---
# arrival_datetime, duration_min, delay_min, seat: 560 nulos
#   -> Son vuelos CANCELADOS (status == CANCELLED), se conservan como NaN (logicamente correcto)
#
# passenger_age (112 nulos): se rellena con la mediana
# passenger_nationality (209 nulos): se rellena con 'DESCONOCIDO'
# sales_channel (144 nulos): se rellena con 'DESCONOCIDO'

df['passenger_age']          = df['passenger_age'].fillna(df['passenger_age'].median())
df['passenger_nationality']  = df['passenger_nationality'].fillna('DESCONOCIDO')
df['sales_channel']          = df['sales_channel'].fillna('DESCONOCIDO')


# --- VERIFICACION FINAL ---
print("\n=== VERIFICACION POST-TRANSFORMACION ===")
print("Nulos restantes:")
print(df.isnull().sum())
print("\nTipos de dato:")
print(df.dtypes)
print("\nValores unicos passenger_gender:", df['passenger_gender'].unique())
print("Valores unicos airline_name:", df['airline_name'].unique())
print("ticket_price dtype:", df['ticket_price'].dtype)


# =============================================================
# FASE 3: CARGA
# =============================================================
from sqlalchemy import create_engine, text

SERVER   = 'ALEJANDRO\\MSSQLSERVER01'
DATABASE = 'vuelos_db'
DRIVER   = 'ODBC Driver 17 for SQL Server'

engine = create_engine(
    f'mssql+pyodbc://{SERVER}/{DATABASE}?driver={DRIVER}&trusted_connection=yes&TrustServerCertificate=yes'
)
with engine.connect() as conn:
    conn.execute(text("TRUNCATE TABLE FACT_Vuelo"))
    conn.execute(text("TRUNCATE TABLE DIM_Tiempo"))
    conn.execute(text("TRUNCATE TABLE DIM_Pasajero"))
    conn.execute(text("TRUNCATE TABLE DIM_Aeropuerto"))
    conn.execute(text("TRUNCATE TABLE DIM_Aerolinea"))
    conn.commit()
# --- DIMENSIONES ---
dim_aerolinea = df[['airline_code','airline_name']].drop_duplicates().reset_index(drop=True)
dim_aerolinea.index += 1
dim_aerolinea.index.name = 'id_aerolinea'

dim_aeropuerto = pd.DataFrame(
    pd.concat([df['origin_airport'], df['destination_airport']]).unique(),
    columns=['codigo_iata']
)
dim_aeropuerto.index += 1
dim_aeropuerto.index.name = 'id_aeropuerto'

dim_pasajero = df[['passenger_id','passenger_gender','passenger_age','passenger_nationality']].drop_duplicates().reset_index(drop=True)
dim_pasajero.index += 1
dim_pasajero.index.name = 'id_pasajero'

dim_tiempo = df[['departure_datetime']].drop_duplicates().copy()
dim_tiempo['anio'] = dim_tiempo['departure_datetime'].dt.year
dim_tiempo['mes']  = dim_tiempo['departure_datetime'].dt.month
dim_tiempo['dia']  = dim_tiempo['departure_datetime'].dt.day
dim_tiempo['hora'] = dim_tiempo['departure_datetime'].dt.hour
dim_tiempo = dim_tiempo.rename(columns={'departure_datetime':'fecha_completa'}).reset_index(drop=True)
dim_tiempo.index += 1
dim_tiempo.index.name = 'id_tiempo'

# --- FACT ---
fact_vuelo = df[[
    'record_id','flight_number','airline_code',
    'origin_airport','destination_airport',
    'departure_datetime','arrival_datetime','duration_min',
    'status','delay_min','aircraft_type','cabin_class','seat',
    'passenger_id','booking_datetime','sales_channel',
    'payment_method','ticket_price','currency',
    'ticket_price_usd_est','bags_total','bags_checked'
]].copy()

# --- CARGA ---
# index=False en todas las dimensiones para no enviar el id
dim_aerolinea.to_sql('DIM_Aerolinea',   engine, if_exists='append', index=False)
dim_aeropuerto.to_sql('DIM_Aeropuerto', engine, if_exists='append', index=False)
dim_pasajero.to_sql('DIM_Pasajero',     engine, if_exists='append', index=False)
dim_tiempo.to_sql('DIM_Tiempo',         engine, if_exists='append', index=False)
fact_vuelo.to_sql('FACT_Vuelo',         engine, if_exists='append', index=False)
print("Carga completada.")