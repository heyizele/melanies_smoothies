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
        # Convert the Snowpark DataFrame to a Pandas DataFrame for easier handling
        pd_df = session.table("fruit_options").to_pandas()

        # Use Pandas DataFrame to get fruit names and their corresponding search terms
        fruit_options = pd_df['FRUIT_NAME'].tolist()
    except Exception as e:
        st.error(f"Error fetching fruit options: {e}")
        pd_df = None
        fruit_options = []

    # Allow the user to select up to 5 ingredients
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:',
        fruit_options,
        max_selections=5  # Enforce a maximum selection of 5
    )

    if ingredients_list:
        # Variables to track missing fruits
        missing_fruits = []

        # Loop through selected fruits to fetch nutrition info
        for fruit_chosen in ingredients_list:
            # Use the SEARCH_ON value for the API call
            try:
                search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
                st.subheader(f"{fruit_chosen} Nutrition Information")

                # Make the API call using the search term
                fruityvice_response = requests.get(
                    f"https://fruityvice.com/api/fruit/{search_on}"
                )
                fruityvice_response.raise_for_status()  # Raise exception for HTTP errors

                # Display the nutrition information in a table
                st.dataframe(data=fruityvice_response.json(), use_container_width=True)
            except (requests.exceptions.RequestException, IndexError):
                # If the fruit isn't in the database, display a warning
                st.warning(f"Information for '{fruit_chosen}' could not be fetched. It will still be included in your smoothie.")
                missing_fruits.append(fruit_chosen)

        # Combine the chosen ingredients (including missing fruits) into a string
        ingredients_string = ', '.join(ingredients_list)

        # Corrected SQL statement with explicit column names
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """

        # Submit the order
        if st.button('Submit Order'):
            try:
                session.sql(my_insert_stmt).collect()
                # Personalized success message
                st.success(
                    f"Your Smoothie '{name_on_order}' is ordered with the following ingredients: {ingredients_string}!",
                    icon="✅"
                )
                # Display missing fruits, if any
                if missing_fruits:
                    st.info(f"The following fruits have missing nutritional data but are still included in your smoothie: {', '.join(missing_fruits)}")
            except Exception as e:
                st.error(f"Error submitting the order: {e}")
    else:
        st.info("Select up to 5 ingredients to create your smoothie.")

except Exception as e:
    st.error(f"Error connecting to Snowflake: {e}")
