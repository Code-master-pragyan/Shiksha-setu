import logging
from typing import List, Optional
from google import genai
from pydantic import ValidationError

from app.ai.schemas import DoubtAnswer, Citation, PracticeQuestion, ShortAnswerEvaluation
from app.ai.prompt_builder import PromptBuilder
from app.api.schemas.retrieval import RetrievalResult
from app.services.student_context import StudentLearningContext

logger = logging.getLogger(__name__)

class GeminiProvider:
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate_grounded_answer(
        self,
        question: str,
        subject: str,
        context: StudentLearningContext,
        context_chunks: List[RetrievalResult]
    ) -> DoubtAnswer:
        
        system_instruction = PromptBuilder.build_system_instruction(context, subject)
        prompt = PromptBuilder.build_prompt(question, context_chunks, context)
        
        logger.info(f"Generating content using model: {self.model}")
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=DoubtAnswer
                )
            )
            
            if not response.text:
                raise RuntimeError("Empty response from Gemini")
                
            return DoubtAnswer.model_validate_json(response.text)
            
        except ValidationError as ve:
            logger.error(f"Failed to parse structured output from Gemini: {ve}")
            raise RuntimeError("Gemini response did not match the expected schema.") from ve
        except Exception as e:
            logger.error(f"Error calling Gemini: {e}")
            raise RuntimeError("Failed to generate answer.") from e

    def generate_practice_question(
        self,
        context: StudentLearningContext,
        subject: str,
        difficulty: str,
        context_chunks: List[RetrievalResult]
    ) -> PracticeQuestion:
        
        sys_inst = f"You are an expert Grade {context.grade} {subject} teacher. Generate a practice question based ONLY on the provided context."
        
        prompt = f"Learning Level / Difficulty: {difficulty.upper()}\n\n"
        prompt += "RETRIEVED EDUCATIONAL CONTEXT:\n\n"
        for idx, chunk in enumerate(context_chunks, 1):
            prompt += f"[Source {idx}]\nText:\n{chunk.text}\n\n"
            
        prompt += """INSTRUCTIONS:
1. Generate a practice question (either multiple_choice or short_answer).
2. The question MUST be answerable strictly using the provided context.
3. If multiple_choice, provide exactly 4 options.
4. Adjust the complexity based on the Learning Level (beginner: recall, intermediate: understanding, advanced: analysis).
5. Output must match the requested JSON schema."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=sys_inst,
                    temperature=0.3,
                    response_mime_type="application/json",
                    response_schema=PracticeQuestion
                )
            )
            if not response.text:
                raise RuntimeError("Empty response from Gemini")
            return PracticeQuestion.model_validate_json(response.text)
        except Exception as e:
            logger.error(f"Error calling Gemini for practice generation: {e}")
            raise RuntimeError("Failed to generate practice question.") from e

    def evaluate_short_answer(
        self,
        question: str,
        expected_answer: str,
        student_answer: str,
        context_chunks: List[RetrievalResult]
    ) -> ShortAnswerEvaluation:
        
        sys_inst = "You are a fair but strict teacher evaluating a student's short answer."
        
        prompt = f"QUESTION: {question}\n"
        prompt += f"EXPECTED ANSWER: {expected_answer}\n"
        prompt += f"STUDENT ANSWER: {student_answer}\n\n"
        prompt += "CONTEXT (for reference):\n"
        for chunk in context_chunks:
            prompt += f"{chunk.text}\n"
            
        prompt += """\nINSTRUCTIONS:
Determine if the student's answer is conceptually correct compared to the expected answer. 
Ignore minor spelling/grammar mistakes. 
Provide brief, constructive feedback."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=sys_inst,
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_schema=ShortAnswerEvaluation
                )
            )
            if not response.text:
                raise RuntimeError("Empty response from Gemini")
            return ShortAnswerEvaluation.model_validate_json(response.text)
        except Exception as e:
            logger.error(f"Error calling Gemini for evaluation: {e}")
            raise RuntimeError("Failed to evaluate answer.") from e
