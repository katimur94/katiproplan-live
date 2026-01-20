import os
import shutil
import datetime
import re

class LocalFileManager:
    def __init__(self, config_manager):
        self.cfg = config_manager
        self.base_path = self.cfg.data.get("base_path", "")
        self.obs_file = os.path.join(os.getcwd(), "obs_live.txt")

    def ensure_base_path(self):
        return os.path.exists(self.base_path) if self.base_path else False

    def get_smart_daily_path(self, proj_number, city):
        if not self.base_path: return None
        now = datetime.datetime.now()
        year_str = str(now.year)
        kw_num = now.isocalendar()[1]
        today_str = now.strftime("%Y-%m-%d")
        proj_folder = f"{proj_number} {city}"

        structure_type = self.cfg.data.get("folder_structure", "KW Jahr (z.B. KW2 2026)")

        if structure_type == "KW Jahr (z.B. KW2 2026)":
            kw_folder = f"KW{kw_num} {year_str}"
            full_path = os.path.join(self.base_path, kw_folder, today_str, proj_folder)
        else:
            kw_folder = f"KW{kw_num}"
            full_path = os.path.join(self.base_path, year_str, kw_folder, today_str, proj_folder)
        
        if not os.path.exists(full_path):
            try: os.makedirs(full_path)
            except: return None
        return full_path

    def create_damage_folder(self, daily_path, street, haltung, folder_name):
        target = os.path.join(daily_path, street, haltung, folder_name)
        if not os.path.exists(target): os.makedirs(target)
        return target

    def scan_local_projects(self):
        if not self.ensure_base_path(): return {}
        scanned_data = {}
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        for root, dirs, files in os.walk(self.base_path):
            folder_name = os.path.basename(root)
            if date_pattern.match(folder_name):
                date_str = folder_name
                for proj in dirs:
                    full_path = os.path.join(root, proj)
                    if proj not in scanned_data: scanned_data[proj] = {"last_date": date_str, "paths": []}
                    if date_str > scanned_data[proj]["last_date"]: scanned_data[proj]["last_date"] = date_str
                    scanned_data[proj]["paths"].append({"date": date_str, "path": full_path})
                dirs[:] = [] 
        return scanned_data

    def get_directory_content(self, path):
        if not os.path.exists(path): return []
        items = []
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                is_dir = os.path.isdir(full_path)
                icon = "📁" if is_dir else "📄"
                if not is_dir:
                    lower = item.lower()
                    if lower.endswith(('.mp4', '.avi', '.mov')): icon = "🎬"
                    elif lower.endswith(('.jpg', '.png')): icon = "🖼️"
                    elif lower.endswith(('.xls', '.xlsx')): icon = "📊"
                    elif lower.endswith('.pdf'): icon = "📕"
                items.append({"name": item, "path": full_path, "is_dir": is_dir, "icon": icon})
        except: pass
        return sorted(items, key=lambda x: (not x['is_dir'], x['name']))

    def rename_item(self, old_path, new_name):
        try:
            folder = os.path.dirname(old_path)
            new_path = os.path.join(folder, new_name)
            os.rename(old_path, new_path)
            return True, new_path
        except Exception as e: return False, str(e)

    def delete_item(self, path):
        try:
            if os.path.isfile(path): os.remove(path)
            elif os.path.isdir(path): shutil.rmtree(path)
            return True, ""
        except Exception as e: return False, str(e)

    def get_next_video_number(self, folder_path, swarm_max_number=0):
        local_max = 0
        if os.path.exists(folder_path):
            files = os.listdir(folder_path)
            for f in files:
                m = re.match(r"^(\d+)", f)
                if m:
                    num = int(m.group(1))
                    if num > local_max: local_max = num
        return max(local_max, swarm_max_number) + 1

    def update_obs_txt(self, city, street, haltung, dn=""):
        try:
            content = f"Stadt: {city}\nStraße: {street}\nHaltung: {haltung}"
            if dn: content += f"\nDN {dn}"
            with open(self.obs_file, "w", encoding="utf-8") as f: f.write(content)
            return True
        except: return False
    
    # --- AUFMASS SYNC FIX ---
    def scan_for_cloud_export(self):
        if not self.ensure_base_path(): return {"projects": {}, "stats": {}}
        export_data = {}
        stats = {"stutzen": 0, "kliner": 0, "totalProjects": 0, "gesamtSaniert": 0}
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        
        for root, dirs, files in os.walk(self.base_path):
            folder_name = os.path.basename(root)
            if date_pattern.match(folder_name):
                date_str = folder_name
                for proj in dirs:
                    proj_path = os.path.join(root, proj)
                    if proj not in export_data:
                        export_data[proj] = {"stutzenSaniert": 0, "klinerSaniert": 0, "streets": {}}
                    try:
                        for s in os.listdir(proj_path):
                            s_path = os.path.join(proj_path, s)
                            if not os.path.isdir(s_path): continue
                            if s not in export_data[proj]["streets"]: export_data[proj]["streets"][s] = {}
                            
                            for h in os.listdir(s_path):
                                h_path = os.path.join(s_path, h)
                                if not os.path.isdir(h_path): continue
                                if h not in export_data[proj]["streets"][s]: export_data[proj]["streets"][s][h] = {}
                                
                                # 1. SCANNE NACH EXCEL/DOKUMENTEN DIREKT IN DER HALTUNG
                                docs = []
                                for f in os.listdir(h_path):
                                    if f.lower().endswith(('.xls', '.xlsx', '.pdf', '.doc', '.docx')):
                                        docs.append({"name": f, "date": date_str})
                                
                                if docs:
                                    if "📄 DOKUMENTE" not in export_data[proj]["streets"][s][h]:
                                        export_data[proj]["streets"][s][h]["📄 DOKUMENTE"] = {"files": [], "dates": [], "isSaniert": False}
                                    
                                    # Hinzufügen ohne Duplikate
                                    current_list = export_data[proj]["streets"][s][h]["📄 DOKUMENTE"]["files"]
                                    for d in docs:
                                        if not any(x['name'] == d['name'] for x in current_list):
                                            current_list.append(d)

                                # 2. SCANNE NACH SCHADENSORDNERN
                                for item in os.listdir(h_path):
                                    item_path = os.path.join(h_path, item)
                                    if os.path.isdir(item_path):
                                        dmg_name = item
                                        if dmg_name not in export_data[proj]["streets"][s][h]:
                                            export_data[proj]["streets"][s][h][dmg_name] = {"files": [], "dates": [], "isSaniert": False}
                                        entry = export_data[proj]["streets"][s][h][dmg_name]
                                        if date_str not in entry["dates"]: entry["dates"].append(date_str)
                                        
                                        for f in os.listdir(item_path):
                                            if f.lower().endswith((".mp4", ".jpg", ".pdf", ".xlsx")):
                                                if not any(x['name'] == f for x in entry['files']):
                                                    entry['files'].append({"name": f, "date": date_str})
                                                if ("nach san" in f.lower() or "nach verschließen" in f.lower()) and not entry["isSaniert"]:
                                                    entry["isSaniert"] = True
                                                    stats["gesamtSaniert"] += 1
                                                    if "stutzen" in dmg_name.lower(): stats["stutzen"] += 1; export_data[proj]["stutzenSaniert"] += 1
                                                    elif "liner" in dmg_name.lower(): stats["kliner"] += 1; export_data[proj]["klinerSaniert"] += 1
                    except: pass
                dirs[:] = []
        stats["totalProjects"] = len(export_data)
        return {"projects": export_data, "stats": stats}

    def generate_html_report(self, folder_path, street, haltung):
        if not os.path.exists(folder_path): return False, "Ordner existiert nicht."
        try:
            items = []
            for f in os.listdir(folder_path):
                full = os.path.join(folder_path, f)
                if os.path.isfile(full) and not f.endswith(".html"):
                    size = os.path.getsize(full) / 1024 / 1024
                    icon = "📄"
                    if f.endswith(".mp4"): icon = "🎬"
                    elif f.endswith(".jpg"): icon = "🖼️"
                    items.append(f"<div style='background:#222;padding:10px;margin:5px;display:flex;justify-content:space-between'><span>{icon} {f}</span><span style='color:#888'>{size:.2f} MB</span></div>")
            
            html = f"""<html><body style='font-family:sans-serif;background:#111;color:#eee;padding:20px'>
            <h1 style='color:#00ff66;border-bottom:1px solid #333'>{street} / {haltung}</h1>
            <p>Erstellt: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
            {''.join(items)}
            </body></html>"""
            
            r_path = os.path.join(folder_path, "Tagesbericht.html")
            with open(r_path, "w", encoding="utf-8") as f: f.write(html)
            return True, r_path
        except Exception as e: return False, str(e)