from django.shortcuts import render
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
import time

def home(request):
    return render(request, "home.html")

def handle_form(request):
    if request.method == "GET":
        domain = request.GET.get('domain-search')
        query = request.GET.get('keyword-search')

        print(f"Received domain: {domain} and query: {query}")

        try:
            # Fetch the website content
            url = f'http://{domain}/'
            response = requests.get(url)
            response.raise_for_status()  # Check for errors

            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()

            keyword_density, keyword_count, total_words = calculate_keyword_density(page_text, query)
            readability_score = calculate_readability_score(page_text)
            load_speed = measure_load_speed(url)

            description = check_description(soup).title()
            img_alt = check_img_tag(soup).title()
            title = check_title(soup).title()

            # Print results
            if keyword_count > 0:
                print(f"The query '{query}' was found {keyword_count} times in {domain}.")
                print(f"Total words on page: {total_words}")
                print(f"Keyword Density: {keyword_density:.2f}%")
            else:
                print(f"The query '{query}' was NOT found in {domain}.")
            
            if load_speed is not None:
                print(f"Page Load Speed: {load_speed:.2f} seconds")
            else:
                print("Could not measure page load speed.")

        except requests.exceptions.RequestException as e:
            print(f"Error accessing {domain}: {e}")
            load_speed = None

        return render(request, 'home.html', {
            'domain': domain,
            'query': query,
            'query_count': keyword_count,
            'total_words': total_words,
            'keyword_density': keyword_density,
            'description': description,
            'img_alt': img_alt,
            'title': title,
            'read_score': readability_score,
            'load_speed': load_speed
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
    
    return round(keyword_density, 2), keyword_count, total_words

def check_title(soup):
    title_tag = soup.title
    title = title_tag.string.strip() if title_tag else None
    title_check = "filled" if title else "missing"
    return title_check

def check_description(soup):
    meta_description_tag = soup.find('meta', {'name': 'description'})
    meta_description = meta_description_tag['content'] if meta_description_tag else None
    meta_description_check = "filled" if meta_description else "missing"
    return meta_description_check

def check_img_tag(soup):
    img_tags = soup.find_all('img')
    img_alt_check = "filled" if all(img.get('alt') for img in img_tags) else "missing"
    if img_alt_check == "missing":
        missing_alt_imgs = [img for img in img_tags if not img.get('alt')]
    return img_alt_check

# Readability formula based on Flesch-Kincaid Score: https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
def calculate_readability_score(page_text):
    # Tokenize text into sentences and words
    sentences = page_text.split('.')
    words = page_text.split()
    total_sentences = len(sentences)
    total_words = len(words)

    # Count total syllables (basic implementation)
    total_syllables = sum(count_syllables(word) for word in words)

    # Calculate readability score using the formula
    if total_sentences > 0 and total_words > 0:
        readability_score = 206.835 - (1.015 * (total_words / total_sentences)) - (84.6 * (total_syllables / total_words))
    else:
        readability_score = 0
        
    if readability_score >= 100:
        readability_score = 100
    elif readability_score < 0:
        readability_score = 0

    return round(readability_score, 2)

def count_syllables(word):
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev_char_was_vowel = False

    for char in word:
        if char in vowels:
            if not prev_char_was_vowel:
                count += 1  # Count each new vowel group as one syllable
            prev_char_was_vowel = True
        else:
            prev_char_was_vowel = False

    if word.endswith("e"):
        count -= 1  # Subtract a syllable if the word ends with "e"

    return max(count, 1)  # Ensure at least one syllable per word

def measure_load_speed(url):
    """
    Measures the load speed of a page in seconds.
    """
    start_time = time.time()
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for errors
        end_time = time.time()
        load_time = end_time - start_time  # Calculate load time in seconds
        return round(load_time, 2)
    except requests.exceptions.RequestException as e:
        print(f"Error loading page for speed check: {e}")
        return None  # Return None if there's an error