import requests, time

API_KEY = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MDg3MjQzODAsImlhdCI6MTc3NzE4ODM4MCwicmF5IjoiZjJiODgyMDUwMmMxODhjNGRhZjA2NjZjMDI3NWViMjQiLCJzdWIiOjQwMDI1OTd9.xA3wO_aBiA32jUqu7uS7CUptxmBxwsYnTYiCB3oWilk-yz66hBfCmsrASwKoqb6dSEBFJ96AUwTr39lFm4FdidsGgLllwaWaWdK8ySre5vrA8DoI7kblwdWY_SixhQIBoZdF5QpTsK8m9a1G2mx7z0-nebJyIbSxAxqEQW5ndAL9axfXW3ye8t5R2efDlIz99EENifX0t5zVgSgvxDeQcZ6ljuH5XSyctEqAIc-iJXLUYYaqTI60Ig2XACmg12SFiDHiUCT6czi_TG6oh7uWiuv3vWk6QabR_BGZ2taA7AVG3vcQ6_udEG0RQ84z0s1qZ9pnB_aXPJLkQTWJeTvXJA"   # troque pela chave real

def pegar_numero():
    url = "https://5sim.net/v1/user/buy/activation/brazil/virtual61/99app"
    headers = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200 or not resp.text.strip():
        raise Exception(f"Falha na API: {resp.text}")
    data = resp.json()
    if data.get("status") != "ok":
        raise Exception(data.get("message", "Erro desconhecido"))
    return data["id"], data["phone"]

aid, number = pegar_numero()
print(f"\nNúmero: {number}")
input("Abra o app 99Food, cadastre com esse número e solicite o SMS. Depois pressione Enter...")

url_check = f"https://5sim.net/v1/user/check/{aid}"
headers = {"Authorization": f"Bearer {API_KEY}"}
codigo = None
for _ in range(15):
    time.sleep(10)
    resp = requests.get(url_check, headers=headers).json()
    if resp.get("status") == "ok" and resp.get("sms"):
        codigo = resp["sms"][0]["code"]
        break

if codigo:
    print(f"Código: {codigo}")
else:
    print("Código não encontrado.")