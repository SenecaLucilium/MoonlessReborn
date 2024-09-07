from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager

import re
from bs4 import BeautifulSoup
from telegraph import Telegraph

def processElement(element):
    if element.name == 'h1':
        return None
    if element.name == 'a':
        if element.find('img'):
            img_alt = element.find('img').get('alt', '')
            img_src = element.find('img').get('src')
            img_width = element.find('img').get('width', '')
            img_height = element.find('img').get('height', '')
            return {'tag': 'img', 'src': img_src, 'alt': img_alt, 'width': img_width, 'height': img_height}
        return None
    elif element.name == 'div':
        classes = element.get('class', [])
        if classes == []:
            return None
        elif 'BlockRenderer_markup_Wtipg' in classes:
            children = []

            for child in element.contents:
                if child.name == 'i':
                    children.append({'tag': 'text', 'text': f"<i>{child.get_text()}</i>"})
                elif child.name == 'b':
                    children.append({'tag': 'text', 'text': f"<b>{child.get_text()}</b>"})
                elif child.name == 'a':
                    href = child.get('href')
                    inner_text = ''.join(str(grandchild) for grandchild in child.contents)
                    children.append({'tag': 'a', 'href': href, 'children': [{'tag': 'text', 'text': inner_text}]})
                elif child.name is None:
                    children.append({'tag': 'text', 'text': child.strip()})
            
            if children == []:
                return {'tag': 'text', 'text': ""}
            return {'tag': 'p', 'children': children}
        elif 'BlockRenderer_audio_uJ3mS' in classes:
            audio_title = "Здесь находится аудио, которое тебе недоступно :)"
            if element.find('div', class_='AudioPlayer_title_caOU6'):
                audio_title = element.find('div', class_='AudioPlayer_title_caOU6').get_text()

            return {'tag': 's', 'children': [{'tag': 'text', 'text': audio_title}]}
        elif 'VideoBlock_root_aH2SN' in classes:
            return {'tag': 's', 'children': [{'tag': 'text', 'text': 'Здесь находится видео, которое тебе недоступно :)'}]}
        else:
            return None
    else:
        return None

def articleToNodes (html: str):
    soup = BeautifulSoup(html, 'html.parser').find('article')
    nodes = []

    for element in soup.find_all(recursive=False):
        if element.name:
            node = processElement(element)
            if node is not None:
                nodes.append(node)

    return nodes

def nodesToHtml(nodes):
    def render_node(node):
        if node['tag'] == 'p':
            return f"<p>{''.join(render_node(child) for child in node.get('children', []))}</p>"
        elif node['tag'] == 'a':
            return f"<a href='{node.get('href', '')}'>{''.join(render_node(child) for child in node.get('children', []))}</a>"
        elif node['tag'] == 's':
            return f"<s>{''.join(render_node(child) for child in node.get('children', []))}</s>"
        elif node['tag'] == 'text':
            return node.get('text', '')
        elif node['tag'] == 'img':
            src = node.get('src', '')
            alt = node.get('alt', '')
            width = node.get('width', '')
            height = node.get('height', '')
            width_attr = f" width='{width}'" if width else ''
            height_attr = f" height='{height}'" if height else ''
            return f"<img src='{src}' alt='{alt}'{width_attr}{height_attr}/>"
        else:
            return ''
    
    return ''.join(render_node(node) for node in nodes)

def getArticleByUrl (driver: WebDriver, url: str) -> str | None:
    try:
        driver.get (url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
        html = driver.page_source

        nodes = articleToNodes(html)
        html_content = nodesToHtml(nodes)

        print(html_content)

        telegraph = Telegraph()
        response = telegraph.create_page (
            title=BeautifulSoup(html, 'html.parser').find('h1', class_='Post_title_G2QHp').text,
            author_name=BeautifulSoup(html, 'html.parser').find('div', class_='UserCard_authorName_a8qEj').text,
            author_url=url.split('/posts')[0],
            html_content=html_content
        )
        return response['url']
    except Exception as error:
        print (error)
        return None