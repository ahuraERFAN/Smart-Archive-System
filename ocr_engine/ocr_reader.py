import cv2
import numpy as np
import pytesseract
import re
import os

# تنظیم مسیر Tesseract
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

class UniversalFormParser:
    def __init__(self):
        # تنظیمات بهینه برای خواندن متون فارسی به هم ریخته
        self.custom_config = r'--oem 3 --psm 6 -l fas+eng'
        
    def preprocess_image(self, image_path: str):
        """پیش‌پردازش عمومی و قوی‌تر برای هر نوع سند"""
        img_array = np.fromfile(image_path, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"تصویر خوانده نشد: {image_path}")

        # تبدیل به خاکستری
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # حذف نویز و افزایش وضوح
        kernel = np.ones((1, 1), np.uint8)
        gray = cv2.dilate(gray, kernel, iterations=1)
        gray = cv2.erode(gray, kernel, iterations=1)
        
        # باینری کردن تصویر با آستانه تطبیقی
        processed = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return processed

    def extract_key_values(self, text: str) -> dict:
        """
        استخراج هوشمند و داینامیک تمام فیلدها از هر سندی
        بدون وابستگی به نام فرم یا کلمات خاص
        """
        data = {}
        # پاکسازی اولیه
        text = re.sub(r'[\u200e\u200f\u202a-\u202e]', ' ', text)
        lines = text.split('\n')
        
        # الگوهای جداکننده معمول در فرم‌ها (دو نقطه، سمی‌کالن، خط تیره یا حتی فاصله زیاد)
        separator_pattern = re.compile(r'([:؛=]|-{2,}|\s{3,})')

        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
                
            # جستجوی جداکننده‌ها در خط
            match = separator_pattern.search(line)
            if match:
                # جدا کردن کلید و مقدار بر اساس اولین جداکننده پیدا شده
                split_index = match.start()
                key = line[:split_index].strip()
                value = line[match.end():].strip()
                
                # تمیز کردن کلیدهای کثیف
                key = re.sub(r'[^\w\s\u0600-\u06FF]', '', key).strip()
                
                # اگر کلید معنادار بود (حداقل دو حرف) آن را ذخیره کن
                if len(key) >= 2 and value:
                    data[key] = value

        # استخراج هوشمند تاریخ‌ها از کل متن (در صورتی که جلوی لیبل خاصی نباشند)
        dates = re.findall(r'\b\d{2,4}[/-]\d{1,2}[/-]\d{1,2}\b', text)
        if dates:
            data['تاریخ_های_یافت_شده'] = " | ".join(dates)

        return data

    def process_document(self, image_path: str) -> str:
        """پردازش کامل سند و فرمت‌بندی خروجی"""
        try:
            processed_img = self.preprocess_image(image_path)
            raw_text = pytesseract.image_to_string(processed_img, config=self.custom_config)
            
            if not raw_text.strip():
                return "متنی در سند یافت نشد."

            extracted_data = self.extract_key_values(raw_text)
            
            # ساخت خروجی خوانا برای هر فرمی
            output = ["«اطلاعات استخراج شده از سند»\n" + "="*30]
            if not extracted_data:
                output.append("هیچ فیلد استانداردی (کلید: مقدار) یافت نشد. متن خام:\n" + raw_text)
            else:
                for key, value in extracted_data.items():
                    output.append(f"{key} : {value}")
                    
            return "\n".join(output)

        except Exception as e:
            return f"خطا در پردازش تصویر: {e}"

# نحوه استفاده:
def read_text(image_path: str) -> str:
    parser = UniversalFormParser()
    return parser.process_document(image_path)
