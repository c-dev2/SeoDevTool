from django.shortcuts import render
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup

def home(request):
    return render(request, "home.html")

def handle_form(request):
    if request.method == "GET":
        domain = request.GET.get('domain-search')
        query = request.GET.get('keyword-search')

        print(f"Received domain: {domain} and query: {query}")

        try:
            # Fetch the website content
            response = requests.get(f'http://{domain}')
            response.raise_for_status()  # Check for errors

            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()

            keyword_density, keyword_count, total_words = calculate_keyword_density(page_text, query)

            description = check_description(soup)
            img_alt = check_img_tag(soup)
            title = check_title(soup)

            # Print results
            if keyword_count > 0:
                print(f"The query '{query}' was found {keyword_count} times in {domain}.")
                print(f"Total words on page: {total_words}")
                print(f"Keyword Density: {keyword_density:.2f}%")
            else:
                print(f"The query '{query}' was NOT found in {domain}.")

        except requests.exceptions.RequestException as e:
            print(f"Error accessing {domain}: {e}")

        return render(request, 'home.html', {
            'domain': domain,
            'query': query,
            'query_count': keyword_count,
            'total_words': total_words,
            'keyword_density': keyword_density,
            'description': description,
            'img_alt': img_alt,
            'title': title
        })
    else:
        return render(request, 'home.html')



def calculate_keyword_density(page_text, keyword):
    page_text = page_text.lower()
    keyword = keyword.lower()

    #counting occurrences of the keyword and total words
    keyword_count = page_text.count(keyword)
    total_words = len(page_text.split())

    #calculating keyword density
    if total_words > 0:
        keyword_density = (keyword_count / total_words) * 100
    else:
        keyword_density = 0
    
    return keyword_density, keyword_count, total_words

def check_title(soup):
    title_tag = soup.title
    title = title_tag.string.strip() if title_tag else None
    title_check = "filled" if title else "missing"
    print(f"Title is {title_check}: {title}")
    return title_check

def check_description(soup):
    meta_description_tag = soup.find('meta', {'name': 'description'})
    meta_description = meta_description_tag['content'] if meta_description_tag else None
    meta_description_check = "filled" if meta_description else "missing"
    print(f"Meta description is {meta_description_check}: {meta_description}")
    return meta_description

def check_img_tag(soup):
    img_tags = soup.find_all('img')
    img_alt_check = "filled" if all(img.get('alt') for img in img_tags) else "missing"
    if img_alt_check == "missing":
        missing_alt_imgs = [img for img in img_tags if not img.get('alt')]
        print(f"Images without alt attributes: {len(missing_alt_imgs)}")
    return img_alt_check