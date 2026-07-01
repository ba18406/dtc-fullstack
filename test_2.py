import pandas as pd

file_path = r"C:\Users\Administrator\Downloads\بيانات الهيئة التعليمية للمدارس الخاصة.xlsx"

df = pd.read_excel(file_path)

sch_col = df.columns.to_list()[0:4]

emp_col = df.columns.to_list()[4:11]

rows = []

for idx, row in df.iterrows():
    sch_part = {c: row.get(c) for c in sch_col}
    for i in range(0, 24):
        suffix = "" if i == 0 else str(i)

        # stop if this employee block doesn't exist in the file
        if f"{emp_col[0]}{suffix}" not in df.columns:   # اسم الموظف / اسم الموظف1 / ...
            break
        
        emp = {}
        for col in emp_col:
            col_name = f"{col}{suffix}"
            emp[col] = row.get(col_name)
        name = emp.get(emp_col[0])
        if pd.notna(name) and str(name).strip() !="":
            rows.append({**sch_part, **emp})
df_out = pd.DataFrame(rows)
print(df_out)
output_path = r"C:\Users\Administrator\Downloads\employees_normalized_1.xlsx"
df_out.to_excel(output_path, index=False)
print("Save to ..", output_path)

'''
school_cols = ["المحافظة", "الولاية", "رمز المدرسة", "اسم المدرسة"]

employee_fields = [
    ("اسم الموظف"),
    ("الجنسية"),
    ("نوع العقد"),
    ("المسمى الوظيفي"),
    ("المادة الدراسية"),
    ("فترة الخدمة (بالسنوات)"),
    ("تاريخ التعيين"),
]

rows = []

for _, r in df.iterrows():
    school_part = {c: r.get(c) for c in school_cols}
    for i in range(0, 24):
        suffix = "" if i == 0 else str(i)
        emp = {}
        for col in employee_fields:
            col_name = f"{col}{suffix}"
            emp[col] = r.get(col_name)
        name = emp.get("اسم الموظف")
        if pd.notna(name) and str(name).strip() != "":
            rows.append({**school_part, **emp})
'''
#print(df.shape)
#print(df.columns[5:16])
