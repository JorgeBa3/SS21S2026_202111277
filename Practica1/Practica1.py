import pandas as pd

df = pd.read_csv('dataset_vuelos_crudo.csv')

print("Shape ", df.shape)
print()
print(df.head())


print(df.info())

columnas_texto =['status', 'cabin_class', 'passenger_gender', 'airline_name', 'sales_channel', 'currency']

for columna in columnas_texto:
    print(f"Valores únicos en la columna '{columna}':")
    print(df[columna].unique())

# Fechas

print("\nEjemplos de departure_datetime:")
print(df['departure_datetime'].head(10))

print("\nEjemplos de booking_datetime:")
print(df['booking_datetime'].head(15))


def parsear_fecha(serie):
    # Intento 1: formato DD/MM/YYYY HH:MM
    resultado = pd.to_datetime(serie, format='%d/%m/%Y %H:%M', errors='coerce')
    
    # Intento 2: donde quedó NaT, probar el otro formato
    mascara = resultado.isnull()  # ¿qué método detecta los NaT?
    resultado[mascara] = pd.to_datetime(serie[mascara], format='%m-%d-%Y %I:%M %p', errors='coerce')
    
    return resultado


df['departure_datetime'] = parsear_fecha(df['departure_datetime'])
df['arrival_datetime']   = parsear_fecha(df['arrival_datetime'])
df['booking_datetime']   = parsear_fecha(df['booking_datetime'])

# Verificar cuántos NaT quedaron después de parsear
print("\nNaT restantes por columna de fecha:")
print("departure_datetime:", df['departure_datetime'].isnull().sum())
print("arrival_datetime:  ", df['arrival_datetime'].isnull().sum())
print("booking_datetime:  ", df['booking_datetime'].isnull().sum())

# Ver tipos de dato — deben decir datetime64
print("\nTipos de dato:")
print(df[['departure_datetime','arrival_datetime','booking_datetime']].dtypes)


# -----------------------------------
print(df['ticket_price'].dtype)   # debe decir float64
print(df['ticket_price'].head())  # debe mostrar números con punto
df['ticket_price'] = pd.to_numeric(df['ticket_price'].str.replace(',', '.'), errors='coerce')

print(df['ticket_price'].dtype)   # debe decir float64
print(df['ticket_price'].head())  # debe mostrar números con punto