from geopy.distance import geodesic
import requests
import json

promien_kola = 100 # 100 m
domyslna_predkosc = 40 # prędkość wyrażona w km/h

'''
Klucz - ograniczenie prędkości na danym obszarze
Wartość - promień obszaru, wspólrzędna N-S, współrzędna W-E  
'''
paris = {
    50: (48.8584, 2.2945),  # Wieża Eiffla
    30: (48.8600, 2.2960),  # W pobliżu Wieży Eiffla
    40: (48.8520, 2.3500),  # Katedra Notre-Dame
    50: (48.8615, 2.3370),  # Luwr
    30: (48.8745, 2.2955),  # Łuk Triumfalny
    60: (48.8875, 2.3438),  # Bazylika Sacré-Cœur
    70: (48.8935, 2.2370),  # La Défense
    20: (48.8665, 2.3220),  # Plac de la Concorde
    50: (48.8000, 2.2717)   # Punkt w pobliżu (48.82, 2.29)
}

def czy_punkt_w_kole(srodek, promien, punkt):
    """
    Sprawdza, czy dany punkt znajduje się w obrębie koła o określonym środku i promieniu.

    :param srodek: Krotka (szerokość, długość) środka koła
    :param promien: Promień koła w metrach
    :param punkt: Krotka (szerokość, długość) sprawdzanego punktu
    :return: True, jeśli punkt znajduje się w kole, False w przeciwnym razie
    """
    odleglosc = geodesic(srodek, punkt).m
    return odleglosc <= promien


def get_access_token(client_id, client_secret, scope):
    token_url = 'https://api.orange.com/oauth/v3/token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope
    }
    response = requests.post(token_url, data=payload)
    response_data = response.json()
    access_token = response_data.get('access_token')
    return response_data['access_token']

def call_api(access_token):
    api_url = 'https://api.orange.com/camara/orange-lab/location-retrieval/v0.3/retrieve'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {
        "device": {
            "phoneNumber": "+33699901032"
        },
        "maxAge": 6000
    }
    response = requests.post(api_url, headers=headers, json=data)
    return response.json()


client_id = ''
client_secret = ''
scope = ""


access_token = get_access_token(client_id, client_secret, scope)


def parsuj_json(json_dane):
    """
    Parsuje dane JSON i wyciąga współrzędne latitude oraz longitude.

    :param json_dane: Sformatowany string JSON zawierający dane lokalizacji
    :return: Krotka (latitude, longitude)
    """
    dane = json.loads(json_dane)
    latitude = dane["area"]["center"]["latitude"]
    longitude = dane["area"]["center"]["longitude"]
    #print("latitude:", latitude," ", type(latitude), "\n")
    #print("longitude:", longitude, "\n")
    return latitude, longitude


api_response = json.dumps(call_api(access_token), indent=4)
parsuj_json(api_response)
print(parsuj_json(api_response))
punkt_z_api = parsuj_json(api_response)


def znajdz_obszar_dla_punktu(punkt):
    """
    Sprawdza, czy dany punkt należy do jednego z obszarów w słowniku.
    Jeśli tak, wypisuje klucz obszaru.

    :param punkt: Krotka (szerokość, długość) sprawdzanego punktu
    """
    for speed, srodek in paris.items():
        if czy_punkt_w_kole(srodek, promien_kola, punkt):
            print(f"Nadana prędkość {speed}km/h")
            return speed
    print("Zostaje nadana domyslna prędkość 40km/h.")
    return domyslna_predkosc



znajdz_obszar_dla_punktu(punkt_z_api)

# Przykładowe użycie:
#srodek_kola = (48.8000, 2.2717)  # Warszawa
#promien_kola = 100  # 10 km
#unkt_testowy = (48.8, 2.271)  # Punkt w pobliżu

#wynik = czy_punkt_w_kole(srodek_kola, promien_kola, punkt_testowy)
#print("Czy punkt jest w kole?", wynik)