import secrets
from datetime import datetime
from zoneinfo import ZoneInfo

MONTHS_PT = {
    1: "jan", 2: "fev", 3: "mar", 4: "abr",
    5: "mai", 6: "jun", 7: "jul", 8: "ago",
    9: "set", 10: "out", 11: "nov", 12: "dez"
}

TIMEZONE = ZoneInfo("America/Sao_Paulo")

def get_current_date() -> str:
    now = datetime.now(TIMEZONE)
    month_pt = MONTHS_PT[now.month]
    return f"{month_pt}/{now.year}"

def generate_random_id() -> str:
    return secrets.token_hex(4)