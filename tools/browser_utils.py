from bs4 import BeautifulSoup, Comment
import re

def clean_html(html_content):
    """
    HTML simplification strategy per paper Section 3.3.
    Removes unnecessary tags to reduce token count while preserving critical structure.
    """
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    tags_to_remove = ['script', 'style', 'svg', 'img', 'video', 'iframe', 'meta', 'link', 
                      'noscript', 'embed', 'object', 'audio', 'source', 'track', 'canvas']
    for tag in soup(tags_to_remove):
        tag.decompose()
    
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    for element in soup.find_all(string=True):
        if element.parent.name not in ['script', 'style']:
            element.replace_with(re.sub(r'\s+', ' ', element.strip()))
    
    # keep key structure: forms, inputs, buttons, links, IDs, classes
    if soup.body:
        for form in soup.find_all('form'):
            pass
        
        for input_elem in soup.find_all(['input', 'textarea', 'select']):
            pass
        
        for link in soup.find_all(['a', 'button']):
            pass
        
        return str(soup.body)
    else:
        return str(soup)