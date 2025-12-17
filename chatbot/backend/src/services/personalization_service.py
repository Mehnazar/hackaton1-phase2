"""Content personalization service based on user background."""

from typing import Dict, List
from openai import OpenAI

from ..config import settings


class PersonalizationService:
    """Service for personalizing book content based on user profile."""

    def __init__(self):
        api_key = settings.openai_api_key
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = settings.openai_chat_model

    def _check_client(self):
        """Ensure OpenAI client is initialized."""
        if self.client is None:
            raise ValueError("OpenAI API key not configured. Personalization features are disabled.")

    def get_personalization_rules(
        self,
        software_background: str,
        hardware_background: str
    ) -> Dict[str, str]:
        """Get personalization rules based on user background."""

        rules = {
            "beginner": {
                "approach": "Add detailed explanations, avoid jargon, include analogies",
                "code_style": "Add inline comments, break down complex code, include print statements",
                "depth": "Cover fundamentals thoroughly, skip advanced optimization",
                "examples": "Use simple, real-world examples with step-by-step walkthrough"
            },
            "intermediate": {
                "approach": "Balance explanation with efficiency, introduce best practices",
                "code_style": "Clean code with strategic comments, show common patterns",
                "depth": "Cover standard approaches and common optimizations",
                "examples": "Use practical examples with some edge cases"
            },
            "advanced": {
                "approach": "Focus on architecture, performance, and trade-offs",
                "code_style": "Production-ready code, minimal comments, design patterns",
                "depth": "Deep dive into algorithms, optimizations, and system design",
                "examples": "Complex scenarios, performance benchmarks, scalability considerations"
            }
        }

        hardware_context = {
            "low-end": "Emphasize resource-efficient approaches, lighter models, optimization techniques",
            "mid-range": "Balance between performance and resource usage, standard configurations",
            "high-end": "Leverage GPU acceleration, larger models, parallel processing"
        }

        return {
            **rules.get(software_background, rules["intermediate"]),
            "hardware_context": hardware_context.get(hardware_background, hardware_context["mid-range"])
        }

    async def personalize_content(
        self,
        original_content: str,
        software_background: str,
        hardware_background: str,
        chapter_title: str
    ) -> Dict[str, any]:
        """Personalize chapter content using OpenAI."""
        self._check_client()

        rules = self.get_personalization_rules(software_background, hardware_background)

        system_prompt = f"""You are an expert technical writer personalizing educational content.

User Profile:
- Software Background: {software_background}
- Hardware Background: {hardware_background}

Personalization Rules:
- Approach: {rules['approach']}
- Code Style: {rules['code_style']}
- Depth: {rules['depth']}
- Examples: {rules['examples']}
- Hardware Context: {rules['hardware_context']}

Task: Adapt the following chapter content to match the user's profile. Maintain the core information but adjust:
1. Explanation depth and technical terminology
2. Code examples and complexity
3. Hardware requirements and recommendations
4. Practical exercises difficulty

Keep the markdown formatting intact. Return ONLY the personalized content."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Chapter: {chapter_title}\n\n{original_content}"}
                ],
                temperature=0.3,
                max_tokens=4000
            )

            personalized_content = response.choices[0].message.content

            modifications = self._detect_modifications(
                original_content,
                personalized_content,
                software_background,
                hardware_background
            )

            return {
                "personalized_content": personalized_content,
                "modifications": modifications,
                "difficulty_level": software_background,
                "personalization_applied": True
            }

        except Exception as e:
            print(f"Personalization error: {e}")
            return {
                "personalized_content": original_content,
                "modifications": ["Personalization failed - showing original content"],
                "difficulty_level": software_background,
                "personalization_applied": False
            }

    def _detect_modifications(
        self,
        original: str,
        personalized: str,
        software_bg: str,
        hardware_bg: str
    ) -> List[str]:
        """Detect what modifications were made."""

        modifications = []

        # Length-based detection
        if len(personalized) > len(original) * 1.2:
            modifications.append(f"Added detailed explanations for {software_bg} level")
        elif len(personalized) < len(original) * 0.8:
            modifications.append(f"Condensed content for {software_bg} level")

        # Content-based detection
        if software_bg == "beginner" and "```" in personalized:
            modifications.append("Added code comments and explanations")

        if hardware_bg == "low-end" and any(word in personalized.lower() for word in ["optimize", "efficient", "lightweight"]):
            modifications.append("Added resource optimization recommendations")

        if hardware_bg == "high-end" and any(word in personalized.lower() for word in ["gpu", "parallel", "accelerat"]):
            modifications.append("Included GPU acceleration and performance tips")

        if not modifications:
            modifications.append("Adjusted tone and examples to match profile")

        return modifications

    async def translate_to_urdu(self, content: str, chapter_title: str) -> str:
        """Translate chapter content to Urdu using OpenAI."""
        self._check_client()

        system_prompt = """You are a professional technical translator specializing in English to Urdu translation for technical educational content.

Guidelines:
1. Translate all text to Urdu (اردو)
2. Keep code blocks, URLs, and technical terms in English
3. Maintain markdown formatting
4. Preserve headings, lists, and structure
5. Use appropriate Urdu technical terminology
6. Keep proper nouns in English

Return ONLY the translated content."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Translate this chapter to Urdu:\n\nChapter: {chapter_title}\n\n{content}"}
                ],
                temperature=0.2,
                max_tokens=4000
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Translation error: {e}")
            return content  # Return original on error


# Global instance
personalization_service = PersonalizationService()
