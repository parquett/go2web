import argparse
import socket
import re
from urllib.parse import urlparse
import json
import ssl

def remove_html_tags(text):
    text = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', text)
    text = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def parse_http_response(response):
    parts = response.split('\r\n\r\n', 1)
    if len(parts) < 2:
        return "No content found"
    
    headers, body = parts
    
    content_type = 'text/html' 
    for line in headers.split('\r\n'):
        if line.lower().startswith('content-type:'):
            content_type = line.split(':', 1)[1].strip().lower()
            break
    
    if 'application/json' in content_type:
        try:
            parsed_json = json.loads(body)
            return json.dumps(parsed_json, indent=2)
        except:
            return body
    else:
        clean_body = remove_html_tags(body)
        paragraphs = [p.strip() for p in clean_body.split('\n\n') if p.strip()]
        formatted_text = '\n\n'.join(paragraphs)
        return formatted_text

def parse_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        url = 'http://' + url
        parsed = urlparse(url)
    return parsed

def create_http_request(host, path):
    return (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Connection: close\r\n"
        f"User-Agent: go2web/1.0\r\n"
        f"Accept: text/html,application/json\r\n"
        f"\r\n"
    )

cache = {}

def make_http_request(url, max_redirects=5):
    if max_redirects == 0:
        raise Exception("Too many redirects")
    
    if url in cache:
        return cache[url]
        
    parsed_url = parse_url(url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    if parsed_url.query:
        path += '?' + parsed_url.query
    port = 443 if parsed_url.scheme == 'https' else 80

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if parsed_url.scheme == 'https':
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=host)

        sock.connect((host, port))

        request = create_http_request(host, path)
        sock.send(request.encode())
        
        response = b''
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data
            
        sock.close()
        
        decoded_response = response.decode('utf-8', errors='ignore')
        status_line = decoded_response.split('\n')[0]
        status_code = int(status_line.split()[1])
        
        if status_code in (301, 302, 303, 307):
            for line in decoded_response.split('\n'):
                if line.lower().startswith('location:'):
                    new_url = line.split(':', 1)[1].strip()
                    print(f"Redirecting to: {new_url}")
                    return make_http_request(new_url, max_redirects - 1)
        
        clean_content = parse_http_response(decoded_response)
        
        cache[url] = clean_content
            
        return clean_content
        
    except Exception as e:
        print(f"Error: {e}")

def search_term(term):
    search_url = f"https://api.duckduckgo.com/?q={term.replace(' ', '+')}&format=json"
    return make_http_request(search_url)


def format_related_topics(search_result):
    try:
        matches = re.findall(r'"FirstURL"\s*:\s*"([^"]+)".*?"Text"\s*:\s*"([^"]+)"', search_result)
        if matches:
            for url, text in matches:
                print(f'"{text}":"{url}"')

    except Exception as e:
        print(f"Error formatting topics: {e}")

def main():
    parser = argparse.ArgumentParser(
        description='CLI tool for making HTTP requests and searching the web'
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--url', help='Make an HTTP request to the specified URL')
    group.add_argument('-s', '--search', help='Search the term using search engine')
    
    args = parser.parse_args()
    
    if args.url:
        print(make_http_request(args.url))
    elif args.search:
        print(format_related_topics(search_term(args.search)))

if __name__ == "__main__":
    main() 