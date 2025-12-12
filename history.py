import os
import json
import datetime as dt

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'common', 'data')
HIST_FILE = os.path.join(DATA_DIR, 'historico.json')


def _ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(HIST_FILE):
        with open(HIST_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def load_history():
    _ensure_storage()
    try:
        with open(HIST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f) or []
    except Exception:
        return []


def save_record(objeto: str, status: str):
    """Save or update a record. If objeto exists, update it; otherwise create new.
    
    Status can be: Subiu, Desceu, Pronto
    Each status sets its corresponding timestamp field.
    """
    _ensure_storage()
    ts = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        data = load_history()
        
        # Find existing entry by objeto name (case-insensitive)
        existing_idx = None
        for i, entry in enumerate(data):
            if entry.get('objeto', '').upper() == objeto.upper():
                existing_idx = i
                break
        
        if existing_idx is not None:
            # Update existing entry
            entry = data[existing_idx]
        else:
            # Create new entry
            entry = {
                'objeto': objeto,
                'subiu': None,
                'desceu': None,
                'pronto': None,
                'status': None,
            }
            data.append(entry)
        
        # Update the appropriate timestamp and status
        status_lower = status.lower()
        if status_lower == 'subiu':
            entry['subiu'] = ts
            entry['status'] = 'Subiu'
        elif status_lower == 'desceu':
            entry['desceu'] = ts
            entry['status'] = 'Desceu'
        elif status_lower == 'pronto':
            entry['pronto'] = ts
            entry['status'] = 'Pronto'
        
        with open(HIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return entry
    except Exception:
        pass
    return None


def show_history():
    # Delegated to Qt app
    try:
        from qt_app import TrayApp
        TrayApp.instance().show_history()
    except Exception:
        pass