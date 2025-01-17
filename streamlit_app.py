# Import Python packages
import streamlit as st
from snowflake.snowpark.session import Session
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Input for smoothie name
name_on_order = st.text_input('Name of Smoothie:')
st.write('The name of your Smoothie will be:', name_on_order)

# Connect to Snowflake session
try:
    # Read Snowflake connection details from Streamlit secrets
    conn_params = st.secrets["connections"]["snowflake"]
    session = Session.builder.configs(conn_params).create()

    # Ensure correct database and schema are used
    session.sql("USE DATABASE smoothies").collect()
    session.sql("USE SCHEMA public").collect()

    # Fetch fruit options from the database
    try:
        my_dataframe = session.table("fruit_options").select(col('FRUIT_NAME')).collect()
        fruit_options = [row['FRUIT_NAME'] for row in my_dataframe]  # Extract fruit names as a list
    except Exception as e:
        st.error(f"Error fetching fruit options: {e}")
        fruit_options = []

    # Allow the user to select up to 5 ingredients
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        fruit_options,
        max_selections=5  # Enforce a maximum selection of 5
    )

    if ingredients_list:
        # Create ingredients string and display nutrition information for each selected fruit
        ingredients_string = ''
        for fruit_chosen in ingredients_list:
            ingredients_string += fruit_chosen + ', '

            # Display the subheader for the fruit
            st.subheader(f"{fruit_chosen} Nutrition Information")
            
            # Make the API call for each fruit
            try:
                smoothiefroot_response = requests.get(
                    f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}"
                )
                smoothiefroot_response.raise_for_status()  # Raise exception for HTTP errors
                # Display the nutrition information in a table
                st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching nutrition info for {fruit_chosen}: {e}")

        # Corrected SQL statement with explicit column names
        ingredients_string = ingredients_string.strip(', ')  # Remove trailing comma
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
                st.error(f"Error submitting the order: {e}")
    else:
        st.info("Select up to 5 ingredients to create your smoothie.")

except Exception as e:
    st.error(f"Error connecting to Snowflake: {e}")
