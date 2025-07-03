import requests
import json
import re
from tqdm import tqdm

def reserve_copy (breed, yad_token):

    url_all = "https://dog.ceo/api/breeds/list/all"
    url_upload = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    url_create = "https://cloud-api.yandex.net/v1/disk/resources"

    headers = {
                "Authorization": f"OAuth {yad_token}"
            }

    delimiters = r"[_/#|]"

    response = requests.get(url_all)

    data = response.json()


    params = {
                "path": f"{breed}",
            }

    response_upl = requests.put(url_create, headers=headers, params=params)

    print(f"Создаем папку {breed}")

    results_all = []
    if breed in data["message"]:
        if data["message"][breed]:
            for sub_breed in tqdm(data["message"][breed],
                                  desc="Загрузка под-пород"):
                url_sub_breed = f"https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random"
                response_sub_breed = requests.get(url_sub_breed)
                image = response_sub_breed.json()['message']
                name_url_sub_breed = re.split(delimiters, image)[-1]
                name_sub_breed = breed + "_" + sub_breed + "_" + name_url_sub_breed
                params_upload = {
                    "path": f"{breed}/{name_sub_breed}",
                    "url": image
                }
                response_upload = requests.post(url_upload,
                                                headers=headers,
                                                params=params_upload)

                if 200 <= response_upload.status_code < 300:
                    print(f"Подпорода {sub_breed} загружена")
                    results_all.append({"file_name": name_sub_breed})
        else:
            url_breed = f"https://dog.ceo/api/breed/{breed}/images/random"
            response = requests.get(url_breed)
            image_breed = response.json()['message']
            name_url_breed = re.split(delimiters, image_breed)[-1]

            name = breed + "_" + name_url_breed
            params_upload = {
                        "path": f"{breed}/{name}",
                        "url": image_breed
                    }
            response_upload = requests.post(url_upload,
                                            headers=headers,
                                            params=params_upload)

            if 200 <= response_upload.status_code < 300:
                print(f"Фотография породы {breed} загружена")
                results_all.append({"file_name": name})
    else:
        print("Такой породы нет.")

    results_all_finall = results_all
    json_str = json.dumps(results_all_finall, indent=2)

    params = {
                "path": f"{breed}/results.json",
                "overwrite": "true"
            }

    response_upl_result = requests.get(url_upload,
                                 headers=headers,
                                 params=params)

    response_upl_result_link = response_upl_result.json()['href']

    requests.put(
        response_upl_result_link,
        data=json_str.encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    print(results_all_finall)
    return results_all_finall




if __name__ == "__main__":
    breed_input = input("Введите название породы: ")
    yad_token_input = input("Введите OAuth токен Яндекс.Диска: ")
    reserve_copy(breed_input, yad_token_input)