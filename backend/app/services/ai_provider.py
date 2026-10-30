import abc
import base64
import hashlib
import json
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.core.errors import AIProviderError

class BaseAIProvider(abc.ABC):
    @abc.abstractmethod
    async def generate_text(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        temperature: float = 0.7
    ) -> str:
        pass

    @abc.abstractmethod
    async def generate_vision(
        self,
        prompt: str,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> str:
        pass

    @abc.abstractmethod
    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav"
    ) -> str:
        pass

    @abc.abstractmethod
    async def generate_speech(
        self,
        text: str,
        voice: str = "alloy"
    ) -> bytes:
        pass

    @abc.abstractmethod
    async def generate_image(
        self,
        prompt: str
    ) -> str:
        pass

    @abc.abstractmethod
    async def generate_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        pass


class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise AIProviderError("OPENAI_API_KEY is not configured in .env")
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_text(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        temperature: float = 0.7
    ) -> str:
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_CHAT_MODEL,
                messages=full_messages,
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI generate_text error: {e}")
            raise AIProviderError(f"OpenAI error: {str(e)}")

    async def generate_vision(
        self,
        prompt: str,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> str:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{b64}"
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt or "Describe and analyze this image in detail."},
                    {"type": "image_url", "image_url": {"url": data_uri}}
                ]
            }
        ]
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_VISION_MODEL,
                messages=messages,
                max_tokens=1000
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI generate_vision error: {e}")
            raise AIProviderError(f"OpenAI Vision error: {str(e)}")

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav"
    ) -> str:
        try:
            transcript = await self.client.audio.transcriptions.create(
                model=settings.OPENAI_TRANSCRIPTION_MODEL,
                file=(filename, audio_bytes)
            )
            return transcript.text
        except Exception as e:
            logger.error(f"OpenAI transcription error: {e}")
            raise AIProviderError(f"OpenAI Transcription error: {str(e)}")

    async def generate_speech(
        self,
        text: str,
        voice: str = "alloy"
    ) -> bytes:
        try:
            response = await self.client.audio.speech.create(
                model=settings.OPENAI_TTS_MODEL,
                voice=voice or settings.OPENAI_TTS_VOICE,
                input=text[:4096]
            )
            return response.content
        except Exception as e:
            logger.error(f"OpenAI TTS error: {e}")
            raise AIProviderError(f"OpenAI Speech error: {str(e)}")

    async def generate_image(
        self,
        prompt: str
    ) -> str:
        try:
            response = await self.client.images.generate(
                model=settings.OPENAI_IMAGE_MODEL,
                prompt=prompt,
                n=1,
                size="1024x1024",
                response_format="url"
            )
            return response.data[0].url
        except Exception as e:
            logger.error(f"OpenAI image generation error: {e}")
            raise AIProviderError(f"OpenAI Image Generation error: {str(e)}")

    async def generate_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        if not texts:
            return []
        try:
            clean_texts = [t.replace("\n", " ") for t in texts]
            response = await self.client.embeddings.create(
                input=clean_texts,
                model=settings.EMBEDDING_MODEL
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"OpenAI embeddings error: {e}")
            raise AIProviderError(f"OpenAI Embeddings error: {str(e)}")


class GeminiProvider(BaseAIProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise AIProviderError("GEMINI_API_KEY is not configured in .env")
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def generate_text(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        temperature: float = 0.7
    ) -> str:
        # Build contents structure
        contents = []
        for msg in messages:
            role = "user" if msg.get("role") in ("user", "system") else "model"
            contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {"temperature": temperature}
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        url = f"{self.base_url}/models/{settings.GEMINI_CHAT_MODEL}:generateContent?key={self.api_key}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise AIProviderError(f"Gemini API returned {resp.status_code}: {resp.text}")
            data = resp.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                return "No response received from Gemini."

    async def generate_vision(
        self,
        prompt: str,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> str:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        contents = [
            {
                "parts": [
                    {"text": prompt or "Analyze this image."},
                    {"inline_data": {"mime_type": mime_type, "data": b64}}
                ]
            }
        ]
        url = f"{self.base_url}/models/{settings.GEMINI_CHAT_MODEL}:generateContent?key={self.api_key}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json={"contents": contents})
            if resp.status_code != 200:
                raise AIProviderError(f"Gemini Vision error {resp.status_code}: {resp.text}")
            data = resp.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                return "No vision response received from Gemini."

    async def transcribe_audio(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        # Gemini can take inline audio data
        b64 = base64.b64encode(audio_bytes).decode("utf-8")
        contents = [
            {
                "parts": [
                    {"text": "Please transcribe this audio recording accurately into text."},
                    {"inline_data": {"mime_type": "audio/wav", "data": b64}}
                ]
            }
        ]
        url = f"{self.base_url}/models/{settings.GEMINI_CHAT_MODEL}:generateContent?key={self.api_key}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json={"contents": contents})
            if resp.status_code != 200:
                raise AIProviderError(f"Gemini Audio error {resp.status_code}: {resp.text}")
            data = resp.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                return "Unable to transcribe audio with Gemini."

    async def generate_speech(self, text: str, voice: str = "alloy") -> bytes:
        raise AIProviderError("Gemini TTS is not directly supported via standard REST; consider using OpenAI TTS.")

    async def generate_image(self, prompt: str) -> str:
        raise AIProviderError("Direct Imagen generation via Gemini REST requires Imagen endpoint configuration.")

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        url = f"{self.base_url}/models/{settings.GEMINI_EMBEDDING_MODEL}:batchEmbedContents?key={self.api_key}"
        requests = [
            {"model": f"models/{settings.GEMINI_EMBEDDING_MODEL}", "content": {"parts": [{"text": t}]}}
            for t in texts
        ]
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json={"requests": requests})
            if resp.status_code != 200:
                raise AIProviderError(f"Gemini Embeddings error {resp.status_code}: {resp.text}")
            data = resp.json()
            return [e["values"] for e in data.get("embeddings", [])]


class MockAIProvider(BaseAIProvider):
    """
    Mock AI Provider for development, testing, and zero-cost local execution without API keys.
    """
    async def generate_text(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        temperature: float = 0.7
    ) -> str:
        last_msg = messages[-1]["content"] if messages else ""
        lower = last_msg.lower()

        # Check for context in system prompt
        has_rag = "[RETRIEVED DOCUMENT CONTEXT]" in system_prompt
        has_web = "[WEB SEARCH RESULTS]" in system_prompt
        is_emotional = "empathetic" in system_prompt.lower() or "emotional" in system_prompt.lower()

        if is_emotional:
            return (
                f"I hear you, and what you're experiencing is completely valid. "
                f"It sounds like you're carrying a lot right now. "
                f"Would it help to take a slow, deep breath together, or would you prefer to talk more about what's on your mind? "
                f"I'm here to listen without judgment.\n\n"
                f"*(Note: Running in local mock mode. Configure OPENAI_API_KEY in .env for production AI models.)*"
            )

        if has_rag:
            return (
                f"Based on the documents in your workspace:\n\n"
                f"I analyzed the uploaded knowledge sources and found relevant details addressing your query: '{last_msg}'. "
                f"The documents discuss key aspects of your topic. Please check the citations below for exact references.\n\n"
                f"*(Note: Running in local mock mode with verified RAG context integration.)*"
            )

        if has_web:
            return (
                f"According to recent web search results:\n\n"
                f"The search query yielded relevant current information regarding '{last_msg}'. "
                f"The referenced websites provide in-depth coverage. Please see the source links listed below.\n\n"
                f"*(Note: Running in local mock mode with active web search citations.)*"
            )

        return (
            f"Hello! I am your Multimodal AI Personal Assistant.\n\n"
            f"You asked: **{last_msg}**\n\n"
            f"I can assist you with:\n"
            f"- 📄 Uploading and querying documents with RAG vector search\n"
            f"- 🌐 Searching the live web with real source links\n"
            f"- 📝 Creating, editing, and versioning documents\n"
            f"- 💬 Empathetic emotional support mode\n"
            f"- 🖼️ Vision and audio multimodal processing\n\n"
            f"*(Running with Mock AI Provider. Add your `OPENAI_API_KEY` or `GEMINI_API_KEY` to `.env` to unlock live frontier LLM generation!)*"
        )

    async def generate_vision(
        self,
        prompt: str,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> str:
        size_kb = round(len(image_bytes) / 1024, 1)
        return (
            f"Image Analysis: Successfully received {mime_type} image ({size_kb} KB).\n\n"
            f"Prompt: '{prompt or 'Describe this image'}'\n\n"
            f"The image content has been processed by the multimodal pipeline. "
            f"In live mode with OpenAI GPT-4o or Gemini, full visual object detection, text extraction, and scene interpretation will be returned."
        )

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav"
    ) -> str:
        size_kb = round(len(audio_bytes) / 1024, 1)
        return f"Audio transcription complete ({filename}, {size_kb} KB): 'Hello assistant, this is a simulated transcription of the uploaded audio recording.'"

    async def generate_speech(
        self,
        text: str,
        voice: str = "alloy"
    ) -> bytes:
        # Return a minimal valid RIFF/WAV header with a short silent tone
        sample_rate = 16000
        duration_sec = 1
        num_samples = sample_rate * duration_sec
        byte_rate = sample_rate * 2
        block_align = 2
        data_size = num_samples * 2
        chunk_size = 36 + data_size

        wav_bytes = bytearray()
        wav_bytes.extend(b"RIFF")
        wav_bytes.extend(chunk_size.to_bytes(4, "little"))
        wav_bytes.extend(b"WAVE")
        wav_bytes.extend(b"fmt ")
        wav_bytes.extend((16).to_bytes(4, "little"))
        wav_bytes.extend((1).to_bytes(2, "little"))  # PCM
        wav_bytes.extend((1).to_bytes(2, "little"))  # 1 channel (mono)
        wav_bytes.extend(sample_rate.to_bytes(4, "little"))
        wav_bytes.extend(byte_rate.to_bytes(4, "little"))
        wav_bytes.extend(block_align.to_bytes(2, "little"))
        wav_bytes.extend((16).to_bytes(2, "little"))  # 16 bits per sample
        wav_bytes.extend(b"data")
        wav_bytes.extend(data_size.to_bytes(4, "little"))
        wav_bytes.extend(b"\x00" * data_size)
        return bytes(wav_bytes)

    async def generate_image(
        self,
        prompt: str
    ) -> str:
        # Generate an inline SVG data URI representing a placeholder generated image
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">'
            f'<defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">'
            f'<stop offset="0%" stop-color="#4f46e5"/><stop offset="100%" stop-color="#9333ea"/>'
            f'</linearGradient></defs>'
            f'<rect width="512" height="512" rx="24" fill="url(#g)"/>'
            f'<circle cx="256" cy="200" r="80" fill="#ffffff" fill-opacity="0.2"/>'
            f'<text x="256" y="340" fill="#ffffff" font-family="system-ui, sans-serif" font-size="22" font-weight="bold" text-anchor="middle">Generated Image</text>'
            f'<text x="256" y="380" fill="#e0e7ff" font-family="system-ui, sans-serif" font-size="14" text-anchor="middle">{prompt[:40]}</text>'
            f'</svg>'
        )
        b64_svg = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
        return f"data:image/svg+xml;base64,{b64_svg}"

    async def generate_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        # Generates deterministic, normalized mock embeddings
        dim = settings.EMBEDDING_DIMENSIONS
        results = []
        for text in texts:
            seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
            # Create deterministic vector
            vec = []
            for i in range(dim):
                val = ((seed + i * 31) % 1000) / 1000.0 - 0.5
                vec.append(val)
            # Normalize
            norm = sum(x * x for x in vec) ** 0.5 or 1.0
            norm_vec = [x / norm for x in vec]
            results.append(norm_vec)
        return results


def get_ai_provider() -> BaseAIProvider:
    provider = settings.AI_PROVIDER.lower().strip()
    if provider == "openai":
        if settings.OPENAI_API_KEY:
            return OpenAIProvider()
        logger.warning("AI_PROVIDER is 'openai' but OPENAI_API_KEY is missing. Falling back to MockAIProvider.")
        return MockAIProvider()
    elif provider == "gemini":
        if settings.GEMINI_API_KEY:
            return GeminiProvider()
        logger.warning("AI_PROVIDER is 'gemini' but GEMINI_API_KEY is missing. Falling back to MockAIProvider.")
        return MockAIProvider()
    else:
        return MockAIProvider()
