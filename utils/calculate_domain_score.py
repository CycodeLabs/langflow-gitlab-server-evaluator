import json
import argparse

MULTIPLIERS = {
    "sensitive_domain_type_score": 10,
    "company_size_score": 10,
    "industry_score": 9,
    "sensitive_repo_score": 9,
    "repo_activity_score": 5
}
MAX_SCORE_PER_CATEGORY = 10


def calculate_score(entry):
    # Calculate a total score based on the individual scores
    total_score = (
        entry["sensitive_domain_type_score"] * MULTIPLIERS["sensitive_domain_type_score"] +
        entry["company_size_score"] * MULTIPLIERS["company_size_score"] +
        entry["industry_score"] * MULTIPLIERS["industry_score"] +
        entry["sensitive_repo_score"] * MULTIPLIERS["sensitive_repo_score"] +
        entry["repo_activity_score"] * MULTIPLIERS["repo_activity_score"]
    )
    
    # Normalize to a score out of 100
    max_possible_score = (
        MULTIPLIERS["sensitive_domain_type_score"] * MAX_SCORE_PER_CATEGORY +
        MULTIPLIERS["company_size_score"] * MAX_SCORE_PER_CATEGORY +
        MULTIPLIERS["industry_score"] * MAX_SCORE_PER_CATEGORY +
        MULTIPLIERS["sensitive_repo_score"] * MAX_SCORE_PER_CATEGORY +
        MULTIPLIERS["repo_activity_score"] * MAX_SCORE_PER_CATEGORY
    )
    
    normalized_score = (total_score / max_possible_score) * 100
    return normalized_score

def main():
    parser = argparse.ArgumentParser(description="Calculate domain scores based on the input file and save to the output file.")
    parser.add_argument("-i", "--input_file", type=str, required=True, help="Path to the input file containing langflow query results.")
    parser.add_argument("-o", "--output_file", type=str, required=True, help="Path to the output file where results will be saved.")
    args = parser.parse_args()

    with open(args.input_file, 'r') as file:
        data = json.load(file)

    for entry in data:
        entry["calculated_score"] = calculate_score(entry)

    # Sort the data by calculated score in descending order
    sorted_data = sorted(data, key=lambda x: x["calculated_score"], reverse=True)

    with open(args.output_file, 'w') as f:
        f.write(json.dumps(sorted_data, indent=4))

if __name__ == "__main__":
    main()