import re
import uuid
from typing import List, Optional, Tuple

class RequirementExtractor:
    PATTERNS = {
        "PERFORMANCE_REQUIREMENT": [
            r"shall\s+(?:maintain|achieve|ensure|provide|support)\s+.*?(?:\d+%|\d+\s+(?:seconds|minutes|hours|days))",
            r"uptime.*?\d+%",
            r"response\s+time.*?\d+\s+(?:seconds|milliseconds)",
            r"availability.*?\d+%",
            r"processing.*?within\s+\d+",
            r"latency.*?\d+",
        ],
        "COMPLIANCE_REQUIREMENT": [
            r"shall\s+comply\s+with",
            r"must\s+(?:meet|satisfy|adhere\s+to)",
            r"in\s+accordance\s+with",
            r"(?:FISMA|NIST|ISO|SOC|HIPAA|FedRAMP)",
            r"encryption.*?(?:AES|TLS|SSL)",
            r"security\s+(?:standards|requirements|controls)",
            r"audit.*?requirements",
            r"(?:authentication|authorization).*?(?:MFA|multi-factor)",
        ],
        "DELIVERABLE_REQUIREMENT": [
            r"shall\s+(?:submit|provide|deliver|furnish)",
            r"(?:report|documentation|deliverable).*?(?:monthly|weekly|quarterly|annually)",
            r"contractor\s+shall\s+prepare",
            r"(?:plan|document|report).*?shall\s+be\s+(?:submitted|provided|delivered)",
            r"by\s+the\s+\d+(?:st|nd|rd|th)\s+(?:day|business\s+day)",
        ],
    }

    def extract(self, text: str, document_id: str) -> List[dict]:
        requirements = []
        lines = text.split('\n')
        current_section = "Unknown"
        current_subsection = "0"

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            section_match = re.match(r'^(Section\s+[\w.]+)[\s:]+(.+)', line, re.IGNORECASE)
            if section_match:
                current_section = section_match.group(1)
                current_subsection = str(line_num)
                continue

            if not re.search(r'\b(?:shall|must|will\s+be\s+required\s+to)\b', line, re.IGNORECASE):
                continue

            classification, confidence = self._classify(line)

            if classification:
                requirements.append({
                    "id": str(uuid.uuid4()),
                    "document_id": document_id,
                    "raw_text": line,
                    "clean_text": self._clean_text(line),
                    "classification": classification,
                    "source_section": current_section,
                    "source_subsection": current_subsection,
                    "ai_confidence_score": str(confidence),
                    "status": "ai_extracted"
                })

        return requirements

    def _classify(self, text: str) -> Tuple[Optional[str], float]:
        scores = {}

        for classification, patterns in self.PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1

            if score > 0:
                scores[classification] = score / len(patterns)

        if not scores:
            return None, 0.0

        best_classification = max(scores, key=scores.get)
        confidence = scores[best_classification]

        return best_classification, confidence

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
