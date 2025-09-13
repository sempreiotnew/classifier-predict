import serial
import pandas as pd
import joblib

SERIAL_PORT = "/dev/cu.usbserial-0001"
BAUDRATE = 115200
MODEL_FILE = "gas_model.pkl"

# Carregar modelo treinado
clf, le = joblib.load(MODEL_FILE)

# Função para predizer label de um dado
def predict_label(data_dict):
    df = pd.DataFrame([data_dict])
    pred_encoded = clf.predict(df)
    pred_label = le.inverse_transform(pred_encoded)
    return pred_label[0]

# Abrir serial
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)

header = None
start_recording = False

print("Aguardando header da serial para iniciar predição...")

try:
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            continue

        # Detecta header
        if not start_recording and line.startswith("id,index"):
            header = line.split(",")
            start_recording = True
            print("Header detectado, iniciando predição...")
            continue

        # Processa linhas de dados
        if start_recording:
            parts = line.split(",")
            if len(parts) < len(header):
                continue  # ignora linhas incompletas

            # Monta dicionário com as features usadas no treino
            try:
                gas_index = int(parts[3])
                if gas_index in [99, 100]:
                    continue  # ignora índices inválidos

                data_dict = {
                    'millis': float(parts[2]),
                    'gas_index': gas_index,
                    'mes_index': int(parts[4]),
                    'temperature': float(parts[5]),
                    'pressure': float(parts[6]),
                    'humidity': float(parts[7]),
                    'gas_resistance': float(parts[8])
                }
            except ValueError:
                continue  # ignora linhas inválidas

            # Predição
            label_pred = predict_label(data_dict)
            print(f"Dado: {data_dict} → Predição: {label_pred}")

except KeyboardInterrupt:
    print("\nPrograma interrompido pelo usuário.")
    ser.close()
