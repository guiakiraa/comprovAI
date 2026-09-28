from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import google.auth
import io
from src.logger import get_logger
from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)

READ_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
WRITE_SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_service(scopes: list[str]):
    credentials, _ = google.auth.default(scopes=scopes)
    return build("drive", "v3", credentials=credentials)


def download_file(file_id: str) -> bytes:
    logger.info(f"Baixando arquivo do Drive: {file_id}")
    service = _get_service(READ_SCOPES)

    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()

    content = buffer.getvalue()
    logger.info(f"Download concluído — {len(content)} bytes")
    return content


def delete_file(file_id: str) -> None:
    logger.info(f"Movendo arquivo para a lixeira do Drive: {file_id}")
    service = _get_service(WRITE_SCOPES)
    service.files().update(fileId=file_id, body={"trashed": True}).execute()
    logger.info("Arquivo movido para a lixeira com sucesso!")


def list_files_in_folder(folder_id: str) -> list[dict]:
    logger.info(f"Listando arquivos da pasta: {folder_id}")
    service = _get_service(READ_SCOPES)

    query = (
        f"'{folder_id}' in parents "
        f"and mimeType != 'application/vnd.google-apps.folder' "
        f"and trashed = false"
    )

    files = []
    page_token = None

    while True:
        results = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType)",
            pageSize=1000,
            pageToken=page_token
        ).execute()

        files.extend(results.get("files", []))

        page_token = results.get("nextPageToken")
        if not page_token:
            break

    logger.info(f"{len(files)} arquivo(s) encontrado(s) na pasta")
    return files
