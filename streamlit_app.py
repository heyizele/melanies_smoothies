# Import python packages
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
st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# New Input: Radio button for the 'order_filled' status
order_filled = st.radio("Mark order as filled?", options=[False, True], index=0)
st.write(f"Order will be marked as: **{'Filled' if order_filled else 'Not Filled'}**")

# Get the active Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Retrieve available fruits from the Snowflake table
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).to_pandas()
except Exception as e:
    st.error(f"Error retrieving fruit options: {e}")
    st.stop()

# Multiselect for choosing ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=my_dataframe['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Combine selected ingredients into a single string

    for fruit_chosen in ingredients_list:
        # Retrieve the 'SEARCH_ON' value for the selected fruit
        try:
            search_on = my_dataframe.loc[my_dataframe['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        except IndexError:
            search_on = "Not found"

        # Nutrition Information Section
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            if smoothiefroot_response.status_code == 200:
                nutrition_data = pd.DataFrame(smoothiefroot_response.json())  # Convert JSON response to DataFrame
                st.dataframe(nutrition_data, use_container_width=True)  # Display as a table
            else:
                st.write(f"⚠️ No nutrition information found for {fruit_chosen}.")
        except Exception as e:
            st.error(f"Error retrieving nutrition data for {fruit_chosen}: {e}")

    # Submit order button
    if st.button('Submit Order'):
        # Construct the SQL INSERT statement
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
            VALUES ('{ingredients_string}', '{name_on_order}', {order_filled})
        """
        try:
            # Execute the SQL query
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"Error occurred while submitting the order: {e}")

