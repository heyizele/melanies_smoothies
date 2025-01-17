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
        # Select both FRUIT_NAME and SEARCH_ON for display and API lookup
        my_dataframe = session.table("fruit_options").select(
            col('FRUIT_NAME'), col('SEARCH_ON')
        ).collect()

        # Map FRUIT_NAME to SEARCH_ON for easy lookup
        fruit_map = {row['FRUIT_NAME']: row['SEARCH_ON'] for row in my_dataframe}
        fruit_options = list(fruit_map.keys())  # Extract display names
    except Exception as e:
        st.error(f"Error fetching fruit options: {e}")
        fruit_options = {}
        fruit_map = {}

    # Allow the user to select up to 5 ingredients
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        fruit_options,
        max_selections=5  # Enforce a maximum selection of 5
    )

    if ingredients_list:
        # Variables to track valid ingredients and errors
        valid_ingredients = []
        missing_fruits = []

        # Loop through selected fruits to fetch nutrition info
        for fruit_chosen in ingredients_list:
            # Use the SEARCH_ON value for the API call
            search_term = fruit_map.get(fruit_chosen, fruit_chosen)  # Default to name if not mapped
            st.subheader(f"{fruit_chosen} Nutrition Information")  # Show the user-friendly name

            try:
                # Make the API call using the search term
                smoothiefroot_response = requests.get(
                    f"https://my.smoothiefroot.com/api/fruit/{search_term.lower()}"
                )
                smoothiefroot_response.raise_for_status()  # Raise exception for HTTP errors

                # Display the nutrition information in a table
                st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
                valid_ingredients.append(fruit_chosen)  # Add to valid ingredients list
            except requests.exceptions.RequestException:
                # If the fruit isn't in the database, display a warning and track it
                st.warning(f"Information for '{fruit_chosen}' could not be fetched. It will not be included in your smoothie.")
                missing_fruits.append(fruit_chosen)

        # Combine the valid ingredients into a string
        ingredients_string = ', '.join(valid_ingredients)

        if valid_ingredients:
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
                    # Display missing fruits, if any
                    if missing_fruits:
                        st.info(f"The following fruits were excluded from your smoothie due to missing data: {', '.join(missing_fruits)}")
                except Exception as e:
                    st.error(f"Error submitting the order: {e}")
        else:
            st.error("No valid fruits were selected for your smoothie. Please choose different fruits.")

    else:
        st.info("Select up to 5 ingredients to create your smoothie.")

except Exception as e:
    st.error(f"Error connecting to Snowflake: {e}")
