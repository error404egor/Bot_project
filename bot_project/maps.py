import requests


geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"


def get_ll_spn(address):
    print(address)
    user_request = address
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": user_request,
        "format": "json"}
    response = requests.get(geocoder_api_server, params=geocoder_params)
    if not response:
        raise ConnectionError  # вывести ошибку пдключения
    json_response = response.json()
    try:
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        left_down = tuple(map(float, toponym["boundedBy"]["Envelope"]["lowerCorner"].split(" ")))
        right_up = tuple(map(float, toponym["boundedBy"]["Envelope"]["upperCorner"].split(" ")))
        ll = ((left_down[0] + right_up[0]) / 2, (left_down[1] + right_up[1]) / 2)
        spn = (right_up[0] - left_down[0], right_up[1] - left_down[1])
        return ll, spn
    except IndexError:
        raise FileNotFoundError  # вывести ошибку ненахождения объекта


def get_address_photo(ll, spn):
    ll = ','.join(tuple(map(str, ll)))
    spn = ','.join(tuple(map(str, spn)))
    pt = ll + ",org"
    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&pt={pt}&l=map"
    return static_api_request

