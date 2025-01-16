import streamlit as st
import requests
import pandas as pd

# App Header
st.title("🍓 Smoothie Ordering App")
st.subheader("Customize your smoothie by selecting your favorite ingredients!")

# Smoothie Ingredients Input
ingredients_input = st.text_input(
    "Enter ingredients for your smoothie (comma-separated):",
    placeholder="e.g., banana, strawberry, mango"
)

# Display ingredient list when user inputs data
if ingredients_input:
    ingredients_list = [ingredient.strip() for ingredient in ingredients_input.split(",")]
    
    st.write("### Selected Ingredients:")
    st.write(", ".join(ingredients_list))

    # Fetch and display data for each ingredient
    st.write("### Nutritional Information:")
    for fruit_chosen in ingredients_list:
        st.write(f"Fetching data for **{fruit_chosen}**...")
        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
            
            if response.status_code == 200:
                fruit_data = response.json()
                fruit_df = pd.DataFrame([fruit_data])  # Convert JSON response to DataFrame
                st.dataframe(fruit_df, use_container_width=True)
            else:
                st.warning(f"No data available for **{fruit_chosen}** (Status code: {response.status_code})")
        
        except Exception as e:
            st.error(f"Error fetching data for **{fruit_chosen}**: {e}")

# Order Placement Section
st.divider()
st.write("### Ready to Place Your Order?")
if st.button("Place Order"):
    if ingredients_input:
        st.success("✅ Your order has been successfully placed!")
        st.balloons()
    else:
        st.error("❌ Please add ingredients to place your order.")

# Footer
st.divider()
st.caption("Made with ❤️ using Streamlit")
