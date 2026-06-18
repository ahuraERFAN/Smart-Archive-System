import re
import json

def extract_fields(clean_text: str) -> str:
    """
    استخراج فیلدها از متنِ تمیز شده به صورت JSON برای دیتابیس
    قابلیت تشخیص و استخراج اطلاعات هر ۳ نوع فرم
    """
    data = {}
    
    # 1. تشخیص فرم مرخصی
    if "فرم درخواست مرخصی پرسنل" in clean_text:
        data['form_type'] = "leave_request"
        
        match = re.search(r'شماره پرسنلی:\s*(\d+)', clean_text)
        if match: data['personnel_id'] = match.group(1)
            
        match = re.search(r'نام و نام خانوادگی:\s*(.*?)\s+دپارتمان', clean_text)
        if match: data['full_name'] = match.group(1).strip()
            
        match = re.search(r'علت مرخصی:\s*(.*)', clean_text)
        if match: data['reason'] = match.group(1).strip()
            
        match = re.search(r'مجموع زمان مرخصی.*?:\s*(\d+)', clean_text)
        if match: data['total_hours'] = match.group(1).strip()

    # 2. تشخیص فرم تجهیزات
    elif "فرم درخواست تجهیزات" in clean_text:
        data['form_type'] = "equipment_request"
        
        match = re.search(r'نام و نام خانوادگی:\s*(.*?)\s+واحد', clean_text)
        if match: data['full_name'] = match.group(1).strip()
            
        match = re.search(r'داخلی تماس:\s*(\d+)', clean_text)
        if match: data['phone_ext'] = match.group(1).strip()
            
        match = re.search(r'شرح دقیق نیاز و دلایل توجیهی:\s*(.*)', clean_text, re.DOTALL)
        if match: data['reason'] = match.group(1).strip()

    # 3. تشخیص فرم گزارش هزینه
    elif "فرم گزارش هزینه" in clean_text:
        data['form_type'] = "expense_report"
        
        match = re.search(r'نام:\s*(.*)', clean_text)
        if match: data['full_name'] = match.group(1).strip()
            
        match = re.search(r'جمع کل هزینه‌ها:\s*([\d\,]+)', clean_text)
        if match: data['total_expense'] = match.group(1).strip()

    else:
        data['form_type'] = "unknown"

    return json.dumps(data, ensure_ascii=False, indent=4)
