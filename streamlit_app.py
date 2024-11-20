# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
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
#session = get_active_session()

# Retrieve available fruits from the Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()

# Multiselect for choosing ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=my_dataframe['FRUIT_NAME'].tolist(),  # Convert column to a list for selection
    max_selections=5
)

if ingredients_list:        
    # Join selected fruits into a single string
    ingredients_string = ', '.join(ingredients_list)

    # Debugging statement (optional)
    # st.write(f"Selected ingredients: {ingredients_string}")

    # Construct the SQL INSERT statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Debugging statement (optional)
    # st.write(f"SQL Query: {my_insert_stmt}")

    # Submit order button
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        try:
            # Execute the SQL query
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"Error occurred: {e}")

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response).json())
sf_df = st.dataframe(data=smothiefroot_response.json(), use_container_width=True)



