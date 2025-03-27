# go2web CLI Tool

A command-line interface tool for making HTTP requests and performing web searches using DuckDuckGo.

## Features

- Make HTTP/HTTPS requests to any URL
- Built-in caching mechanism for faster repeated requests
- Content negotiation (supports both JSON and HTML responses)
- Automatic redirect handling
- Web search functionality using DuckDuckGo
- Clean text output with HTML tags removed

## Installation

Clone this repository and ensure you have Python 3.9 or higher installed.
## Usage

### Making HTTP Requests

To make a request to a specific URL:

```bash
python go2web.py -u https://example.com
```

### Performing Web Searches


To search the web using DuckDuckGo:

```bash
python go2web.py -s "your search query"
```

## Technical Details

### HTTP Client Features

- Custom socket-based HTTP client implementation
- SSL/TLS support for HTTPS connections
- Automatic handling of redirects (301, 302, 303, 307)
- In-memory response caching
- Content type detection and appropriate parsing
- HTML cleanup and formatting

### Code Structure

The main components of the tool are:
- HTTP request creation and handling
- Response parsing and formatting
- Content type negotiation
- Search functionality
- Command-line interface

## Requirements

- Python 3.9+
- No external dependencies required (uses only Python standard library)

## Example of usage
![work](https://github.com/user-attachments/assets/1591c813-c1c3-4d82-8112-048ec272fb91)
