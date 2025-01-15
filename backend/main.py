import fitz 
import re
import requests
from googlesearch import search
import os
import json
import logging
from googleapiclient.discovery import build 

# Constants
MAX_LEVELS = 5
DOWNLOAD_DIR = "downloads"
OUTPUT_FILE = "output/dependency_graph.json"
SEARCH_DELAY = 2

# Google Custom Search Engine 
CSE_ID = "c1ad58686b7214061" 
API_KEY = "AIzaSyDpGrdj6VYqjj16htY-AZj63ihYjMWKwpk"

# Setup logging
logging.basicConfig(
    filename="output/logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def download_initial_mdl():
    """Download MDL-570 if it doesn't exist"""
    if not os.path.exists("downloads/initial"):
        os.makedirs("downloads/initial")
    
    initial_path = "downloads/initial/MDL-570.pdf"
    if not os.path.exists(initial_path):
        print("Downloading MDL-570...")
        try:
            query = "NAIC MDL-570 life insurance regulation filetype:pdf"
            for url in search(query, num_results=10):
                if url.lower().endswith('.pdf'):
                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(initial_path, 'wb') as f:
                            f.write(response.content)
                        print("Successfully downloaded MDL-570")
                        break
        except Exception as e:
            print(f"Error downloading MDL-570: {e}")
    return initial_path

# Google Custom Search API client
def google_search(query, num_results=10):
    """Search for a query using Google Custom Search API."""
    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        res = service.cse().list(q=query, cx=CSE_ID, num=num_results).execute()
        return res.get("items", [])
    except Exception as e:
        print(f"Error during Google search: {e}")
        return []

def download_pdf(url, output_dir, name):
    """Download a PDF from the given URL."""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            safe_name = re.sub(r'[^\w\-_.]', '_', name) + '.pdf'
            filepath = os.path.join(output_dir, safe_name)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Successfully downloaded: {filepath}")
            return filepath
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return None

def extract_regulation_references(pdf_path):
    """Extract references to other regulations"""
    regulations = []
    try:
        with fitz.open(pdf_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            
            patterns = [
                r'Model\s+(?:Law|Regulation)\s+#?\d+',
                r'MDL-\d+',
                r'Model\s+\d+',
                r'(?:Regulation|Rule)\s+\d+',
                r'\b(?:Chapter|Section)\s+\d+[A-Z]?\s+(?:of\s+the)?\s+(?:Insurance|Life\s+Insurance|Annuity)\s+(?:Code|Regulation|Law)',
                r'Insurance\s+Regulation\s+\d+'
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    ref = match.group().strip()
                    if ref not in regulations:
                        regulations.append(ref)
            
    except Exception as e:
        print(f"Error extracting references from {pdf_path}: {e}")
    
    return regulations

def process_regulation_tree(pdf_path, level=0, processed_refs=None, graph_data=None):
    """Process the regulation and its dependencies recursively."""
    if level >= MAX_LEVELS:
        return graph_data
    
    if processed_refs is None:
        processed_refs = set()
    
    if graph_data is None:
        graph_data = {"nodes": [], "links": []}
    
    current_level_dir = os.path.join(DOWNLOAD_DIR, f"level_{level}")
    os.makedirs(current_level_dir, exist_ok=True)
    
    references = extract_regulation_references(pdf_path)
    current_node = os.path.basename(pdf_path).split('.')[0]
    
    # Add current node if not already in nodes
    if current_node not in [node['id'] for node in graph_data['nodes']]:
        graph_data['nodes'].append({"id": current_node})

    print(f"\nLevel {level} - Found {len(references)} references in {current_node}")
    logging.info(f"Level {level} - Found references: {references}")
    
    downloaded_count = 0
    
    for ref in references:
        print(f"Level {level} - Processing reference: {ref}")
        
        if ref not in processed_refs:
            processed_refs.add(ref)
            
            # Add reference as a node if not already in nodes
            if ref not in [node['id'] for node in graph_data['nodes']]:
                graph_data['nodes'].append({"id": ref})
            
            # Add link between current node and reference
            graph_data['links'].append({"source": current_node, "target": ref})

            if downloaded_count < 2:
                ref_url = search_for_regulation(f'"{ref}" NAIC insurance regulation filetype:pdf')
                if ref_url:
                    logging.info(f"Level {level} - Found URL for reference {ref}: {ref_url}")
                    ref_pdf_path = download_pdf(ref_url, current_level_dir, ref)
                    if ref_pdf_path:
                        process_regulation_tree(ref_pdf_path, level + 1, processed_refs, graph_data)
                        downloaded_count += 1

    return graph_data

def search_for_regulation(query):
    """Search for a regulation using Google Custom Search API."""
    results = google_search(query)
    if results:
        for result in results:
            if result['link'].lower().endswith('.pdf'):
                return result['link']
    return None

def save_dependency_tree(tree, output_file):
    """Save the dependency tree to a JSON file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(tree, f, indent=2)
    logging.info(f"Dependency tree saved to {output_file}")

if __name__ == "__main__":
    try:
        print("Starting Insurance Regulation Dependency Analysis...")
        
        os.makedirs("downloads/initial", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        
        initial_pdf = download_initial_mdl()
        
        if os.path.exists(initial_pdf):
            graph_data = process_regulation_tree(initial_pdf)
            save_dependency_tree(graph_data, OUTPUT_FILE)
            print("Dependency analysis complete.")
        else:
            print("Error: Could not locate or download MDL-570.")
    except Exception as e:
        print(f"Fatal error during execution: {e}")
