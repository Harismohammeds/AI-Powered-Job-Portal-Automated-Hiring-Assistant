import json
import logging
from pprint import pprint
from parsers.experience_parser import ExperienceParser

logging.basicConfig(level=logging.INFO)

def test_parser():
    with open('data/processed/Personal-trainer-resume-example-3_classified.json') as f:
        data = json.load(f)
    
    exp_text = data.get('experience', '')
    print("Experience Text:")
    print(exp_text)
    
    parser = ExperienceParser()
    extracted = parser.parse_experience(exp_text)
    
    print("\nExtracted Roles:")
    pprint(extracted)
    
    print("\nMetrics:")
    metrics = parser.calculate_metrics(extracted)
    pprint(metrics)

if __name__ == '__main__':
    test_parser()
