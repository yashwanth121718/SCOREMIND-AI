import re
import math
from typing import Dict, List, Tuple

# Try importing NLTK, sklearn, sentence-transformers gracefully with robust fallbacks
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    
    # Download essential NLTK data packages silently
    for resource in ['punkt', 'stopwords', 'wordnet']:
        try:
            nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
        except LookupError:
            nltk.download(resource, quiet=True)
            
    HAS_NLTK = True
except Exception:
    HAS_NLTK = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except Exception:
    HAS_SKLEARN = False

# Basic Stopwords Fallback if NLTK is absent
BASIC_STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
    'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than',
    'such', 'both', 'through', 'about', 'against', 'between', 'into', 'throughout',
    'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just',
    'don', 'should', 'now', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'it', 'its'
}


class AnswerEvaluatorAI:
    def __init__(self):
        self.stemmer = PorterStemmer() if HAS_NLTK else None

    def preprocess_text(self, text: str) -> List[str]:
        """
        Tokenize, remove punctuation & stop words, and stem tokens.
        """
        if not text:
            return []
            
        # Lowercase & sanitize
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        
        if HAS_NLTK:
            tokens = word_tokenize(clean_text)
            stop_words = set(stopwords.words('english'))
        else:
            tokens = clean_text.split()
            stop_words = BASIC_STOPWORDS

        # Filter stop words and short tokens
        filtered_tokens = [w for w in tokens if w not in stop_words and len(w) > 1]
        
        # Stemming
        if self.stemmer:
            processed = [self.stemmer.stem(w) for w in filtered_tokens]
        else:
            processed = filtered_tokens
            
        return processed

    def calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate TF-IDF Cosine Similarity between model answer and student answer.
        Returns percentage (0.0 to 100.0).
        """
        if not text1 or not text2:
            return 0.0
            
        if HAS_SKLEARN:
            try:
                vectorizer = TfidfVectorizer(stop_words='english')
                tfidf_matrix = vectorizer.fit_transform([text1, text2])
                sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(sim * 100.0)
            except Exception:
                pass

        # Jaccard / Token Overlap Fallback if sklearn vectorizer fails on edge cases
        tokens1 = set(self.preprocess_text(text1))
        tokens2 = set(self.preprocess_text(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
            
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return (len(intersection) / len(union)) * 100.0

    def evaluate_keywords(self, model_answer: str, student_answer: str, target_keywords: str = "") -> Tuple[float, List[str], List[str]]:
        """
        Extract key terms and compare with student answer.
        Returns: (keyword_score_percent, matched_keywords, missing_keywords)
        """
        # Determine explicit or auto-extracted keywords
        kw_list = []
        if target_keywords and target_keywords.strip():
            kw_list = [k.strip().lower() for k in target_keywords.split(',') if k.strip()]
        
        if not kw_list:
            # Auto-extract top content words from model answer
            processed_model = self.preprocess_text(model_answer)
            # Find unique non-duplicate key words
            kw_list = list(dict.fromkeys(processed_model))[:12]

        if not kw_list:
            return 100.0, [], []

        student_lower = student_answer.lower()
        matched = []
        missing = []

        for kw in kw_list:
            # Match stem or whole phrase in student answer
            stem_kw = self.stemmer.stem(kw) if self.stemmer else kw
            if kw in student_lower or stem_kw in student_lower:
                matched.append(kw)
            else:
                missing.append(kw)

        match_ratio = len(matched) / len(kw_list)
        keyword_score = match_ratio * 100.0
        
        return round(keyword_score, 2), matched, missing

    def evaluate_grammar_and_quality(self, student_answer: str, model_answer: str) -> float:
        """
        Evaluate structural quality, length proportion, punctuation, and sentence clarity.
        Returns score percentage (0.0 to 100.0).
        """
        if not student_answer or not student_answer.strip():
            return 0.0

        words = student_answer.strip().split()
        word_count = len(words)
        model_word_count = len(model_answer.strip().split())

        if word_count == 0:
            return 0.0

        # 1. Word Count Ratio (Penalize extremely short answers relative to model answer)
        target_len = max(model_word_count, 15)
        length_ratio = min(word_count / target_len, 1.2)
        length_score = min(length_ratio * 100.0, 100.0)

        # 2. Basic Punctuation & Capitalization Check
        sentences = [s.strip() for s in re.split(r'[.!?]+', student_answer) if s.strip()]
        num_sentences = max(len(sentences), 1)

        cap_sentences = sum(1 for s in sentences if s[0].isupper())
        capitalization_ratio = cap_sentences / num_sentences

        has_ending_punct = 1.0 if re.search(r'[.!?]$', student_answer.strip()) else 0.7

        structure_score = (capitalization_ratio * 50.0) + (has_ending_punct * 50.0)

        # Weighted final grammar & quality score
        final_quality = (0.60 * length_score) + (0.40 * structure_score)
        return min(max(round(final_quality, 2), 10.0), 100.0)

    def generate_feedback(self, 
                          similarity_score: float, 
                          keyword_score: float, 
                          grammar_score: float, 
                          obtained_marks: float, 
                          max_marks: float,
                          matched_kw: List[str], 
                          missing_kw: List[str]) -> str:
        """
        Generate comprehensive, student-friendly AI feedback breakdown.
        """
        percentage = (obtained_marks / max_marks) * 100.0 if max_marks > 0 else 0.0

        feedback_parts = []

        if percentage >= 85:
            feedback_parts.append("🌟 **Excellent Work!** Your answer covers all major concepts thoroughly with strong structural clarity.")
        elif percentage >= 70:
            feedback_parts.append("👍 **Good Answer!** You demonstrated a solid understanding of the topic with minor omissions.")
        elif percentage >= 50:
            feedback_parts.append("⚠️ **Average Attempt.** Your answer addresses key ideas but lacks essential technical depth or complete explanations.")
        else:
            feedback_parts.append("❌ **Needs Significant Improvement.** The response is incomplete or strays from the model answer expectations.")

        # Breakdown highlights
        feedback_parts.append(f"• **Semantic Match**: {similarity_score:.1f}% alignment with model answer.")
        
        if matched_kw:
            matched_str = ", ".join(matched_kw[:6])
            feedback_parts.append(f"• **Key Concepts Covered**: Successfully included {matched_str}.")
            
        if missing_kw:
            missing_str = ", ".join(missing_kw[:6])
            feedback_parts.append(f"• **Missing Keywords**: Consider adding details regarding: {missing_str}.")

        if grammar_score < 60:
            feedback_parts.append("• **Grammar & Formatting Tip**: Ensure answers use proper capitalization, complete sentences, and sufficient length.")

        return "\n".join(feedback_parts)

    def evaluate_answer(self, 
                        model_answer: str, 
                        student_answer: str, 
                        keywords: str = "", 
                        max_marks: float = 10.0,
                        sim_weight: float = 0.50,
                        kw_weight: float = 0.35,
                        gram_weight: float = 0.15) -> Dict:
        """
        Complete Evaluation Pipeline:
        1. Calculate Similarity Score (TF-IDF + Cosine)
        2. Calculate Keyword Match Score
        3. Calculate Grammar & Structural Quality Score
        4. Compute Partial Marks
        5. Generate Detailed AI Feedback
        """
        if not student_answer or not student_answer.strip():
            return {
                'similarity_score': 0.0,
                'grammar_score': 0.0,
                'keyword_score': 0.0,
                'obtained_marks': 0.0,
                'feedback': "No answer submitted.",
                'matched_keywords': "",
                'missing_keywords': keywords or ""
            }

        # 1. Similarity
        sim_score = self.calculate_tfidf_similarity(model_answer, student_answer)
        
        # 2. Keywords
        kw_score, matched_kw, missing_kw = self.evaluate_keywords(model_answer, student_answer, keywords)
        
        # 3. Grammar & Quality
        gram_score = self.evaluate_grammar_and_quality(student_answer, model_answer)
        
        # 4. Total Weighted Score (0.0 to 100.0)
        composite_score = (sim_score * sim_weight) + (kw_score * kw_weight) + (gram_score * gram_weight)
        
        # Compute obtained marks bounded between 0 and max_marks
        raw_marks = (composite_score / 100.0) * max_marks
        obtained_marks = min(max(round(raw_marks, 2), 0.0), max_marks)

        # 5. Feedback
        feedback_text = self.generate_feedback(
            sim_score, kw_score, gram_score, obtained_marks, max_marks, matched_kw, missing_kw
        )

        return {
            'similarity_score': round(sim_score, 2),
            'grammar_score': round(gram_score, 2),
            'keyword_score': round(kw_score, 2),
            'obtained_marks': obtained_marks,
            'feedback': feedback_text,
            'matched_keywords': ", ".join(matched_kw),
            'missing_keywords': ", ".join(missing_kw)
        }


# Global Singleton Instance for clean imports
ai_evaluator = AnswerEvaluatorAI()
