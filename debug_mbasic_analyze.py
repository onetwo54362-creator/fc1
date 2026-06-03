from bs4 import BeautifulSoup
import re

with open("mbasic_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# In mbasic, comments usually have an id that contains the comment ID
comments = soup.find_all('div', id=re.compile(r'^\d+$'))
if not comments:
    comments = soup.find_all('div', id=re.compile(r'^c_'))

print(f"Found {len(comments)} comment divs!")

for i, c in enumerate(comments[:3]):
    # Author is usually in an <h3> or <a>
    author_a = c.find('a')
    author = author_a.text if author_a else "Unknown"
    
    # Body is usually a <div> containing the text
    body = c.get_text(separator=' | ', strip=True)
    print(f"Comment {i+1}: {author} - {body}")

# Check for a "View next comments" or "View previous comments" link
nav_links = soup.find_all('a', href=re.compile(r'p=\d+'))
print(f"\nPagination links found: {len(nav_links)}")
for n in nav_links:
    print(f"  {n.text}: {n['href']}")
