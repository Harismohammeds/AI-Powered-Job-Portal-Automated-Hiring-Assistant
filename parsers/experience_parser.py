import re
from datetime import datetime
from dateutil import parser as date_parser

class ExperienceParser:
    def __init__(self):
        # Regex to capture date ranges like "Jan 2020 - Dec 2021" or "2018 to Present"
        # Since resumes may use '20XX', we'll preprocess replacing 'XX' with '20' to make them parsable
        self.date_range_pattern = re.compile(
            r'((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?\s*)?\d{4})'
            r'\s*(?:-|–|—|to)\s*'
            r'((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?\s*)?\d{4}|present|current)',
            re.IGNORECASE
        )
        # Job titles often follow these patterns or are preceded/followed by standard delimiters
        self.job_title_keywords = ['engineer', 'developer', 'manager', 'designer', 'assistant', 'director', 'analyst', 'trainer', 'nurse', 'phlebotomist', 'consultant']

    def parse_experience(self, text):
        experiences = []
        if not text:
            return experiences
        
        # Preprocessing: clean up non-standard characters and normalize 20XX down to a parsable 2020
        clean_text = text.replace('XX', '20')
        # Also treat 'ongoing' as present
        clean_text = clean_text.replace('(Ongoing)', 'Present').replace('ongoing', 'Present')
        
        matches = list(self.date_range_pattern.finditer(clean_text))
        
        for i, match in enumerate(matches):
            start_str = match.group(1).strip()
            end_str = match.group(2).strip()
            
            # Some matches might be partial or invalid, ensuring we have digits
            if not any(c.isdigit() for c in start_str):
                continue

            current_exp = {
                'start_date': start_str,
                'end_date': end_str,
                'is_current': end_str.lower() in ['present', 'current', 'ongoing']
            }
            current_exp['duration_months'] = self._calculate_duration(start_str, end_str)
            
            # Look at text preceding the date to find job title and company
            # We look back from this date match to previous date match (or start of text)
            start_idx = 0 if i == 0 else matches[i-1].end()
            preceding_text = clean_text[start_idx:match.start()].strip()
            
            # Split by common delimiters to separate title, company, location
            parts = [p.strip() for p in re.split(r'\||-|,|\n', preceding_text) if len(p.strip()) > 2]
            
            if parts:
                # The text closer to the date is more likely to be the job title and company
                # Often it's structured as: Title | Company | Location
                # So the last 3 chunks are usually those fields.
                
                # Take up to the last 3 chunks
                recent_parts = parts[-3:] if len(parts) >= 3 else parts
                
                if len(recent_parts) == 3:
                    # Let's assume Title, Company, Location
                    title_part = recent_parts[0]
                    current_exp['company'] = recent_parts[1]
                elif len(recent_parts) == 2:
                    title_part = recent_parts[0]
                    current_exp['company'] = recent_parts[1]
                else:
                    title_part = recent_parts[0]
                    current_exp['company'] = "Unknown"
                    
                # Clean up title if it's too long (e.g. captures a whole paragraph)
                words = title_part.split()
                if len(words) > 8:
                    current_exp['title'] = " ".join(words[-5:])
                else:
                    current_exp['title'] = title_part
            else:
                current_exp['title'] = "Unknown Job Title"
                current_exp['company'] = "Unknown Company"
                
            experiences.append(current_exp)
            
        return experiences

    def _calculate_duration(self, start_str, end_str):
        try:
            # If no month is present, default to Jan
            if not any(c.isalpha() for c in start_str):
                start_str = "Jan " + start_str
            start_date = date_parser.parse(start_str)

            if end_str.lower() in ['present', 'current']:
                end_date = datetime.now()
            else:
                if not any(c.isalpha() for c in end_str):
                    end_str = "Dec " + end_str
                end_date = date_parser.parse(end_str)
            
            months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
            return max(1, months)
        except Exception:
            return 0

    def calculate_metrics(self, experiences):
        total_months = sum(exp.get('duration_months', 0) for exp in experiences)
        
        # We need dates for gaps/overlaps, let's try to convert parsed strings back to datetimes
        parsed_dates = []
        for exp in experiences:
            try:
                start = date_parser.parse(exp['start_date'] if any(c.isalpha() for c in exp['start_date']) else "Jan " + exp['start_date'])
                end = datetime.now() if exp['is_current'] else date_parser.parse(exp['end_date'] if any(c.isalpha() for c in exp['end_date']) else "Dec " + exp['end_date'])
                parsed_dates.append((start, end, exp))
            except Exception:
                continue
        
        parsed_dates.sort(key=lambda x: x[0])
        gaps_detected = []
        overlaps_detected = []
        
        for i in range(1, len(parsed_dates)):
            prev_end = parsed_dates[i-1][1]
            curr_start = parsed_dates[i][0]
            
            diff_months = (curr_start.year - prev_end.year) * 12 + (curr_start.month - prev_end.month)
            if diff_months > 1:
                gaps_detected.append({
                    "gap_duration_months": diff_months,
                    "between_roles": [parsed_dates[i-1][2].get('title', 'Unknown'), parsed_dates[i][2].get('title', 'Unknown')]
                })
            elif diff_months < 0:
                overlaps_detected.append({
                    "overlap_duration_months": abs(diff_months),
                    "overlapping_roles": [parsed_dates[i-1][2].get('title', 'Unknown'), parsed_dates[i][2].get('title', 'Unknown')]
                })
        
        return {
            "total_experience_months": total_months,
            "total_experience_years": round(total_months / 12, 1),
            "gaps_detected": gaps_detected,
            "overlaps_detected": overlaps_detected
        }
