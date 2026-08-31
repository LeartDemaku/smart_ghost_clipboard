"""
Moduli i Ruajtjes së Historikut Lokal me SQLite (history_store.py).
Ofron ruajtje të qëndrueshme, kërkim të shpejtë në kohë reale,
shënim të preferuarave (favorites), dhe pastrim të historikut.
"""

import os
import sqlite3
import datetime
import logging
from typing import List, Dict, Any, Optional

from app.config import BASE_DIR

logger: logging.Logger = logging.getLogger(__name__)

DB_PATH: str = os.path.join(BASE_DIR, "smart_ghost_history.db")


class HistoryStore:
    """
    Menaxheri i bazës së të dhënave SQLite për historikun e transformimeve të AI.
    """

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Krijon një lidhje të re me bazën e të dhënave me timeout të sigurt."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Krijon tabelën dhe indekset e nevojshme nëse nuk ekzistojnë."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        action_name TEXT NOT NULL,
                        original_text TEXT NOT NULL,
                        transformed_text TEXT NOT NULL,
                        latency_ms INTEGER DEFAULT 0,
                        is_favorite INTEGER DEFAULT 0
                    )
                    """
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_history_time ON history (id DESC)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_history_fav ON history (is_favorite)"
                )
                conn.commit()
                logger.debug("Baza e të dhënave e historikut u inicializua: %s", self.db_path)
        except Exception as error:
            logger.error("Gabim gjatë inicializimit të historikut SQLite: %s", error)

    def add_entry(
        self,
        action_name: str,
        original_text: str,
        transformed_text: str,
        latency_ms: int = 0,
    ) -> Optional[int]:
        """
        Shton një transformim të ri në historik.
        """
        if not transformed_text or not transformed_text.strip():
            return None

        # Mos ruaj mesazhet e gabimit të API në historik
        if transformed_text.startswith("Gabim") or "Gabim Autentifikimi" in transformed_text:
            return None

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO history (timestamp, action_name, original_text, transformed_text, latency_ms, is_favorite)
                    VALUES (?, ?, ?, ?, ?, 0)
                    """,
                    (now_str, action_name, original_text.strip(), transformed_text.strip(), latency_ms),
                )
                conn.commit()
                entry_id = cursor.lastrowid
                logger.info("U ruajt në historik entry #%s (%s)", entry_id, action_name)
                return entry_id
        except Exception as error:
            logger.error("Gabim gjatë shtimit në historik: %s", error)
            return None

    def get_entries(
        self,
        limit: int = 50,
        search_query: str = "",
        favorites_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Merr listën e regjistrimeve të historikut me opsione filtrimi dhe kërkimi.
        """
        results: List[Dict[str, Any]] = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT id, timestamp, action_name, original_text, transformed_text, latency_ms, is_favorite FROM history WHERE 1=1"
                params: List[Any] = []

                if favorites_only:
                    query += " AND is_favorite = 1"

                if search_query and search_query.strip():
                    term = f"%{search_query.strip()}%"
                    query += " AND (original_text LIKE ? OR transformed_text LIKE ? OR action_name LIKE ?)"
                    params.extend([term, term, term])

                query += " ORDER BY id DESC LIMIT ?"
                params.append(limit)

                cursor.execute(query, params)
                rows = cursor.fetchall()
                for row in rows:
                    results.append({
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "action_name": row["action_name"],
                        "original_text": row["original_text"],
                        "transformed_text": row["transformed_text"],
                        "latency_ms": row["latency_ms"],
                        "is_favorite": bool(row["is_favorite"]),
                    })
        except Exception as error:
            logger.error("Gabim gjatë leximit të historikut: %s", error)

        return results

    def toggle_favorite(self, entry_id: int) -> bool:
        """
        Ndryshon statusin e preferuarës (Favorite) për një regjistrim.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE history SET is_favorite = (1 - is_favorite) WHERE id = ?",
                    (entry_id,),
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as error:
            logger.error("Gabim gjatë toggle favorite për id=%d: %s", entry_id, error)
            return False

    def delete_entry(self, entry_id: int) -> bool:
        """
        Fshin një regjistrim specifik nga historiku.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM history WHERE id = ?", (entry_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as error:
            logger.error("Gabim gjatë fshirjes së entry id=%d: %s", entry_id, error)
            return False

    def clear_all(self) -> bool:
        """
        Fshin të gjithë historikun (përveç atyre të shënuara si të preferuara nëse dëshirohet, ose të gjitha).
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM history")
                conn.commit()
                logger.info("Historiku u pastrua plotësisht.")
                return True
        except Exception as error:
            logger.error("Gabim gjatë pastrimit të historikut: %s", error)
            return False
