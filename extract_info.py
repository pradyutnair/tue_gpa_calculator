import pandas as pd
import numpy as np
import string
import tabula
import warnings
import regex as re

warnings.filterwarnings("ignore")


def grades_table_creator(file):
    df = tabula.read_pdf(file, pages="3-6", multiple_tables=False, columns=[0.9, 2.2, 6.1, 7, 7.7, 9])
    df = pd.DataFrame(df[0])
    df = df.reset_index().T.reset_index().T
    df = df.reset_index().iloc[:, 2:]
    df.columns = ['course_type', 'course_code', 'course_name', 'credits', 'credits_duplicated', 'date', 'final_grades',
                  'category']


    def fix_credits(column):
        column = column.astype(str)
        pattern = r"([^\d|\.])"
        creds_2 = []
        for i in column:
            i = re.sub(pattern, '', i)
            if i == '' or float(i) < 5 or float(i) > (15):
                i = 0
            creds_2.append(float(i))
        return creds_2


    df.credits = fix_credits(df.credits)
    df.credits_duplicated = fix_credits(df.credits_duplicated)

    df.credits = df.credits + df.credits_duplicated
    df = df.drop('credits_duplicated', axis=1)

    dates = df.date.astype(str)
    final_grades = df.final_grades.astype(str)

    date_pattern = r"(\d{2}-\d{2}-\d{4})"
    grade_pattern = r"(\s\d+\.\d)"
    date_fixed = []
    grades_fixed = []

    for i in dates:
        date = re.findall(date_pattern, i)
        if not date:
            date_fixed.append('No-Date')
        else:
            date_fixed.append(date[0])
        grades_fixed.append(re.sub(date_pattern, '', i))

    final_grades_fixed = []
    for i in grades_fixed:
        i = re.sub(',','.',i)
        try:
            if i == 'nan' or float(i) < 5:
                final_grades_fixed.append(0)
            else:
                final_grades_fixed.append(float(i))



        except:
            final_grades_fixed.append(0)
            
    df.final_grades = df.final_grades.str.replace(',','.')
    df.final_grades = df.final_grades.str.replace(r"\w*", '0')
    df.final_grades = df.final_grades.replace(np.nan, 0)
    df.final_grades = df.final_grades.astype(float) + np.array(final_grades_fixed)
    df.date = date_fixed

    course_pattern = r"((2|\w){4,}\d)"
    df.course_code = df.course_code.astype(str)
    course_codes = df.course_code
    course_code_fixed = []
    course_name_fixed = []
    for i in course_codes:
        code = re.findall(course_pattern, i)
        if not code:
            course_code_fixed.append('')
        else:
            course_code_fixed.append(code[0][0])
        course_addition = re.sub(course_pattern, '', i)
        if course_addition == 'nan':
            course_name_fixed.append('')
        else:
            course_name_fixed.append(re.sub(course_pattern, '', i))

    df.course_code = course_code_fixed
    df.course_name = df.course_name.fillna('')
    df.course_name = df.course_name + np.array(course_name_fixed)
    return df[df.credits > 0]

