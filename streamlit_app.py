# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark import Session

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Input for smoothie name
name_on_order = st.text_input('Name of Smoothie:')
st.write('The name of your Smoothie will be:', name_on_order)

# Connect to Snowflake session
try:
    cnx = st.connection("snowflake")
    session = cnx.session
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
    fruit_options = [row['FRUIT_NAME'] for row in my_dataframe]  # Extract fruit names as a list
except Exception as e:
    st.error(f"Error connecting to Snowflake: {e}")
    st.stop()

# Allow the user to select up to 5 ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=5  # Enforce a maximum selection of 5
)

if ingredients_list:
    # Combine the ingredients into a string
    ingredients_string = ', '.join(ingredients_list)

    # Corrected SQL statement with explicit column names
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Submit the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            # Personalized success message
            st.success(
                f"Your Smoothie '{name_on_order}' is ordered with the following ingredients: {ingredients_string}!",
                icon="✅"
            )
        except Exception as e:
            st.error(f"Error inserting the order: {e}")
else:
    st.info("Select up to 5 ingredients to create your smoothie.")
