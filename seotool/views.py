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

            if query.lower() in soup.get_text().lower():
                print(f"The query '{query}' was found in {domain}.")
            else:
                print(f"The query '{query}' was NOT found in {domain}.")

        except requests.exceptions.RequestException as e:
            print(f"Error accessing {domain}: {e}")

        return render(request, 'home.html')
    else:
        return render(request, 'home.html')