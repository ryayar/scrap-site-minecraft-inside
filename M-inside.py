from bs4 import BeautifulSoup
from datetime import datetime
import os
import requests
import json


data = json

date = datetime.now().date()
url_page = 'https://minecraft-inside.ru'
int_pages_mods = range(1, 10)

headers = {
    "Accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


def deep_search(needles, haystack):
    found = {}
    if type(needles) != type([]):
        needles = [needles]

    if type(haystack) == type(dict()):
        for needle in needles:
            if needle in haystack.keys():
                found[needle] = haystack[needle]
            elif len(haystack.keys()) > 0:
                for key in haystack.keys():
                    result = deep_search(needle, haystack[key])
                    if result:
                        for k, v in result.items():
                            found[k] = v
    elif type(haystack) == type([]):
        for node in haystack:
            result = deep_search(needles, node)
            if result:
                for k, v in result.items():
                    found[k] = v
    return found


def get_all_links_on_a_page(pages):
    links = []

    for page in range(1, 2 if pages <= 1 else pages):
        req = requests.get(f'{url_page}/mods/page/{page}/', headers=headers)
        src = req.text  # Получаю текст страницы
        soup = BeautifulSoup(src, 'lxml')

        links_on_the_page = soup.find_all(class_='box box_grass post')

        for link_on_the_page in links_on_the_page:
            links.append(url_page + link_on_the_page.find('a').get('href'))

    return links


def get_data_on_mod_page(links_mods):
    mod_data = {}
    for referer in links_mods:

        req = requests.get(f'{referer}', headers=headers)
        src = req.text  # Получаю текст страницы
        soup = BeautifulSoup(src, 'lxml')

        mod_name = soup.find('h1', class_='box__title').text  # название мода с его версиями
        try:
            mod_link_logo = url_page + soup.find('div', class_="box__body").next.next.get('src')
        except:
            mod_link_logo = url_page + soup.find('div', class_="box__body").next.get('src')

        desc_and_image = soup.find('script', type="application/ld+json").next
        mod_description = deep_search(['description'], json.loads(desc_and_image))['description']
        try:
            mod_link_image = deep_search(['image'], json.loads(desc_and_image))['image']
        except:
            mod_link_image = ''

        mod_links = []
        mod_version = []
        dl__info = soup.find_all(class_='dl__info')
        for dl__ in dl__info:
            mod_links.append(dl__.find('a').get('href'))
            try:
                dl__name = dl__.find(class_='dl__name').text.split(' ')
                mod_version.append(f'[{dl__name[1].replace("/", "-")}]')
            except:
                mod_version.append(f'{mod_name[mod_name.find("["):]}')
        if not os.path.exists(f'data/{mod_name[:mod_name.find("[")]}'):
            os.mkdir(f'data/{mod_name[:mod_name.find("[")]}')

        mod_data.setdefault(mod_name, {})
        mod_data[mod_name].setdefault('referer', referer)
        mod_data[mod_name].setdefault('mod_name', mod_name)
        mod_data[mod_name].setdefault('mod_link_logo', mod_link_logo)
        mod_data[mod_name].setdefault('mod_description', mod_description)
        mod_data[mod_name].setdefault('mod_link_image', mod_link_image)
        mod_data[mod_name].setdefault('mod_links', mod_links)
        mod_data[mod_name].setdefault('mod_version', mod_version)

        with open(f'data/{mod_name[:mod_name.find("[") - 1]}/{mod_name}.txt', 'w+', encoding='UTF-8') as file:
            file.write(f'home_page_mod: {referer}\n')
            file.write(f'mod_name: {mod_name}\n')
            file.write(f'mod_description: {mod_description}\n')

    return mod_data


def get_all_mods_from_page(info):
    for key, value in info.items():
        headers.setdefault('referer', value['referer'])

        path = value["mod_name"]
        path = path[:path.find("[") - 1]

        if not os.path.exists(f'data/{path}/{path}'):
            os.mkdir(f'data/{path}/{path}')

        i = 0
        for link in value['mod_links']:
            req = requests.get(f'{link}', headers=headers)
            src = req.content

            with open(f'data/{path}/{path}/{path}_{value["mod_version"][i]}.jar', 'wb') as jar:
                jar.write(src)

            i += 1


def get_all_mods_images(info):
    for key, value in info.items():
        path = value["mod_name"]
        path = path[:path.find("[") - 1]

        if not os.path.exists(f'data/{path}/images'):
            os.mkdir(f'data/{path}/images')

        i = 0
        for link in value['mod_link_image']:
            req = requests.get(f'{link}', headers=headers)
            src = req.content

            with open(f'data/{path}/images/{path}_{i}.png', 'wb') as image:
                image.write(src)

            i += 1


def get_mods_logo(info):
    for key, value in info.items():
        path = value["mod_name"]
        path = path[:path.find("[") - 1]

        if not os.path.exists(f'data/{path}/images'):
            os.mkdir(f'data/{path}/images')

        i = 0
        req = requests.get(f'{value["mod_link_logo"]}', headers=headers)
        src = req.content

        with open(f'data/{path}/images/logo.png', 'wb') as image:
            image.write(src)

        i += 1


def main():
    if not os.path.exists(f'data'):
        os.mkdir(f'data')
    need_page = int(input('Введите необходимое количество страниц: '))
    all_links = get_all_links_on_a_page(need_page)
    all_info = get_data_on_mod_page(all_links)
    get_all_mods_from_page(all_info)
    get_all_mods_images(all_info)
    get_mods_logo(all_info)


if __name__ == '__main__':
    main()
