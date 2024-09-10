from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from telegraph import Telegraph

from BackEnd.logger import Logger
logger = Logger()

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
    def render_node (node):
        print (node)
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

    html_parts = []
    current_part = ''
    
    for node in nodes:
        content = render_node(node)
        if len(current_part) + len(content) > max_length:
            html_parts.append(current_part)
            current_part = ''
        current_part += content

    if current_part:
        html_parts.append(current_part)
    return html_parts

def getArticleByUrl (driver: WebDriver, url: str):
    try:
        logger.logger.info (f'Started parsing url: {url}.')
        driver.get (url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
        html = driver.page_source

        title = BeautifulSoup(html, 'html.parser').find('h1', class_='Post_title_G2QHp')
        title = title.text if title else "Default Title"
        author_name = BeautifulSoup(html, 'html.parser').find('div', class_='UserCard_authorName_a8qEj')
        author_name = author_name.text if author_name else "Default Author"
        author_url = url.split('/posts')[0]

        # print (title, author_name, author_url)
        logger.logger.info (f'Got info - title: {title}, author: {author_name}, author_url: {author_url}.')

        nodes = articleToNodes(html)
        html_parts = nodesToHtml(nodes)

        logger.logger.info ('Creating telegraph instance and account.')
        telegraph = Telegraph()
        telegraph.create_account (
            short_name=author_name,
            author_name=author_name,
            author_url=author_url
        )
        url_parts = []
        for html in html_parts:
            logger.logger.info ('Creating telegraph page.')
            response = telegraph.create_page (
                title=title,
                author_name=author_name,
                author_url=author_url,
                html_content=html
            )
            url_parts.append(response['url'])
        return url_parts
    except Exception as error:
        logger.logger.error (f'Something went wrong, when getting article by Url with error: {error}')
        return None

# with open ('article.html', 'r', encoding='utf-8') as file:
#     html = file.read()

# nodes = articleToNodes(html)
# html_parts = nodesToHtml(nodes)

# telegraph = Telegraph()
# telegraph.create_account (
#     short_name='short name',
#     author_name='author name'
# )
# url_parts = []
# for html in html_parts:
#     response = telegraph.create_page (
#         title='title',
#         author_name='author name',
#         html_content=html
#     )
#     url_parts.append(response['url'])

# print (url_parts)