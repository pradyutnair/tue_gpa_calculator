import pandas as pd
import numpy as np
import string
import tabula
import warnings
import regex as re
import fitz

warnings.filterwarnings("ignore")


def fix_credits(column):
    """
    Parameters
    -----------
    column: pandas.Series

    Returns
    -----------
    Removes invalid characters and out of bound values from the
    credits column
    """

    column = column.astype(str)
    pattern = r"([^\d|\.])"
    new_credits = []
    for i in column:
        i = re.sub(pattern, '', i)
        if i == '' or float(i) < 5 or float(i) > 15:
            i = 0
        new_credits.append(float(i))
    return new_credits


# %%
def fix_dates_grades(df):
    """
    Parameters
    -----------
    df: Takes a dataframe created from tabula-py

    Returns
    -----------
    Removes invalid characters and out of bound values from the
    date column. Also adds preliminary grades values through corrections.
    """
    dates = df.date.astype(str)
    date_pattern = r"(\d{2}-\d{2}-\d{4})"
    date_fixed = []
    grades_fixed = []

    for i in dates:
        date = re.findall(date_pattern, i)
        if date == 'nan' or not date:
            date_fixed.append('No-Date')
        else:
            date_fixed.append(date[0])
        grades_fixed.append(re.sub(date_pattern, '', i))

    final_grades_fixed = []
    for i in grades_fixed:
        i = re.sub(',', '.', i)
        try:
            if i == 'nan' or float(i) < 5:
                final_grades_fixed.append(0)
            else:
                final_grades_fixed.append(float(i))
        except:
            final_grades_fixed.append(0)
    return date_fixed, final_grades_fixed


def fix_course(df):
    """
    Parameters
    -----------
    df: Takes a dataframe created from tabula-py

    Returns
    -----------
    Removes invalid characters and out of bound values from the
    course column. Also fixes course names.
    """
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

    return course_code_fixed, course_name_fixed


# %%
def grades_table_creator(file):
    """
    Parameters
    -----------
    file: Raw pdf input file

    Returns
    -----------
    Preprocessed dataframe with the relevant and corrected information
    """
    pages = 0
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for _ in doc:
            pages += 1
    page_description = "3-{}".format(pages)
    df = tabula.read_pdf(file, pages=page_description, multiple_tables=False, columns=[0.9, 2.2, 6.1, 7, 7.7, 9])
    df = pd.DataFrame(df[0])
    df = df.reset_index().T.reset_index().T
    df = df.reset_index().iloc[:, 2:]
    df.columns = ['course_type', 'course_code', 'course_name', 'credits', 'credits_duplicated', 'date', 'final_grades',
                  'category']
    df.credits = fix_credits(df.credits)
    df.credits_duplicated = fix_credits(df.credits_duplicated)
    df.credits = df.credits + df.credits_duplicated
    df = df.drop('credits_duplicated', axis=1)

    dates = df.date.astype(str)
    final_grades = df.final_grades.astype(str)
    dates_fixed, final_grades_fixed = fix_dates_grades(df)

    remove_words = []
    pattern = r"([^\d | .])"
    #df.final_grades = df.final_grades.str.replace(',', '.')

    for i in df.final_grades.astype(str):
        sub = re.sub(pattern, '', i)
        try:
            if sub == 'nan' or sub == '' or float(sub) < 4:
                remove_words.append(0)
            else:
                remove_words.append(float(sub))
        except:
            final_grades_fixed.append(0)

    df.final_grades = remove_words
    df.final_grades = df.final_grades.astype(str).str.replace(r"[^\d*|.]", '0').replace(np.nan, 0)
    df.final_grades = df.final_grades.astype(float).fillna(0)

    df.final_grades = df.final_grades + np.array(final_grades_fixed)
    df.date = dates_fixed

    course_code_fixed, course_name_fixed = fix_course(df)

    df.course_code = course_code_fixed
    df.course_name = df.course_name.fillna('')
    df.course_name = df.course_name + np.array(course_name_fixed)
    return df[df.credits>0]
