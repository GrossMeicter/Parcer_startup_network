import requests
from bs4 import BeautifulSoup
import json
import csv
import os
from time import sleep
import random

def get_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }

    offers_data_list = [] # список для предложений
    iteration_count = 13
    print(f"Всего итераций: #{iteration_count}")

    with open("data/offers_data_list.csv", "w", encoding="utf-8") as file: # создаем общий csv-файл
        writer = csv.writer(file,  delimiter=';', lineterminator='\n')
        writer.writerow(
            (
                "Название",
                "Цена продажи",
                "Идея",
                "Текущее состояние",
                "Годовой объем продаж",
                "Годовой объем чистой прибыли",
                "Финансы",
                "Причина продажи",
                "Рынок",
                "Ссылка на страницу"
            )
        )

    for item in range (1, 13): # хардкод в котором прописано жестко триннадцать страниц
        req = requests.get(url + f"/page/{item}/", headers)

        folder_name = f"data/data_{item}" #задание имен папок для каждой страницы

        if os.path.exists(folder_name):
            print("Папка уже существует")
        else:
            os.mkdir(folder_name)

        with open(f"{folder_name}/offer_{item}.html", "w", encoding="utf-8") as file: # создается файл общей страницы
            file.write(req.text)

        with open(f"{folder_name}/offer_{item}.html", encoding="utf-8") as file: # извлекаем данные из общей страницы
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        articles = soup.find_all("a", class_="projects_list_b")

        offers_urls = [] # список ссылок на предложения
        for a in articles:
            offer_url = a.get("href")
            offers_urls.append(offer_url)

        for offer_url in offers_urls: # ограничение одним запуском убрано
            req = requests.get(offer_url, headers)
            offer_link_name = offer_url.split("/")[-1]

            with open(f"{folder_name}/{offer_link_name}", "w", encoding="utf-8") as file:
                file.write(req.text)

            with open(f"{folder_name}/{offer_link_name}", encoding="utf-8") as file:
                src = file.read()

            soup = BeautifulSoup(src, "lxml")
            offer_data = soup.find("div", id="detail-content")

            try: # берем название предложения
                offer_name = offer_data.find("h1").text.strip()
            except Exception:
                offer_name = "No offer name"

            try: # берем цену продажи
                offer_sale_price = offer_data.find("span", itemprop="price").text.strip()
            except Exception:
                offer_sale_price = "No offer sale price"
            
            try: # берем идею
                offer_idea = offer_data.find("span", itemprop="description").text.strip()
            except Exception:
                offer_idea = "No offer idea"

            try: # берем текущее состояние
                offer_present_s = offer_data.find("div", id="PRESENT_S").find("div", class_="i_d").text.strip()
            except Exception:
                offer_present_s = "No offer present state"

            try: # берем годовой объем продаж
                offer_volume = offer_data.find("div", id="SALE_YEARLYVOLUME").find("div", class_="i_d").text.strip()
            except Exception:
                offer_volume = "No offer volume"

            try: # берем годовой объем чистой прибыли
                offer_profit = offer_data.find("div", id="SALE_YEARLYPROFIT").find("div", class_="i_d").text.strip()
            except Exception:
                offer_profit = "No offer profit"

            try: # берем финансы
                offer_finance = offer_data.find("div", id="FINANCE").find("div", class_="i_d").text.strip()
            except Exception:
                offer_finance = "No offer finance"

            try: # берем причина продажи
                offer_reason = offer_data.find("div", id="REASON_SALE").find("div", class_="i_d").text.strip()
            except Exception:
                offer_reason = "No offer reason"

            try: # берем рынок
                offer_market = offer_data.find("div", id="MARKET").find("div", class_="i_d").text.strip()
            except Exception:
                offer_market = "No offer market"

            offers_data_list.append(
                {
                    "Название": offer_name,
                    "Цена продажи": offer_sale_price,
                    "Идея": offer_idea,
                    "Текущее состояние": offer_present_s,
                    "Годовой объем продаж": offer_volume,
                    "Годовой объем чистой прибыли": offer_profit,
                    "Финансы": offer_finance,
                    "Причина продажи": offer_reason,
                    "Рынок": offer_market,
                    "Ссылка на страницу": offer_url
                }
            )
            
            with open("data/offers_data.json", "a", encoding="utf-8") as file: # записываем новый блок данных в общий json-файл
                json.dump(offers_data_list, file, indent=4, ensure_ascii=False)

            with open("data/offers_data_list.csv", "a", encoding="utf-8") as file: # записываем новую строку в общий csv-файл
                writer = csv.writer(file,  delimiter=';', lineterminator='\n')
                writer.writerow(
                    (
                    offer_name,
                    offer_sale_price,
                    offer_idea,
                    offer_present_s,
                    offer_volume,
                    offer_profit,
                    offer_finance,
                    offer_reason,
                    offer_market,
                    offer_url
                    )
                )

        iteration_count -= 1
        print(f"Итерация #{item} завершена, осталось еще #{iteration_count} итераций")
        if iteration_count == 0:
            print("Сбор данных завершен")
        sleep(random.randrange(2, 5))
        
get_data("https://ru.startup.network/sale/")
