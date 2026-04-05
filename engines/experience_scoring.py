import difflib

class ExperienceScorer:
    def __init__(self):
        # We can map some roles logically, or just use difflib fuzzy matching
        self.role_synonyms = {
            "ai engineer": ["machine learning engineer", "data scientist", "ai developer", "nlp engineer", "computer vision engineer"],
            "data analyst": ["data scientist", "business analyst", "data engineer"],
            "personal trainer": ["fitness instructor", "fitness coach", "gym instructor"],
            "registered nurse": ["nurse", "rn", "clinical nurse"],
            "phlebotomist": ["blood collection technician", "phlebotomy technician"],
            "video production assistant": ["video production", "video editor", "production assistant", "camera assistant"]
        }

    def score_relevance(self, experiences, target_job_role):
        """
        Calculates a relevance score (0.0 to 1.0) based on how well the past experiences 
        match the target job role. Longer duration in relevant roles increases the score.
        """
        if not experiences or not target_job_role:
            return {
                "total_relevance_score": 0.0,
                "relevant_experience_months": 0,
                "matching_roles": []
            }
        
        target_role_lower = target_job_role.lower()
        expanded_targets = [target_role_lower]
        
        for k, v in self.role_synonyms.items():
            if target_role_lower in k or target_role_lower in v:
                expanded_targets.append(k)
                expanded_targets.extend(v)
        
        relevant_months = 0
        matching_roles = []
        
        for exp in experiences:
            title = exp.get("title", "").lower()
            duration = exp.get("duration_months", 0)
            
            # Fuzzy match title against expanded targets
            matches = difflib.get_close_matches(title, expanded_targets, n=1, cutoff=0.5)
            
            # Or token overlap
            title_tokens = set(title.split())
            target_tokens = set(expanded_targets[0].split())
            token_match = len(title_tokens.intersection(target_tokens)) > 0
            
            if matches or token_match or any(t in title for t in expanded_targets):
                relevant_months += duration
                matching_roles.append(exp.get("title"))

        total_months = sum(e.get("duration_months", 0) for e in experiences)
        
        # Calculate score
        if total_months == 0:
            score = 0.0
        else:
            # Relevancy implies that the ratio of relevant experience to total experience is high,
            # or they have a significant amount of relevant experience (e.g. > 24 months is max score)
            ratio_score = relevant_months / total_months
            absolute_score = min(1.0, relevant_months / 36) # 3 years maxes out absolute path
            
            # Weighted average
            score = (ratio_score * 0.4) + (absolute_score * 0.6)
            
        return {
            "total_relevance_score": round(min(1.0, score), 2),
            "relevant_experience_months": relevant_months,
            "matching_roles": list(set(matching_roles))
        }
