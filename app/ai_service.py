"""
Moduli i Shërbimit të Inteligjencës Artificiale (ai_service.py).
Menaxhon komunikimin me OpenAI API duke përdorur modelin e konfiguruar (AI_MODEL).
Ofron mbështetje për Streaming në kohë reale, matje të saktë të latencës,
trajtues gabimesh të detajuar, dhe logim të strukturuar.
"""

import time
import logging
from typing import Optional, Callable
from openai import (
    OpenAI,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
)
from app.config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    AI_MODEL,
    AI_TIMEOUT_SECONDS,
    PROMPTS,
)

logger: logging.Logger = logging.getLogger(__name__)


class AIService:
    """
    Klasë shërbimi për ndërveprimin me OpenAI API me mbështetje për Streaming dhe Standard Responses.
    """

    def __init__(self) -> None:
        """
        Inicializon klientin OpenAI me çelësin dhe opsionalisht base_url.

        Hedh:
            ValueError: Nëse çelësi OPENAI_API_KEY mungon ose nuk është konfiguruar siç duhet.
        """
        invalid_values = {
            "",
            "vendos_ketu_celesin_tend_openai_sk-...",
            "your_openai_api_key_here",
        }

        if not OPENAI_API_KEY or OPENAI_API_KEY.strip() in invalid_values:
            logger.critical("Çelësi OPENAI_API_KEY mungon ose nuk është konfiguruar.")
            raise ValueError(
                "OPENAI_API_KEY nuk u gjet! Sigurohuni që e keni vendosur në skedarin .env."
            )

        client_kwargs = {
            "api_key": OPENAI_API_KEY,
            "timeout": AI_TIMEOUT_SECONDS,
        }
        if OPENAI_BASE_URL:
            client_kwargs["base_url"] = OPENAI_BASE_URL
            logger.info("Përdoret OpenAI Base URL e personalizuar: %s", OPENAI_BASE_URL)

        self.client: OpenAI = OpenAI(**client_kwargs)
        logger.info(
            "Shërbimi AI u inicializua me sukses. Modeli: %s | Timeout: %.1fs",
            AI_MODEL,
            AI_TIMEOUT_SECONDS,
        )

    def _resolve_system_prompt(
        self, action_key: Optional[str], custom_instruction: Optional[str]
    ) -> str:
        """Përcakton prompt-in e sistemit bazuar në veprimin ose udhëzimin e personalizuar."""
        if custom_instruction and custom_instruction.strip():
            return custom_instruction.strip()
        return PROMPTS.get(
            action_key or "",
            "Je një asistent i dobishëm. Përmirëso tekstin e dhënë.",
        )

    def transform_text_stream(
        self,
        action_key: Optional[str],
        user_text: str,
        custom_instruction: Optional[str] = None,
        on_chunk: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[str, float], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Dërgon kërkesën te modeli AI në modalitet Streaming (token pas tokeni në kohë reale).
        """
        if not user_text or not user_text.strip():
            logger.warning("Kërkesë stream me tekst bosh — u refuzua.")
            if on_error:
                on_error("Nuk ka tekst në clipboard për t'u përpunuar.")
            return

        system_prompt = self._resolve_system_prompt(action_key, custom_instruction)
        logger.info("Kërkesë Streaming AI nisur (%s) me model: %s", action_key or "Custom", AI_MODEL)

        start_time = time.perf_counter()
        accumulated_chunks = []

        try:
            stream = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text.strip()},
                ],
                temperature=0.3,
                stream=True,
                timeout=AI_TIMEOUT_SECONDS,
            )

            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        accumulated_chunks.append(delta)
                        if on_chunk:
                            on_chunk(delta)

            elapsed = time.perf_counter() - start_time
            full_text = "".join(accumulated_chunks).strip()

            logger.info(
                "Streaming përfundoi me sukses në %.2fs (%d fjalë).",
                elapsed,
                len(full_text.split()),
            )

            if on_complete:
                on_complete(full_text, elapsed)

        except AuthenticationError as auth_err:
            logger.error("Gabim Autentifikimi (401): %s", auth_err)
            err_msg = (
                "Gabim Autentifikimi (401): Çelësi OPENAI_API_KEY është i pasaktë ose i skaduar.\n"
                "Ju lutem kontrolloni skedarin .env."
            )
            if on_error:
                on_error(err_msg)

        except RateLimitError as rate_err:
            logger.error("Gabim Rate Limit / Quota (429): %s", rate_err)
            err_msg = (
                "Gabim Kuotash / Rate Limit (429):\n"
                "Llogaria juaj ka arritur kufirin e kërkesave ose nuk ka kredite aktive."
            )
            if on_error:
                on_error(err_msg)

        except (APITimeoutError, TimeoutError) as timeout_err:
            logger.error("Gabim Timeout: %s", timeout_err)
            err_msg = f"Kërkesa zgjati shumë (Timeout pas {AI_TIMEOUT_SECONDS}s)."
            if on_error:
                on_error(err_msg)

        except APIConnectionError as conn_err:
            logger.error("Gabim Lidhjeje me API: %s", conn_err)
            err_msg = "Nuk u arrit lidhja me serverin e OpenAI. Kontrolloni lidhjen e internetit."
            if on_error:
                on_error(err_msg)

        except APIStatusError as status_err:
            logger.error("Gabim Statusi API (%s): %s", status_err.status_code, status_err)
            err_msg = f"Gabim nga OpenAI API (Status {status_err.status_code}): {status_err.message}"
            if on_error:
                on_error(err_msg)

        except Exception as error:
            logger.error("Gabim i papritur gjatë Streaming: %s", error, exc_info=True)
            if on_error:
                on_error(f"Gabim gjatë komunikimit me AI: {str(error)}")

    def transform_text(
        self,
        action_key: Optional[str],
        user_text: str,
        custom_instruction: Optional[str] = None,
    ) -> str:
        """
        Dërgon tekstin te modeli AI dhe kthen rezultatin e plotë sinkron.
        """
        if not user_text or not user_text.strip():
            logger.warning("Kërkesë me tekst bosh — u refuzua.")
            return "Nuk ka tekst në kujtesën e përkohshme (Clipboard) për t'u përpunuar."

        system_prompt = self._resolve_system_prompt(action_key, custom_instruction)
        start_time = time.perf_counter()

        try:
            response = self.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text.strip()},
                ],
                temperature=0.3,
                timeout=AI_TIMEOUT_SECONDS,
            )

            elapsed = time.perf_counter() - start_time
            result_content = response.choices[0].message.content

            if result_content is not None:
                logger.info(
                    "Përgjigja u mor me sukses nga %s brenda %.2f sekondash.",
                    AI_MODEL,
                    elapsed,
                )
                return result_content.strip()

            return "Nuk u kthye asnjë përmbajtje nga modeli AI."

        except Exception as error:
            logger.error("Gabim sinkron me OpenAI: %s", error)
            return f"Gabim: {str(error)}"
