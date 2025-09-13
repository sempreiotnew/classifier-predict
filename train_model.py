# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.preprocessing import LabelEncoder
# import joblib

# CSV_FILE = "data.csv"
# MODEL_FILE = "gas_model.pkl"

# # Ler dados
# df = pd.read_csv(CSV_FILE)

# # Ignorar linhas com gas_index 99 ou 100 (não usadas para treino)
# df = df[~df['gas_index'].isin([99, 100])]

# # Selecionar features (valores numéricos do sensor)
# features = ['millis','gas_index','mes_index','temperature','pressure','humidity','gas_resistance']
# X = df[features]

# # Label encoding
# le = LabelEncoder()
# y = le.fit_transform(df['label'])

# # Separar treino e teste
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # Treinar modelo
# clf = RandomForestClassifier(n_estimators=100, random_state=42)
# clf.fit(X_train, y_train)

# # Avaliação
# acc = clf.score(X_test, y_test)
# print(f"Acurácia no teste: {acc*100:.2f}%")

# # Salvar modelo e encoder
# joblib.dump((clf, le), MODEL_FILE)
# print(f"Modelo salvo em: {MODEL_FILE}")


import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

MODEL_FILE = "gas_model.pkl"

def incremental_train(new_csv_files):
    """
    Atualiza o modelo RandomForest com novos arquivos CSV.
    """
    # Carregar modelo existente ou criar novo
    if os.path.exists(MODEL_FILE):
        clf, le = joblib.load(MODEL_FILE)
        print("Modelo existente carregado.")
        # Carregar histórico de dados já treinados (opcional)
        all_data = pd.DataFrame()  # você pode manter histórico em arquivo
    else:
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        le = LabelEncoder()
        all_data = pd.DataFrame()
        print("Criando novo modelo.")

    # Carregar novos arquivos CSV e concatenar
    new_dfs = []
    for csv_file in new_csv_files:
        df = pd.read_csv(csv_file)
        df = df[~df['gas_index'].isin([99, 100])]  # ignora gas_index inválido
        new_dfs.append(df)
    new_data = pd.concat(new_dfs, ignore_index=True)

    # Concatenar com dados antigos se quiser manter histórico
    if not all_data.empty:
        df_all = pd.concat([all_data, new_data], ignore_index=True)
    else:
        df_all = new_data

    # Features e labels
    features = ['millis','gas_index','mes_index','temperature','pressure','humidity','gas_resistance']
    X = df_all[features]

    # Label encoding
    y = le.fit_transform(df_all['label'])

    # Treinar modelo
    clf.fit(X, y)
    print(f"Modelo treinado com {len(df_all)} amostras.")

    # Salvar modelo atualizado
    joblib.dump((clf, le), MODEL_FILE)
    print(f"Modelo atualizado salvo em: {MODEL_FILE}")

# Exemplo de uso
if __name__ == "__main__":
    # Passe uma lista de novos arquivos CSV para treinar
    incremental_train(["natural_air3.csv", "natural_air.csv", "natural_air2.csv", "alcohol.csv", "cigarro.csv"])
