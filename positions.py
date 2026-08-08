import json
import os
from typing import Dict, Optional

POSITIONS_FILE = "positions.json"

# Список всех возможных должностей (можно редактировать)
ALL_POSITIONS = [
    "Преподаватель",
    "Целитель",
    "Смотритель леса",
    "Библиотекарь",
    "Мастер зелий",
    "Хранитель артефактов",
    "Стражник",
    "Повар",
    "Садовник",
    "Ученый",
    "Архивариус",
    "Переводчик",
    "Музыкант",
]


def load_positions() -> Dict:
    """Загружает данные из JSON или создаёт начальный файл."""
    if not os.path.exists(POSITIONS_FILE):
        data = {p: {"status": "free", "user_id": None, "message_id": None} for p in ALL_POSITIONS}
        save_positions(data)
        return data
    with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_positions(data: Dict):
    with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_position_status(position: str) -> Optional[str]:
    data = load_positions()
    if position not in data:
        return None
    return data[position]["status"]


def reserve_position(position: str, user_id: int, message_id: int = 0) -> bool:
    """Резервирует должность для пользователя."""
    data = load_positions()
    if position not in data or data[position]["status"] != "free":
        return False
    data[position]["status"] = "reserved"
    data[position]["user_id"] = user_id
    data[position]["message_id"] = message_id
    save_positions(data)
    return True


def occupy_position_for_user(user_id: int) -> bool:
    """Переводит зарезервированную должность пользователя в статус occupied."""
    data = load_positions()
    for pos, info in data.items():
        if info["status"] == "reserved" and info["user_id"] == user_id:
            info["status"] = "occupied"
            save_positions(data)
            return True
    return False


def release_reserved_by_user(user_id: int) -> bool:
    """Освобождает все зарезервированные должности для пользователя (при отклонении)."""
    data = load_positions()
    changed = False
    for pos, info in data.items():
        if info["status"] == "reserved" and info["user_id"] == user_id:
            info["status"] = "free"
            info["user_id"] = None
            info["message_id"] = None
            changed = True
    if changed:
        save_positions(data)
    return changed


def free_position(position: str) -> bool:
    """Принудительно освобождает должность (для админа)."""
    data = load_positions()
    if position not in data:
        return False
    if data[position]["status"] == "free":
        return False  # уже свободна
    data[position]["status"] = "free"
    data[position]["user_id"] = None
    data[position]["message_id"] = None
    save_positions(data)
    return True


def get_reserved_position_for_user(user_id: int) -> Optional[str]:
    data = load_positions()
    for pos, info in data.items():
        if info["status"] == "reserved" and info["user_id"] == user_id:
            return pos
    return None


def get_all_positions_status() -> Dict:
    return load_positions()
