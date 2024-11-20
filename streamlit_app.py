import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

# Input for the name on the order
name_on_order = st.text_input('Name on Smoothie:')
st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# Get the active Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Debugging: Check if session is working
if session:
    st.write("✅ Snowflake session established.")
else:
    st.write("❌ Error establishing session.")
    st.stop()

try:
    # Retrieve available fruits from the Snowflake table
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).to_pandas()

    # Check the first few rows of the dataframe
    st.write("Sample of available fruits:", my_dataframe.head())
except Exception as e:
    st.error(f"Error retrieving data from Snowflake: {e}")
    st.stop()

# Multiselect for choosing ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=my_dataframe['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    for fruit_chosen in ingredients_list:
        # Get the 'SEARCH_ON' value for the selected fruit
        search_on = my_dataframe.loc[my_dataframe['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0] \
            if 'SEARCH_ON' in my_dataframe.columns and not my_dataframe.loc[my_dataframe['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].empty \
            else "Not found"

        # Display search value with formatted text
        st.markdown(f"The search value for **{fruit_chosen}** is **{search_on}**.")

        # Nutrition information section
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
            if smoothiefroot_response.status_code == 200:
                st.json(smoothiefroot_response.json())
            else:
                st.write("⚠️ Unable to retrieve nutrition information.")
        except Exception as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

    # Combine ingredients into a single string
    ingredients_string = ', '.join(ingredients_list)

    # Construct the SQL INSERT statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Submit order button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            # Execute the SQL query
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"Error occurred: {e}")
