from openai import OpenAI
import json
import os
from src.classifier.prompts import SYSTEM_PROMPT, USER_PROMPT
from src.logger import get_logger
from src.utils import get_current_date, generate_random_id
from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)
client = OpenAI()

VALID_CATEGORIES = ["agua", "energia", "iptu", "pix", "convenio", "ir", "outros"]

def classify_file(filename: str) -> dict:
    logger.info(f"Classificando arquivo: '{filename}'")

    current_date = get_current_date()
    logger.info(f"Data atual passada ao LLM: '{current_date}'")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(
                filename=filename,
                current_date=current_date
            )}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "file_classification",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": VALID_CATEGORIES,
                            "description": "Categoria do comprovante"
                        },
                        "new_filename": {
                            "type": "string",
                            "description": "Novo nome do arquivo gerado seguindo o padrão"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Breve explicação do raciocínio da classificação"
                        }
                    },
                    "required": ["category", "new_filename", "reasoning"],
                    "additionalProperties": False
                }
            }
        }
    )

    result = json.loads(response.choices[0].message.content)

    if result["category"] == "outros":
        name, ext = os.path.splitext(result["new_filename"])
        result["new_filename"] = f"{name}_{generate_random_id()}{ext}"
        logger.info(f"Categoria 'outros' — ID aleatório adicionado: '{result['new_filename']}'")

    logger.info(f"Categoria identificada: '{result['category']}'")
    logger.info(f"Novo nome gerado: '{result['new_filename']}'")
    logger.info(f"Raciocínio: {result['reasoning']}")

    return result