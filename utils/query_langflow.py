import requests
import logging
import threading
from queue import Queue
import argparse
import os

LOG_FILE_NAME = "query_langflow.log"
RESULTS_FILE_NAME = "langflow_query_results.json"

def init_results_file(output_file):
    with open(output_file, 'w') as f:
        f.write("[")

def terminate_results_file(output_file):
    # Remove the trailing comma and add the closing bracket
    with open(output_file, 'rb+') as f:
        f.seek(-2, os.SEEK_END)
        f.truncate()
        f.write(b"\n]")


def process_message(url, message_queue, output_file):
    while not message_queue.empty():
        message = message_queue.get()
        logging.info(f"Scanning URL: {message}")

        try:
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                json={
                    "input_value": message,
                    "output_type": "text",
                    "input_type": "text",
                }
            )
            response.raise_for_status()

            # Extract the desired JSON output and format it
            output_json = response.json()['outputs'][0]['outputs'][0]['results']['text']['text'].strip()

            with open(output_file, 'a') as f:
                f.write(f'{output_json},\n')

        except requests.RequestException as e:
            logging.error(f"Error processing {message}: {e}")

        message_queue.task_done()


def main():
    parser = argparse.ArgumentParser(description="Process messages through Langflow API")
    parser.add_argument('-u', '--url', required=True, type=str, help="Langflow API URL with specific endpoint")
    parser.add_argument('-i', '--input_file', required=True, type=str, help="Input file containing urls to scan")
    parser.add_argument('-o', '--output_dir', default='.', type=str, help="Output directory to save results and logs")
    parser.add_argument('-t', '--threads', type=int, default=4, help="Number of threads to use (default: 4)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(args.output_dir, LOG_FILE_NAME)) 
    ])
        
    results_file_path = os.path.join(args.output_dir, RESULTS_FILE_NAME)
    init_results_file(results_file_path)

    message_queue = Queue()
    with open(args.input_file, 'r') as f:
        for line in f:
            message_queue.put(line.strip())

    threads = []
    for _ in range(args.threads):
        thread = threading.Thread(target=process_message, args=(args.url, message_queue, results_file_path))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()


    terminate_results_file(results_file_path)
    logging.info(f"Scanning completed. Results saved to {results_file_path}.")


if __name__ == "__main__":
    main()
