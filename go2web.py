import argparse
import socket
from urllib.parse import urlparse

def parse_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        url = 'http://' + url
        parsed = urlparse(url)
    return parsed

def make_http_request(url):
    parsed_url = parse_url(url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    
    print(f"Connecting to: {host}, Path: {path}")

def search_term(term):
    print(f"Searching for: {term}")

def main():
    parser = argparse.ArgumentParser(
        description='CLI tool for making HTTP requests and searching the web'
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--url', help='Make an HTTP request to the specified URL')
    group.add_argument('-s', '--search', help='Search the term using search engine')
    
    args = parser.parse_args()
    
    if args.url:
        make_http_request(args.url)
    elif args.search:
        search_term(args.search)

if __name__ == "__main__":
    main() 