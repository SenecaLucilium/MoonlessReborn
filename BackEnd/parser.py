from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
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

def nodesToHtml(nodes, max_length=20000):
    html_parts = []
    current_part = ''

    def render_node(node):
        nonlocal current_part

        if node['tag'] == 'p':
            content = f"<p>{''.join(render_node(child) for child in node.get('children', []))}</p>"
        elif node['tag'] == 'a':
            content = f"<a href='{node.get('href', '')}'>{''.join(render_node(child) for child in node.get('children', []))}</a>"
        elif node['tag'] == 's':
            content = f"<s>{''.join(render_node(child) for child in node.get('children', []))}</s>"
        elif node['tag'] == 'text':
            content = node.get('text', '')
        elif node['tag'] == 'img':
            src = node.get('src', '')
            alt = node.get('alt', '')
            width = node.get('width', '')
            height = node.get('height', '')
            width_attr = f" width='{width}'" if width else ''
            height_attr = f" height='{height}'" if height else ''
            content = f"<img src='{src}' alt='{alt}'{width_attr}{height_attr}/>"
        else:
            content = ''
        
        if len(current_part) + len(content) > max_length:
            html_parts.append(current_part)
            current_part = ''
        current_part += content
    
    for node in nodes:
        render_node(node)
    
    if current_part:
        html_parts.append(current_part)
    return html_parts

def getArticleByUrl (driver: WebDriver, url: str):
    try:
        driver.get (url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
        html = driver.page_source

        nodes = articleToNodes(html)
        html_parts = nodesToHtml(nodes)

        print (html_parts)

        telegraph = Telegraph()
        url_parts = []
        for html in html_parts:
            response = telegraph.create_page (
                title=BeautifulSoup(html, 'html.parser').find('h1', class_='Post_title_G2QHp').text,
                author_name=BeautifulSoup(html, 'html.parser').find('div', class_='UserCard_authorName_a8qEj').text,
                author_url=url.split('/posts')[0],
                html_content=html
            )
            url_parts.append(response['url'])
        
        return url_parts
    except Exception as error:
        print (error)
        return None