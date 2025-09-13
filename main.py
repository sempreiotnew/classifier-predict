import serial
import csv
import threading
import sys

SERIAL_PORT = "/dev/cu.usbserial-0001"
BAUDRATE = 115200
CSV_FILE = "data.csv"

current_label = None
header = None
start_recording = False

def serial_reader():
    global current_label, header, start_recording
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)

    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)

        while True:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue

                # Detecta header
                if not start_recording and line.startswith("id,index"):
                    header = line.split(",")
                    header.append("label")
                    writer.writerow(header)
                    f.flush()
                    start_recording = True
                    print("Header detectado, iniciando gravação...")
                    continue  # pular a linha do header

                # Processa linhas de dados apenas após header
                if start_recording:
                    parts = line.split(",")
                    if len(parts) != len(header) - 1:
                        continue

                    try:
                        gas_index = int(parts[3])
                    except ValueError:
                        continue  # ignora linhas inválidas

                    if gas_index in [99, 100]:
                        continue

                    parts.append(current_label)
                    writer.writerow(parts)
                    f.flush()
                    print(parts)

            except Exception as e:
                print("Erro processando linha:", line, e)

def label_changer():
    global current_label
    while True:
        try:
            new_label = input("\nDigite a nova label e pressione Enter: ").strip()
            if new_label:
                current_label = new_label
                print(f"Label atual alterada para: {current_label}")
        except KeyboardInterrupt:
            print("\nPrograma interrompido pelo usuário (Ctrl+C).")
            sys.exit(0)

if __name__ == "__main__":
    current_label = input("Digite a label inicial: ").strip()
    print(f"Label inicial: {current_label}")
    print("Aguardando header da serial para iniciar gravação...")

    t = threading.Thread(target=serial_reader, daemon=True)
    t.start()

    label_changer()
