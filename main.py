import requests
import zipfile
import os
import re
import json
import csv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_zip(url, download_path):
    logging.info(f"Downloading file from {url}")
    response = requests.get(url)
    with open(download_path, 'wb') as f:
        f.write(response.content)
    logging.info(f"Downloaded file to {download_path}")

def extract_zip(zip_path, extract_to):
    logging.info(f"Extracting {zip_path} to {extract_to}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    logging.info(f"Extracted files to {extract_to}")

def list_files(directory):
    logging.info(f"Listing files in {directory}:")
    files_found = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            file_path = os.path.join(root, name)
            logging.info(f"Found file: {file_path}")
            files_found.append(file_path)
    return files_found

def find_file_with_extension(directory, extension):
    logging.info(f"Looking for files with {extension} extension in {directory}")
    for file in list_files(directory):
        if file.endswith(extension):
            logging.info(f"Found file with {extension} extension: {file}")
            return file
    raise FileNotFoundError(f"No {extension} file found in the extracted data.")

def clean_line(line):
    clean = re.sub(r'<[^>]*>', '', line).strip()
    return clean

def parse_json_lines(file_path):
    cleaned_data = []
    logging.info(f"Reading and cleaning data from {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            clean_line_content = clean_line(line)
            if clean_line_content:
                try:
                    json_entry = json.loads(clean_line_content)
                    cleaned_data.append(json_entry)
                except json.JSONDecodeError:
                    logging.warning(f"Could not parse line as JSON: {clean_line_content}")
                    continue
    return cleaned_data

def write_csv(data, output_file):
    if not data:
        raise ValueError("No data to write to CSV.")
    
    logging.info(f"Writing data to {output_file}")
    fieldnames = data[0].keys()
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)
    logging.info(f"Data successfully written to {output_file}")

def main(url, output_csv):
    download_path = 'downloaded.zip'
    extract_to = 'extracted_data'
    download_zip(url, download_path)
    extract_zip(download_path, extract_to)
    extracted_files = list_files(extract_to)
    try:
        txt_file_path = find_file_with_extension(extract_to, '.txt')
    except FileNotFoundError:
        logging.info("No .txt file found. Attempting to find other file types.")
        try:
            txt_file_path = find_file_with_extension(extract_to, '.json')
        except FileNotFoundError as e:
            logging.error(e)
            return
    cleaned_json_data = parse_json_lines(txt_file_path)
    try:
        write_csv(cleaned_json_data, output_csv)
    except ValueError as e:
        logging.error(e)

if __name__ == "__main__":
    url = 'https://staging.innup.de/uploads/4191540.zip'
    output_csv = 'cleaned_data.csv'
    
    main(url, output_csv)
