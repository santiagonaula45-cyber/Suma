import streamlit as st

# Título y diseño
st.title("Calculadora Básica de Suma")
st.write("Ingresa dos números para obtener su suma:")

# Entradas de usuario
num1 = st.number_input("Primer número", value=0)
num2 = st.number_input("Segundo número", value=0)

# Botón y lógica
if st.button("Sumar"):
    resultado = num1 + num2
    st.success(f"El resultado es: {resultado}")