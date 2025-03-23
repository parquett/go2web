import argparse
import socket
import re
from urllib.parse import urlparse
import json

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

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
        clean_body = '\n'.join(line.strip() for line in clean_body.splitlines() if line.strip())
        return clean_body

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

def make_http_request(url, max_redirects=5):
    if max_redirects == 0:
        raise Exception("Too many redirects")
        
    parsed_url = parse_url(url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, 80))
        
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
        return clean_content
        
    except Exception as e:
        print(f"Error: {e}")

def search_term(term):
    search_url = f"duckduckgo.com/html/?q={term.replace(' ', '+')}"
    make_http_request(search_url)

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