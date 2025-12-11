import requests
import pandas as pd
import time

# ------------------------------
# LISTA DE CNPJs DIRETAMENTE NO CÓDIGO
# ------------------------------

cnpjs = [
    "07240743000188",
    "50720828000192",
    "48723736000114",
    "23376802000104",
    "37376047000164",
    "48949833000120",
    "21398968000198",
    "33713977000105"
]

OUTPUT_FILE = "leads_madureira.csv"
API_URL = "https://api.cnpja.com.br/companies/"  # API pública gratuita

# ------------------------------
# FUNÇÃO PARA CONSULTAR API
# ------------------------------

def consulta_cnpj(cnpj):
    try:
        url = f"{API_URL}{cnpj}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        return response.json()
    except:
        return None

# ------------------------------
# PROCESSAMENTO
# ------------------------------

resultados = []

print(f"Consultando {len(cnpjs)} CNPJs...\n")

for cnpj in cnpjs:
    print(f"🔎 Consultando {cnpj}...")
    dados = consulta_cnpj(cnpj)

    if not dados or "address" not in dados:
        print("   ⚠️ Dados não encontrados.")
        continue

    endereco = dados.get("address", {})
    situacao = dados.get("status", "").lower()

    # FILTRO: MADUREIRA + ATIVA
    if (
        endereco.get("neighborhood", "").lower() == "madureira" and
        endereco.get("city", "").lower() == "rio de janeiro" and
        "ativa" in situacao
    ):
        # TELEFONES
        telefones = []
        if "phones" in dados and isinstance(dados["phones"], list):
            for tel in dados["phones"]:
                numero = tel.get("number")
                if numero:
                    telefones.append(numero)

        # E-MAILS
        emails = []
        if "emails" in dados and isinstance(dados["emails"], list):
            for em in dados["emails"]:
                e = em.get("address")
                if e:
                    emails.append(e)

        # SÓCIOS
        socios = []
        if "partners" in dados and isinstance(dados["partners"], list):
            for s in dados["partners"]:
                nome = s.get("name")
                qualificacao = s.get("role")
                if nome:
                    socios.append(f"{nome} ({qualificacao})" if qualificacao else nome)

        resultados.append({
            "CNPJ": cnpj,
            "Razão Social": dados.get("name", ""),
            "Nome Fantasia": dados.get("alias", ""),
            "Bairro": endereco.get("neighborhood", ""),
            "Endereço": f"{endereco.get('street', '')}, {endereco.get('number', '')}",
            "CEP": endereco.get("zip", ""),
            "Situação": dados.get("status", ""),
            "CNAE Principal": dados.get("mainActivity", {}).get("text", ""),
            "Telefones": ", ".join(telefones),
            "Emails": ", ".join(emails),
            "Sócios": "; ".join(socios)
        })

    time.sleep(1)  # evita bloqueio da API

# ------------------------------
# EXPORTAÇÃO PARA CSV
# ------------------------------

df = pd.DataFrame(resultados)
df.to_csv(OUTPUT_FILE, index=False, sep=";")

print("\n✅ FINALIZADO!")
print(f"Arquivo gerado: {OUTPUT_FILE}")
print(f"Total de empresas filtradas: {len(df)}")
