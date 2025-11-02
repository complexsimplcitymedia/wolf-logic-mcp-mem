# -*- encoding: utf-8 -*-
"""
OpenMemory API Client
Handles all communication with the FastAPI backend
"""

import os
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime
import psycopg2
import psycopg2.extras

class MemoryAPIClient:
    """Client for interacting with OpenMemory FastAPI backend"""

    def __init__(self):
        # REST API on port 8888
        self.base_url = os.getenv('MEMORY_API_URL', 'http://localhost:8888')
        # PgVector connection - port 8432
        self.pgvector_url = os.getenv('PGVECTOR_URL', 'postgresql://postgres:postgres@localhost:8432/memories')
        self.user_id = os.getenv('USER_ID', 'cadillacthewolf')
        self.timeout = 30

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise

    def _query_pgvector(self, query: str, params=None) -> List[Dict]:
        """Query PgVector database directly"""
        try:
            conn = psycopg2.connect(self.pgvector_url)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(query, params or ())
            results = cur.fetchall()
            cur.close()
            conn.close()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"PgVector query error: {e}")
            return []

    # ========== Memory Endpoints ==========

    def list_memories(self, page: int = 1, page_size: int = 20,
                     search: str = "", apps: List[str] = None,
                     categories: List[str] = None, show_archived: bool = False,
                     sort_by: str = "created_at", sort_order: str = "desc") -> Dict:
        """List memories with filtering and pagination - Query PgVector directly"""
        offset = (page - 1) * page_size

        # Query PgVector wolf-logic table
        query = """
            SELECT
                id,
                payload->>'data' as content,
                payload->>'user_id' as user_id,
                payload->>'created_at' as created_at,
                payload->>'provider' as app_name,
                payload
            FROM wolf-logic
            WHERE payload->>'user_id' = %s
            ORDER BY payload->>'created_at' DESC
            LIMIT %s OFFSET %s
        """

        results = self._query_pgvector(query, (self.user_id, page_size, offset))

        # Count total
        count_query = "SELECT COUNT(*) as total FROM wolf-logic WHERE payload->>'user_id' = %s"
        count_result = self._query_pgvector(count_query, (self.user_id,))
        total = count_result[0]['total'] if count_result else 0

        # Format results
        memories = []
        for row in results:
            memories.append({
                'id': row['id'],
                'content': row['content'],
                'created_at': row['created_at'],
                'app': {'name': row.get('app_name', 'unknown')},
                'categories': [],
                'state': 'active'
            })

        return {
            'memories': memories,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def get_memory(self, memory_id: str) -> Dict:
        """Get single memory by ID"""
        return self._request('GET', f'/api/v1/memories/{memory_id}')

    def create_memory(self, text: str, app_name: str = "wolf-logic-ui",
                     metadata: Dict = None) -> Dict:
        """Create new memory"""
        payload = {
            "user_id": self.user_id,
            "text": text,
            "app": app_name,
            "metadata": metadata or {}
        }
        return self._request('POST', '/api/v1/memories/', json=payload)

    def update_memory(self, memory_id: str, content: str) -> Dict:
        """Update memory content"""
        payload = {"content": content}
        return self._request('PUT', f'/api/v1/memories/{memory_id}', json=payload)

    def delete_memories(self, memory_ids: List[str]) -> Dict:
        """Delete multiple memories"""
        params = {"memory_ids": memory_ids}
        return self._request('DELETE', '/api/v1/memories/', params=params)

    def pause_memories(self, memory_ids: List[str] = None, app_id: str = None,
                      category: str = None, is_paused: bool = True) -> Dict:
        """Pause or unpause memories"""
        payload = {
            "user_id": self.user_id,
            "is_paused": is_paused
        }
        if memory_ids:
            payload["memory_ids"] = memory_ids
        if app_id:
            payload["app_id"] = app_id
        if category:
            payload["category"] = category

        return self._request('POST', '/api/v1/memories/actions/pause', json=payload)

    def archive_memories(self, memory_ids: List[str]) -> Dict:
        """Archive memories"""
        payload = {
            "user_id": self.user_id,
            "memory_ids": memory_ids
        }
        return self._request('POST', '/api/v1/memories/actions/archive', json=payload)

    def get_categories(self) -> List[str]:
        """Get all unique categories for user - Categories not stored in PgVector"""
        # Categories are not part of the wolf-logic table schema in PgVector
        # Return empty list to avoid calling MCP server
        return []

    def get_access_log(self, memory_id: str) -> Dict:
        """Get access log for a memory"""
        return self._request('GET', f'/api/v1/memories/{memory_id}/access-log')

    def get_related_memories(self, memory_id: str, limit: int = 5) -> Dict:
        """Get related memories"""
        return self._request('GET', f'/api/v1/memories/{memory_id}/related?limit={limit}')

    # ========== App Endpoints ==========

    def list_apps(self, search: str = "", is_active: Optional[bool] = None,
                 page: int = 1, page_size: int = 50) -> Dict:
        """List all apps"""
        params = {
            "user_id": self.user_id,
            "page": page,
            "page_size": page_size
        }
        if search:
            params["search"] = search
        if is_active is not None:
            params["is_active"] = is_active

        return self._request('GET', '/api/v1/apps/', params=params)

    def get_app(self, app_id: str) -> Dict:
        """Get app details"""
        return self._request('GET', f'/api/v1/apps/{app_id}')

    def update_app_status(self, app_id: str, is_active: bool) -> Dict:
        """Update app active status"""
        payload = {"is_active": is_active}
        return self._request('PUT', f'/api/v1/apps/{app_id}', json=payload)

    def get_app_memories(self, app_id: str, page: int = 1, page_size: int = 20) -> Dict:
        """Get memories created by an app"""
        params = {"page": page, "page_size": page_size}
        return self._request('GET', f'/api/v1/apps/{app_id}/memories', params=params)

    # ========== Stats Endpoints ==========

    def get_stats(self) -> Dict:
        """Get user stats - Query PgVector directly"""
        # Count memories
        query = "SELECT COUNT(*) as total FROM wolf-logic WHERE payload->>'user_id' = %s"
        result = self._query_pgvector(query, (self.user_id,))
        total_memories = result[0]['total'] if result else 0

        # Count unique apps
        app_query = "SELECT COUNT(DISTINCT payload->>'provider') as total FROM wolf-logic WHERE payload->>'user_id' = %s"
        app_result = self._query_pgvector(app_query, (self.user_id,))
        total_apps = app_result[0]['total'] if app_result else 0

        return {
            'total_memories': total_memories,
            'total_apps': total_apps
        }

    # ========== Config Endpoints ==========

    def get_config(self) -> Dict:
        """Get current configuration"""
        return self._request('GET', f'/api/v1/config/?user_id={self.user_id}')

    def update_config(self, config_data: Dict) -> Dict:
        """Update configuration"""
        config_data["user_id"] = self.user_id
        return self._request('PUT', '/api/v1/config/', json=config_data)

    # ========== Backup Endpoints ==========

    def export_memories(self) -> bytes:
        """Export memories as zip file"""
        payload = {"user_id": self.user_id}
        url = f"{self.base_url}/api/v1/backup/export"
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.content

    def import_memories(self, file_path: str) -> Dict:
        """Import memories from backup zip"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'user_id': self.user_id}
            url = f"{self.base_url}/api/v1/backup/import"
            response = requests.post(url, data=data, files=files, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
