import fitz 
import re
import requests
from googlesearch import search
import os
import json
import logging
from googleapiclient.discovery import build 
import time

# Google Custom Search Engine 
CSE_ID = "c1ad58686b7214061" 
API_KEY = "AIzaSyDpGrdj6VYqjj16htY-AZj63ihYjMWKwpk"

# Constants
MAX_LEVELS = 5
DOWNLOAD_DIR = "downloads"
OUTPUT_FILE = "output/dependency_graph.json"
CLEANED_OUTPUT_FILE = "output/cleaned_dependency_graph.json"  # New output file
SEARCH_DELAY = 2

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

def search_for_regulation(query):
    #Search for a regulation using Google Custom Search API
    results = google_search(query)
    if results:
        for result in results:
            if result['link'].lower().endswith('.pdf'):
                return result['link']
    return None


def google_search(query, num_results=10):
    # Search for a query using Google Custom Search API with rate limiting
    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        time.sleep(SEARCH_DELAY)  # Rate limiting
        res = service.cse().list(q=query, cx=CSE_ID, num=num_results).execute()
        return res.get("items", [])
    except Exception as e:
        logging.error(f"Error during Google search: {e}")
        return []

def download_pdf(url, output_dir, name):
    """Download a PDF from the given URL with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                safe_name = re.sub(r'[^\w\-_.]', '_', name) + '.pdf'
                filepath = os.path.join(output_dir, safe_name)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                logging.info(f"Successfully downloaded: {filepath}")
                return filepath
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return None

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

def clean_regulation_id(regulation_id):
    # Remove extra whitespace and newlines
    cleaned = ' '.join(regulation_id.split())
    
    # Replace underscores with spaces
    cleaned = cleaned.replace('_', ' ')
    
    # Standardize "Model Regulation" format
    cleaned = cleaned.replace('Model Regulation #', 'MDL-')
    cleaned = cleaned.replace('Model Regulation', 'MDL-')
    cleaned = cleaned.replace('Model ', 'MDL-')
    
    # Remove any remaining special characters
    cleaned = ''.join(c for c in cleaned if c.isalnum() or c in ['-', ' '])
    
    return cleaned

def clean_graph_data(data):
    #Clean and deduplicate graph data
    # Create mapping of original IDs to cleaned IDs
    id_mapping = {}
    cleaned_nodes = {}
    
    # Clean and deduplicate nodes
    for node in data['nodes']:
        cleaned_id = clean_regulation_id(node['id'])
        id_mapping[node['id']] = cleaned_id
        
        if cleaned_id not in cleaned_nodes:
            cleaned_nodes[cleaned_id] = {
                'id': cleaned_id,
                'originalIds': [node['id']],
                'type': 'MDL' if 'MDL' in cleaned_id else 'Regulation' if 'Regulation' in cleaned_id else 'Rule'
            }
        else:
            cleaned_nodes[cleaned_id]['originalIds'].append(node['id'])
    
    # Clean and deduplicate links
    cleaned_links = []
    seen_links = set()
    
    for link in data['links']:
        source = id_mapping[link['source']]
        target = id_mapping[link['target']]
        
        # Create unique link identifier
        link_id = f"{source}->{target}"
        
        if link_id not in seen_links and source != target:
            cleaned_links.append({
                'source': source,
                'target': target
            })
            seen_links.add(link_id)
    
    return {
        'nodes': list(cleaned_nodes.values()),
        'links': cleaned_links
    }

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

def save_results(graph_data, output_file):
    """Save both the original and cleaned graph data."""
    try:
        # Save original graph data
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        #use this data for json
        cleaned_data = clean_graph_data(graph_data)
        cleaned_output = output_file.replace('.json', '_cleaned.json')
        with open(cleaned_output, 'w') as f:
            json.dump(cleaned_data, f, indent=2)
        
        logging.info(f"Results saved to {output_file} and {cleaned_output}")
        
    except Exception as e:
        logging.error(f"Error saving results: {e}")

if __name__ == "__main__":
    try:
        print("------Starting Regulation Dependency Analysis--------")
        
        # Create necessary directories
        for directory in ["downloads/initial", "output"]:
            os.makedirs(directory, exist_ok=True)
        
        initial_pdf = download_initial_mdl()
        if os.path.exists(initial_pdf):
            graph_data = process_regulation_tree(initial_pdf)
            save_results(graph_data, OUTPUT_FILE)
            print(f"Original data saved to: {OUTPUT_FILE}")
            print(f"Cleaned data saved to: {OUTPUT_FILE.replace('.json', '_cleaned.json')}")
            print("--------Dependency analysis complete--------")
        else:
            logging.error("Could not locate or download MDL-570.")
            print("Error: Could not locate or download MDL-570.")
            
    except Exception as e:
        logging.error(f"Fatal error during execution: {e}")
        print(f"Fatal error during execution: {e}")
