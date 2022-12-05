import streamlit as st
import pandas as pd
from pytz import country_names
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import os
import sys
from streamlit import cli as stcli
import streamlit
from extract_info import grades_table_creator


def main():
    @st.experimental_memo
    def load_data():
        df = pd.read_csv("grades.csv", encoding="latin-1")
        return df

    @st.experimental_memo
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv()

    # The code below is for the title and logo.
    st.set_page_config(page_title="GPA Calculator", page_icon="🔢", layout="wide")
    st.image(
        "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/325/closed-book_1f4d5.png",
        width=100,
    )
    # conn = init_connection()

    st.title("TU/e GPA Calculator")
    st.write("")
    st.markdown(
        """Find it cumbersome to manually calculate your GPA from `Osiris'` poorly designed document? This tool does it 
        for you automatically! Also, you can edit the cells containing your course & grade information to ensure your scores 
        are accurate."""
    )
    st.write("")
    uploaded_file = st.file_uploader('Upload your .pdf file', type="pdf")
    if uploaded_file:
        df = grades_table_creator(uploaded_file)

        st.write("")
        st.subheader("① Edit and select courses you want to include")
        st.write("Osiris includes all the courses in your elective packages and you probably don't want the "
                 "ones you haven't taken factoring into your GPA.")
        st.info("💡 Hold the `Shift` (⇧) key to select multiple rows at once."
                " Select the first and shift select the last row to select all rows!")
        st.caption("")
        gd = GridOptionsBuilder.from_dataframe(df)
        gd.configure_pagination(enabled=True)
        gd.configure_default_column(editable=True, groupable=True)
        gd.configure_selection(selection_mode="multiple", use_checkbox=True)
        gridoptions = gd.build()
        grid_table = AgGrid(
            df,
            gridOptions=gridoptions,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            theme="material",
        )
        sel_row = grid_table["selected_rows"]

        st.subheader(" ② Check your selection")

        st.write("")

        df_sel_row = pd.DataFrame(sel_row).iloc[:,1:]
        csv = convert_df(df_sel_row)
        if not df_sel_row.empty:
            st.write(df_sel_row)
            st.download_button(
                label="Download to CSV",
                data=csv,
                file_name="results.csv",
                mime="text/csv",
            )
            st.write("")
            st.subheader("③ Your GPA")
            gpa = str(round(df_sel_row["final_grades"].astype("float").mean(),1))
            st.subheader(gpa)

            st.write("")
            st.subheader("④ Grade Progression")
            data = df_sel_row.sort_values(by="date", ascending=True)[['course_name', 'final_grades']]
            st.bar_chart(data=data,width=1000, height=700, use_container_width=True)

    else:
        st.write("Please upload your .pdf file to get started!")


# Your streamlit code

if __name__ == '__main__':
    if streamlit._is_running_with_streamlit:
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
