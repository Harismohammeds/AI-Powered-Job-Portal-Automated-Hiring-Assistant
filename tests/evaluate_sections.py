import json
import logging
from parsers.section_classifier import ResumeSectionClassifier

def evaluate_accuracy(data_path="data/labeled_resumes.json"):
    with open(data_path, "r") as f:
        data = json.load(f)
        
    classifier = ResumeSectionClassifier()
    total_sections = 0
    correct_sections = 0
    
    # Detailed report data
    report_lines = ["# Resume Section Classifier Accuracy Report\n"]
    report_lines.append("## Setup\n")
    report_lines.append("- Tested hybrid Rule-based + NLP approach.")
    report_lines.append(f"- Evaluated over {len(data)} labeled sample resumes.\n")
    report_lines.append("## Results\n")
    
    for item in data:
        expected = item["expected_sections"]
        predicted = classifier.segment(item["raw_text"])
        
        report_lines.append(f"### Resume: {item['id']}\n")
        
        for section, expected_text in expected.items():
            total_sections += 1
            pred_text = predicted.get(section, "").strip()
            
            if pred_text == expected_text.strip():
                correct_sections += 1
                report_lines.append(f"- [x] {section.capitalize()} identified correctly.")
            else:
                report_lines.append(f"- [ ] {section.capitalize()} identification failed.")
                report_lines.append(f"  - Expected: {repr(expected_text)}")
                report_lines.append(f"  - Got:      {repr(pred_text)}")
        
        report_lines.append("\n")
                
    accuracy = (correct_sections / total_sections) * 100 if total_sections > 0 else 0
    
    report_lines.insert(4, f"**Overall Accuracy:** {accuracy:.2f}% ({correct_sections}/{total_sections} sections)\n")
    
    # Write report
    report_content = "\n".join(report_lines)
    with open("docs/accuracy_report.md", "w") as f:
        f.write(report_content)
        
    print(f"Evaluation complete. Accuracy: {accuracy:.2f}%. Report generated at docs/accuracy_report.md")

if __name__ == "__main__":
    evaluate_accuracy()
