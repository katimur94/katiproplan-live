import requests
import base64
import json
import re
import datetime

class SwarmConnector:
    def __init__(self, config_manager):
        self.cfg = config_manager
        self.headers = None
        self.api_url = None
        self.last_world_state = None # Cache für Ghost Data
        self._update_api_details()

    def _update_api_details(self):
        data = self.cfg.data
        if data.get("github_token") and data.get("repo_owner"):
            self.api_url = f"https://api.github.com/repos/{data['repo_owner']}/{data['repo_name']}/contents/{data['repo_path']}"
            self.headers = {
                "Authorization": f"token {data['github_token']}",
                "Accept": "application/vnd.github.v3+json",
                "Cache-Control": "no-cache"
            }

    def fetch_world_state(self):
        """Lädt den aktuellen JSON-Status vom Server."""
        self._update_api_details()
        if not self.api_url:
            return None, "Keine GitHub-Daten konfiguriert."

        try:
            resp = requests.get(self.api_url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                content_b64 = resp.json().get("content", "")
                # Decodieren, Fehler ignorieren falls Encoding seltsam ist
                full_html = base64.b64decode(content_b64).decode('utf-8', errors='ignore')
                sha = resp.json().get("sha")
                
                # Suchen nach dem JSON Block zwischen den Markern
                match = re.search(r"/\*JSON_START\*/(.*?)/\*JSON_END\*/", full_html, re.DOTALL)
                if match:
                    json_data = json.loads(match.group(1))
                    self.last_world_state = {"json": json_data}
                    return {"json": json_data, "sha": sha, "html_template": full_html}, None
                else:
                    # Fallback: Wenn leer, erstelle leere Struktur
                    return {"json": {}, "sha": sha, "html_template": full_html}, None
            else:
                return None, f"GitHub Fehler: {resp.status_code}"
        except Exception as e:
            return None, str(e)

    def push_world_state(self, new_json_data, sha, html_template):
        """Lädt den aktualisierten Status hoch (Sicher gegen Windows-Pfade)."""
        try:
            # JSON erstellen (ensure_ascii=False lässt Umlaute schön)
            json_str = json.dumps(new_json_data, ensure_ascii=False, indent=None)
            
            # --- SICHERE ERSETZUNG (FIX FÜR \u FEHLER) ---
            # Statt re.sub nutzen wir string slicing, damit Backslashes in Pfaden (C:\Users..)
            # nicht als Regex-Befehle missverstanden werden.
            
            pattern = r"/\*JSON_START\*/(.*?)/\*JSON_END\*/"
            match = re.search(pattern, html_template, re.DOTALL)
            
            if match:
                start_idx, end_idx = match.span()
                # Wir bauen den String neu zusammen: Alles davor + Marker + JSON + Marker + Alles danach
                new_html = (
                    html_template[:start_idx] + 
                    "/*JSON_START*/" + 
                    json_str + 
                    "/*JSON_END*/" + 
                    html_template[end_idx:]
                )
            else:
                # Falls Marker fehlen, hängen wir es hinten an (Notfall)
                new_html = html_template + f"\n<script>\n/*JSON_START*/{json_str}/*JSON_END*/\n</script>"

            # Upload Payload
            payload = {
                "message": f"Sync {self.cfg.data['system_name']} - {datetime.datetime.now()}",
                "content": base64.b64encode(new_html.encode('utf-8')).decode('utf-8'),
                "sha": sha
            }
            
            resp = requests.put(self.api_url, headers=self.headers, json=payload)
            
            if resp.status_code in [200, 201]:
                return True, "Erfolg"
            else:
                return False, f"Upload Fehler: {resp.status_code} - {resp.text}"
        except Exception as e:
            return False, str(e)

    def get_project_ghost_structure(self, project_name):
        """
        Filtert Straßen/Haltungen aus der Cloud für das Dropdown.
        """
        if not self.last_world_state:
            return {}
        
        ghost_structure = {}
        
        # Iteriere durch alle Roboter im System
        for sys_name, sys_data in self.last_world_state.get("json", {}).items():
            if not isinstance(sys_data, dict): continue
            
            # Hat dieser Roboter Daten zu unserem Projekt?
            p_data = sys_data.get("data", {}).get("projects", {}).get(project_name)
            if p_data:
                streets = p_data.get("streets", {})
                for s_name, s_content in streets.items():
                    if s_name not in ghost_structure:
                        ghost_structure[s_name] = set()
                    
                    for h_name in s_content.keys():
                        ghost_structure[s_name].add(h_name)
        
        return ghost_structure