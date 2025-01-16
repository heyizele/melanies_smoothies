import streamlit as st
import requests
import pandas as pd

# Title for the app
st.title("Smoothie Ordering App")

# User input for ingredients
ingredients_input = st.text_input("Enter ingredients for your smoothie (comma-separated):")

if ingredients_input:
    # Split the input into a list of ingredients
    ingredients_list = [ingredient.strip() for ingredient in ingredients_input.split(",")]
    
    st.write("Your selected ingredients are:")
    st.write(ingredients_list)
    
    # Loop through the ingredients and fetch data for each
    for fruit_chosen in ingredients_list:
        st.write(f"Fetching data for {fruit_chosen}...")
        
        # Fetch data from the API
        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
            
            if response.status_code == 200:
                # Display the data in a dataframe
                fruit_data = response.json()
                st.dataframe(data=fruit_data, use_container_width=True)
            else:
                st.error(f"Failed to fetch data for {fruit_chosen}. Status code: {response.status_code}")
        
        except Exception as e:
            st.error(f"An error occurred while fetching data for {fruit_chosen}: {e}")

# Option to insert data
time_to_insert = st.checkbox("Ready to insert order?")
if time_to_insert:
    st.success("Your order has been successfully placed!")
