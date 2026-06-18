import os
import shutil
from datetime import datetime
from pathlib import Path

# مسیر داینامیک ذخیره سازی فایل ها
BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__))).parent
BASE_PATH = BASE_DIR / "archive_storage" / "users"

def save_user_file(user_id, source_path):
    user_folder = BASE_PATH / str(user_id)

    # ساخت خودکار پوشه در صورت عدم وجود
    os.makedirs(user_folder, exist_ok=True)

    filename = os.path.basename(source_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = f"{timestamp}_{filename}"
    
    dest_path = os.path.join(user_folder, new_name)
    shutil.copy(source_path, dest_path)

    return dest_path
