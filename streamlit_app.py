# Import necessary libraries
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

# Input for the name on the order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get the active Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Debugging: Check if session is working
if session:
    st.write("Snowflake session established.")
else:
    st.write("Error establishing session.")

try:
    # Retrieve available fruits from the Snowflake table
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()

    # Check the first few rows of the dataframe
    st.write(my_dataframe.head())  # Show a sample of the data to confirm it's loaded
except Exception as e:
    st.error(f"Error retrieving data from Snowflake: {e}")
    st.stop()

# Multiselect for choosing ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=my_dataframe['FRUIT_NAME'].tolist(),  # Convert column to a list for selection
    max_selections=5
)

if ingredients_list:    
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on = my_dataframe.loc[my_dataframe['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
        st.json(smoothiefroot_response.json())  # Show JSON response directly

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
