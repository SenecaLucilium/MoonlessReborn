from datetime import datetime
from bs4 import BeautifulSoup
from telegraph import Telegraph
from BackEnd.articleObject import Article
from BackEnd.logger import ParserLogger
LOGGER = ParserLogger()

def processElement(element):
    try:
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
    except Exception as error:
        LOGGER.error (f'Something went wrong while processing element: {element} with error: {error}')
        return None

def articleToNodes (html: str):
    try:
        soup = BeautifulSoup(html, 'html.parser').find('article')
        nodes = []

        for element in soup.find_all(recursive=False):
            if element.name:
                node = processElement(element)
                if node is not None:
                    nodes.append(node)

        return nodes
    except Exception as error:
        LOGGER.error (f'Something went wrong while articleToNodes with error: {error}')
        return None

def nodesToHtml(nodes, max_length=20000):
    try:
        def render_node (node):
            try:
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
            except Exception as error:
                LOGGER.error (f'Something went wrong while rendering node: {node} with error: {error}')
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
    except Exception as error:
        LOGGER.error (f'Something went wring while nodesToHtml with error: {error}')
        return None

def getArticleByHtml (html: str, url: str) -> Article:
    try:
        LOGGER.info (f'Parsing Article {url}...')
        soup = BeautifulSoup (html, 'html.parser')

        name = soup.find('h1', class_='Post_title_G2QHp').text
        authorName = soup.find('div', class_='UserCard_authorName_a8qEj').text
        authorURL = url.split('/posts')[0]

        creationDate = soup.find('span', attrs={"class": ["Link_block_f6iQc", "CreatedAt_headerLink_CEfWB"]}).text

        try:
            creationDate = int(datetime.strptime(creationDate, "%b %d %Y %H:%M").timestamp())
        except ValueError:
            creationDate += " 2024"
            creationDate = int(datetime.strptime(creationDate, "%b %d %H:%M %Y").timestamp())
        
        # Где-то тут добавить теги

        LOGGER.info (f'Got info - name: {name}, authorName: {authorName}, authorURL: {authorURL}, creationDate: {creationDate}.')

        nodes = articleToNodes(html)
        html_parts = nodesToHtml(nodes)

        LOGGER.info ('Creating telegraph instance and account.')

        telegraph = Telegraph()
        telegraph.create_account (
            short_name=authorName,
            author_name=authorName,
            author_url=authorURL
        )
        url_parts = []
        for html in html_parts:
            LOGGER.info ('Creating telegraph page.')
            response = telegraph.create_page (
                title=name,
                author_name=authorName,
                author_url=authorURL,
                html_content=html
            )
            url_parts.append(response['url'])
        
        return Article(name, authorName, authorURL, url, creationDate, url_parts)
    except Exception as error:
        LOGGER.error (f'Something went wrong, when getting article by HTML with error: {error}')
        return None