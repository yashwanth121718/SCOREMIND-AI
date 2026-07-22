import re
import math
from typing import Dict, List, Tuple, Set

# Try importing NLTK, sklearn, sentence-transformers gracefully with robust fallbacks
try:
    import nltk
    from nltk.corpus import stopwords, wordnet
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    
    # Download essential NLTK data packages silently
    for resource in ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']:
        try:
            nltk.download(resource, quiet=True)
        except Exception:
            pass
            
    HAS_NLTK = True
except Exception:
    HAS_NLTK = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except Exception:
    HAS_SKLEARN = False

# Fallback technical synonym dictionary for domain term matching
TECH_SYNONYMS = {
    'node': {'element', 'vertex', 'point', 'item'},
    'tree': {'hierarchy', 'structure'},
    'search': {'lookup', 'find', 'locate', 'retrieve'},
    'complexity': {'time', 'efficiency', 'cost', 'bounds'},
    'divide': {'split', 'partition', 'decompose'},
    'conquer': {'solve', 'combine'},
    'transaction': {'operation', 'action', 'execution'},
    'isolation': {'concurrency', 'independence', 'separation'},
    'durability': {'persistence', 'permanence', 'saved'},
    'atomicity': {'indivisible', 'all-or-nothing'},
    'consistency': {'validity', 'integrity', 'correctness'},
    'skewed': {'unbalanced', 'asymmetric', 'linear'}
}

BASIC_STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
    'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than',
    'such', 'both', 'through', 'about', 'against', 'between', 'into', 'throughout',
    'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should',
    'now', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had'
}


class AnswerEvaluatorAI:
    def __init__(self):
        self.stemmer = PorterStemmer() if HAS_NLTK else None
        self.lemmatizer = WordNetLemmatizer() if HAS_NLTK else None

    def preprocess_text(self, text: str) -> List[str]:
        """
        Tokenize, remove punctuation & stop words, and stem tokens.
        """
        if not text:
            return []
            
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        
        tokens = []
        if HAS_NLTK:
            try:
                tokens = word_tokenize(clean_text)
                stop_words = set(stopwords.words('english'))
            except Exception:
                tokens = clean_text.split()
                stop_words = BASIC_STOPWORDS
        else:
            tokens = clean_text.split()
            stop_words = BASIC_STOPWORDS

        filtered_tokens = [w for w in tokens if w not in stop_words and len(w) > 1]
        
        if self.stemmer:
            try:
                processed = [self.stemmer.stem(w) for w in filtered_tokens]
            except Exception:
                processed = filtered_tokens
        else:
            processed = filtered_tokens
            
        return processed

    def get_synonyms(self, word: str) -> Set[str]:
        """
        Retrieves synonyms using NLTK WordNet or tech synonym dictionary fallback.
        """
        syns = set()
        w_lower = word.lower()
        
        if w_lower in TECH_SYNONYMS:
            syns.update(TECH_SYNONYMS[w_lower])

        if HAS_NLTK:
            try:
                for syn in wordnet.synsets(w_lower):
                    for l in syn.lemmas():
                        syns.add(l.name().replace('_', ' ').lower())
            except Exception:
                pass

        return syns

    def calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate TF-IDF Cosine Similarity between model answer and student answer.
        """
        if not text1 or not text2:
            return 0.0
            
        if HAS_SKLEARN:
            try:
                vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
                tfidf_matrix = vectorizer.fit_transform([text1, text2])
                sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(sim * 100.0)
            except Exception:
                pass

        tokens1 = set(self.preprocess_text(text1))
        tokens2 = set(self.preprocess_text(text2))
        
        if not tokens1 or not tokens2:
            return 0.0
            
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        return (len(intersection) / len(union)) * 100.0

    def evaluate_keywords(self, model_answer: str, student_answer: str, target_keywords: str = "") -> Tuple[float, List[str], List[str]]:
        """
        Extract key terms and compare with student answer including synonym matching.
        """
        kw_list = []
        if target_keywords and target_keywords.strip():
            kw_list = [k.strip().lower() for k in target_keywords.split(',') if k.strip()]
        
        if not kw_list:
            processed_model = self.preprocess_text(model_answer)
            kw_list = list(dict.fromkeys(processed_model))[:12]

        if not kw_list:
            return 100.0, [], []

        student_lower = student_answer.lower()
        student_tokens = set(self.preprocess_text(student_answer))
        
        matched = []
        missing = []

        for kw in kw_list:
            stem_kw = self.stemmer.stem(kw) if self.stemmer else kw
            syns = self.get_synonyms(kw)
            
            is_matched = (
                kw in student_lower or 
                stem_kw in student_lower or 
                any(s in student_lower for s in syns) or
                bool(syns.intersection(student_tokens))
            )
            
            if is_matched:
                matched.append(kw)
            else:
                missing.append(kw)

        match_ratio = len(matched) / len(kw_list)
        keyword_score = match_ratio * 100.0
        
        return round(keyword_score, 2), matched, missing

    def evaluate_grammar_and_quality(self, student_answer: str, model_answer: str) -> Tuple[float, List[str]]:
        """
        Evaluate structural quality, length proportion, punctuation, and grammar suggestions.
        """
        if not student_answer or not student_answer.strip():
            return 0.0, ["No answer provided."]

        words = student_answer.strip().split()
        word_count = len(words)
        model_word_count = len(model_answer.strip().split())

        suggestions = []

        target_len = max(model_word_count, 15)
        length_ratio = min(word_count / target_len, 1.2)
        length_score = min(length_ratio * 100.0, 100.0)

        if word_count < target_len * 0.5:
            suggestions.append(f"Answer is concise ({word_count} words vs ~{model_word_count} expected). Elaborate on core definitions.")

        sentences = [s.strip() for s in re.split(r'[.!?]+', student_answer) if s.strip()]
        num_sentences = max(len(sentences), 1)

        cap_sentences = sum(1 for s in sentences if s[0].isupper())
        capitalization_ratio = cap_sentences / num_sentences

        if capitalization_ratio < 0.7:
            suggestions.append("Ensure sentences start with capital letters for professional presentation.")

        has_ending_punct = 1.0 if re.search(r'[.!?]$', student_answer.strip()) else 0.7
        if has_ending_punct < 1.0:
            suggestions.append("End complete thoughts and paragraphs with proper punctuation.")

        structure_score = (capitalization_ratio * 50.0) + (has_ending_punct * 50.0)

        final_quality = (0.60 * length_score) + (0.40 * structure_score)
        return min(max(round(final_quality, 2), 10.0), 100.0), suggestions

    def calculate_confidence_score(self, sim_score: float, kw_score: float, gram_score: float, word_count: int) -> float:
        """
        Computes AI evaluation confidence score (0-100%).
        """
        base_confidence = 70.0
        kw_contrib = (kw_score / 100.0) * 15.0
        sim_contrib = (sim_score / 100.0) * 10.0
        len_contrib = min((word_count / 20.0) * 5.0, 5.0)
        
        confidence = base_confidence + kw_contrib + sim_contrib + len_contrib
        return min(round(confidence, 1), 99.5)

    def generate_feedback(self, 
                          similarity_score: float, 
                          keyword_score: float, 
                          grammar_score: float, 
                          obtained_marks: float, 
                          max_marks: float,
                          matched_kw: List[str], 
                          missing_kw: List[str],
                          grammar_suggestions: List[str]) -> Tuple[str, List[str], List[str], List[str]]:
        """
        Generate detailed breakdown: (feedback_text, strengths, weaknesses, suggestions)
        """
        percentage = (obtained_marks / max_marks) * 100.0 if max_marks > 0 else 0.0

        strengths = []
        weaknesses = []
        suggestions = []

        if percentage >= 85:
            feedback_head = "🌟 **Outstanding Answer!** Thorough explanation with strong concept retention."
            strengths.append("High semantic alignment with official model answer.")
            strengths.append("Includes core domain terminology accurately.")
        elif percentage >= 70:
            feedback_head = "👍 **Good Answer!** Demonstrates solid understanding with minor missing details."
            strengths.append("Understands fundamental concepts.")
            if missing_kw:
                weaknesses.append(f"Omitted key technical terms: {', '.join(missing_kw[:3])}")
        elif percentage >= 50:
            feedback_head = "⚠️ **Satisfactory Attempt.** Addresses basic ideas but lacks required technical depth."
            weaknesses.append("Superficial coverage of model answer requirements.")
            if missing_kw:
                weaknesses.append(f"Missing crucial keywords: {', '.join(missing_kw[:4])}")
        else:
            feedback_head = "❌ **Needs Improvement.** Incomplete or off-topic explanation."
            weaknesses.append("Significant divergence from expected reference answer.")

        if matched_kw:
            strengths.append(f"Successfully incorporated: {', '.join(matched_kw[:5])}")

        if missing_kw:
            suggestions.append(f"Revise and include key concepts: {', '.join(missing_kw[:5])}")

        suggestions.extend(grammar_suggestions)

        feedback_parts = [feedback_head]
        feedback_parts.append(f"• **Semantic Match**: {similarity_score:.1f}%")
        feedback_parts.append(f"• **Keyword Match**: {keyword_score:.1f}%")
        if strengths:
            feedback_parts.append(f"• **Key Strength**: {strengths[0]}")
        if weaknesses:
            feedback_parts.append(f"• **Area for Growth**: {weaknesses[0]}")

        return "\n".join(feedback_parts), strengths, weaknesses, suggestions

    def evaluate_answer(self, 
                        model_answer: str, 
                        student_answer: str, 
                        keywords: str = "", 
                        max_marks: float = 10.0,
                        sim_weight: float = 0.50,
                        kw_weight: float = 0.35,
                        gram_weight: float = 0.15) -> Dict:
        """
        Complete AI Pipeline.
        """
        if not student_answer or not student_answer.strip():
            return {
                'similarity_score': 0.0,
                'grammar_score': 0.0,
                'keyword_score': 0.0,
                'confidence_score': 50.0,
                'obtained_marks': 0.0,
                'feedback': "No answer submitted.",
                'matched_keywords': "",
                'missing_keywords': keywords or "",
                'strengths': [],
                'weaknesses': ["Blank answer script."],
                'suggestions': ["Submit a descriptive text answer or upload a valid script file."]
            }

        sim_score = self.calculate_tfidf_similarity(model_answer, student_answer)
        kw_score, matched_kw, missing_kw = self.evaluate_keywords(model_answer, student_answer, keywords)
        gram_score, gram_suggestions = self.evaluate_grammar_and_quality(student_answer, model_answer)

        composite_score = (sim_score * sim_weight) + (kw_score * kw_weight) + (gram_score * gram_weight)
        raw_marks = (composite_score / 100.0) * max_marks
        obtained_marks = min(max(round(raw_marks, 2), 0.0), max_marks)

        word_count = len(student_answer.strip().split())
        confidence_score = self.calculate_confidence_score(sim_score, kw_score, gram_score, word_count)

        feedback_text, strengths, weaknesses, suggestions = self.generate_feedback(
            sim_score, kw_score, gram_score, obtained_marks, max_marks, matched_kw, missing_kw, gram_suggestions
        )

        return {
            'similarity_score': round(sim_score, 2),
            'grammar_score': round(gram_score, 2),
            'keyword_score': round(kw_score, 2),
            'confidence_score': confidence_score,
            'obtained_marks': obtained_marks,
            'feedback': feedback_text,
            'matched_keywords': ", ".join(matched_kw),
            'missing_keywords': ", ".join(missing_kw),
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions
        }


# Global Singleton Instance
ai_evaluator = AnswerEvaluatorAI()
