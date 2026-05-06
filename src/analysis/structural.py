"""Rule-based structural analysis module for writing.

Detects common writing issues without requiring NLP libraries.
"""

import re
from dataclasses import dataclass, field
from typing import Literal

# CEFR level type
CEFRLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]

# CEFR ordering for comparisons
CEFR_ORDER = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4, "C2": 5}


@dataclass
class Issue:
    """Represents a detected writing issue."""
    type: str
    line_sentence: str
    suggestion: str
    severity: Literal["low", "medium", "high"] = "medium"
    
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "line/sentence": self.line_sentence,
            "suggestion": self.suggestion,
            "severity": self.severity,
        }


@dataclass
class AnalysisResult:
    """Result of structural analysis."""
    issues: list[Issue] = field(default_factory=list)
    severity: Literal["low", "medium", "high"] = "low"
    summary: str = ""
    score: float = 100.0
    
    def to_dict(self) -> dict:
        return {
            "issues": [i.to_dict() for i in self.issues],
            "severity": self.severity,
            "summary": self.summary,
            "score": self.score,
        }


class StructuralAnalyzer:
    """Rule-based structural analyzer for English writing.
    
    Detects:
    - Article misuse (overuse of "the", missing "a/an")
    - Run-on sentences (> 3 conjunctions)
    - Sentence fragments (very short sentences without proper subject)
    - Spanish interference (false friends)
    - Verb tense inconsistency
    - Preposition patterns
    """
    
    # Spanish false friends dictionary
    FALSE_FRIENDS = {
        "actually": {
            "actual_meaning": "in fact",
            "likely_intent": "currently",
            "suggestions": ["currently", "in fact", "actually (if meaning 'in fact')"],
        },
        "assist": {
            "actual_meaning": "to help",
            "likely_intent": "to attend",
            "suggestions": ["attend", "go to", "participate in"],
        },
        "sensible": {
            "actual_meaning": "reasonable, practical",
            "likely_intent": "sensitive",
            "suggestions": ["sensitive", "emotional", "delicate"],
        },
        "embarrassed": {
            "actual_meaning": "feeling awkward",
            "likely_intent": "pregnant (embarazada)",
            "suggestions": ["pregnant", "expecting"],
        },
        "library": {
            "actual_meaning": "a place with books for borrowing",
            "likely_intent": "bookstore (librería)",
            "suggestions": ["bookstore", "bookshop"],
        },
    }
    
    # Common Spanish-influenced preposition errors
    SPANISH_PREPOSITIONS = {
        "depend of": "depend on",
        "think in": "think about",
        "listen in": "listen to",
        "explain me": "explain to me",
        "ask me": "ask me something" + " OR " + "inquire of me",
        "married with": "married to",
        "enter to": "enter",
        "consist in": "consist of",
    }
    
    # Standard subjects/pronouns for fragment detection
    STANDARD_SUBJECTS = {
        "i", "you", "he", "she", "it", "we", "they",
        "the", "a", "an", "this", "that", "there",
        "what", "which", "who", "whom", "whose",
    }
    
    # Conjunctions that count toward run-on detection
    CONJUNCTIONS = {"and", "but", "so", "because", "when", "or", "nor", "yet", "although", "while", "since", "if", "unless", "until", "after", "before"}
    
    def __init__(self):
        """Initialize the structural analyzer."""
        pass
    
    def analyze(self, text: str) -> AnalysisResult:
        """Analyze text for structural issues.
        
        Args:
            text: The text to analyze.
            
        Returns:
            AnalysisResult with detected issues and score.
        """
        result = AnalysisResult()
        issues: list[Issue] = []
        
        if not text or not text.strip():
            result.summary = "No text provided for analysis."
            return result
        
        # Split into sentences for sentence-level analysis
        sentences = self._split_sentences(text)
        words = text.split()
        total_words = len(words)
        
        # 1. Check article misuse
        issues.extend(self._check_article_usage(text, sentences, total_words))
        
        # 2. Check run-on sentences
        issues.extend(self._check_runons(sentences))
        
        # 3. Check sentence fragments
        issues.extend(self._check_fragments(sentences))
        
        # 4. Check Spanish interference (false friends)
        issues.extend(self._check_false_friends(sentences))
        
        # 5. Check verb tense inconsistency
        issues.extend(self._check_verb_tense(text, sentences))
        
        # 6. Check preposition patterns
        issues.extend(self._check_prepositions(sentences))
        
        result.issues = issues
        
        # Calculate score (100 - penalties)
        score = 100.0
        for issue in issues:
            if issue.severity == "high":
                score -= 15
            elif issue.severity == "medium":
                score -= 8
            else:
                score -= 3
        result.score = max(0.0, score)
        
        # Determine overall severity
        if any(i.severity == "high" for i in issues):
            result.severity = "high"
        elif any(i.severity == "medium" for i in issues):
            result.severity = "medium"
        elif issues:
            result.severity = "low"
        
        # Generate summary
        result.summary = self._generate_summary(issues, result.score)
        
        return result
    
    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting by period, question, exclamation
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _check_article_usage(self, text: str, sentences: list[str], total_words: int) -> list[Issue]:
        """Check for article misuse (overuse of 'the', missing 'a/an')."""
        issues = []
        
        # Count "the" occurrences
        the_count = len(re.findall(r'\bthe\b', text, re.IGNORECASE))
        the_density = the_count / total_words if total_words > 0 else 0
        
        # Excessive "the" usage (> 0.12 per word)
        if the_density > 0.12:
            issues.append(Issue(
                type="article_overuse",
                line_sentence=f"Text density: {the_density:.2f} 'the' per word",
                suggestion="Try using 'a/an' or omitting articles when appropriate. Reduce 'the' usage.",
                severity="medium",
            ))
        
        # Check for singular countable nouns without articles
        # Pattern: "is/am/are/was/were" + article-like word + singular noun (simplified)
        singular_patterns = [
            (r'\b(is|am|are|was|were)\s+(\w+ing)\b', "possible missing article before gerund"),
        ]
        
        for sentence in sentences:
            words = sentence.lower().split()
            # Check for very short sentences that might be fragments
            # "It is a good idea" is ok, but "Is good" is not
            if len(words) >= 2:
                # Check for subject-verb pattern without article before noun
                for pattern, msg in singular_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        issues.append(Issue(
                            type="article_missing",
                            line_sentence=sentence[:80] + "..." if len(sentence) > 80 else sentence,
                            suggestion=f"Possible missing article: {msg}",
                            severity="low",
                        ))
        
        return issues
    
    def _check_runons(self, sentences: list[str]) -> list[Issue]:
        """Check for run-on sentences (> 3 conjunctions)."""
        issues = []
        
        for sentence in sentences:
            words = sentence.lower().split()
            conjunction_count = sum(1 for w in words if w.strip('.,!?') in self.CONJUNCTIONS)
            
            if conjunction_count > 3:
                issues.append(Issue(
                    type="run_on_sentence",
                    line_sentence=sentence[:80] + "..." if len(sentence) > 80 else sentence,
                    suggestion=f"Found {conjunction_count} conjunctions. Consider breaking into shorter sentences.",
                    severity="medium",
                ))
        
        return issues
    
    def _check_fragments(self, sentences: list[str]) -> list[Issue]:
        """Check for sentence fragments (very short sentences without proper subjects)."""
        issues = []
        
        for sentence in sentences:
            words = sentence.split()
            if len(words) < 4:
                # Very short sentence - check if it starts with standard subject
                first_word = words[0].lower().strip('.,!?')
                if first_word not in self.STANDARD_SUBJECTS:
                    issues.append(Issue(
                        type="sentence_fragment",
                        line_sentence=sentence,
                        suggestion="This may be a sentence fragment. Ensure it has a subject and verb.",
                        severity="low",
                    ))
        
        return issues
    
    def _check_false_friends(self, sentences: list[str]) -> list[Issue]:
        """Check for Spanish interference (false friends)."""
        issues = []
        
        text_lower = " ".join(sentences).lower()
        
        for word, info in self.FALSE_FRIENDS.items():
            # Case-insensitive word boundary match
            pattern = rf'\b{word}\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                issues.append(Issue(
                    type="spanish_interference_false_friend",
                    line_sentence=f"'{word}' detected",
                    suggestion=f"'{word}' means '{info['actual_meaning']}', not '{info['likely_intent']}'. Use: {', '.join(info['suggestions'])}",
                    severity="medium",
                ))
        
        return issues
    
    def _check_verb_tense(self, text: str, sentences: list[str]) -> list[Issue]:
        """Check for verb tense inconsistency (simplified heuristic)."""
        issues = []
        
        # Simple past tense markers
        past_markers = ['yesterday', 'last', 'ago', 'was', 'were', 'had', 'did', 'finished', 'went', 'came', 'saw', 'knew']
        # Simple present tense markers  
        present_markers = ['today', 'now', 'currently', 'am', 'is', 'are', 'do', 'does', 'have', 'has', 'usually', 'always', 'never', 'sometimes']
        
        past_count = sum(1 for m in past_markers if m in text.lower())
        present_count = sum(1 for m in present_markers if m in text.lower())
        
        # If both past and present markers exist with no clear temporal transition
        if past_count > 0 and present_count > 0:
            # Check for temporal markers that would justify mixing
            temporal_markers = ['while', 'when', 'before', 'after', 'during', 'meanwhile', 'then', 'now', 'today']
            has_temporal = any(m in text.lower() for m in temporal_markers)
            
            if not has_temporal and abs(past_count - present_count) <= 2:
                # No clear reason for mixing - possible inconsistency
                issues.append(Issue(
                    type="tense_inconsistency",
                    line_sentence=f"Found past markers ({past_count}) and present markers ({present_count})",
                    suggestion="If writing about both past and present, use clear time markers (yesterday, today, while, when) to indicate tense changes.",
                    severity="low",
                ))
        
        return issues
    
    def _check_prepositions(self, sentences: list[str]) -> list[Issue]:
        """Check for common Spanish-influenced preposition errors."""
        issues = []
        
        text_lower = " ".join(sentences).lower()
        
        for wrong, correct in self.SPANISH_PREPOSITIONS.items():
            if wrong in text_lower:
                issues.append(Issue(
                    type="preposition_error",
                    line_sentence=f"'{wrong}' detected",
                    suggestion=f"'{wrong}' → '{correct}' (Spanish interference)",
                    severity="medium",
                ))
        
        # Check for "in the night" vs "at night"
        if re.search(r'\bin\s+the\s+night\b', text_lower):
            # Check if it's NOT "in the morning/afternoon/evening"
            if not re.search(r'\bin\s+the\s+(morning|afternoon|evening)\b', text_lower):
                issues.append(Issue(
                    type="preposition_error",
                    line_sentence="Use of 'in the night'",
                    suggestion="Use 'at night' (but 'in the morning/afternoon/evening' is correct)",
                    severity="low",
                ))
        
        # Check for "on Monday" vs "in Monday" (wrong)
        if re.search(r'\bin\s+monday\b', text_lower) or re.search(r'\bin\s+tuesday\b', text_lower) or \
           re.search(r'\bin\s+wednesday\b', text_lower) or re.search(r'\bin\s+thursday\b', text_lower) or \
           re.search(r'\bin\s+friday\b', text_lower) or re.search(r'\bin\s+saturday\b', text_lower) or \
           re.search(r'\bin\s+sunday\b', text_lower):
            issues.append(Issue(
                type="preposition_error",
                line_sentence="Use of 'in Monday' etc.",
                suggestion="Use 'on Monday', 'on Tuesday', etc. (days of the week use 'on')",
                severity="medium",
            ))
        
        return issues
    
    def _generate_summary(self, issues: list[Issue], score: float) -> str:
        """Generate a one-line summary of main issues."""
        if not issues:
            return f"Excellent structural quality (score: {score:.0f}/100). No significant issues detected."
        
        # Group by type
        by_type: dict[str, int] = {}
        for issue in issues:
            by_type[issue.type] = by_type.get(issue.type, 0) + 1
        
        # Find most common issues
        most_common = sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:3]
        issue_descriptions = [f"{t} ({c})" for t, c in most_common]
        
        return f"Score: {score:.0f}/100. Main issues: {', '.join(issue_descriptions)}"
