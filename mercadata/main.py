import os
from turtle import st

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



def load_csv_data(csv_path):
    if os.path.exists(csv_path):
        try:
            data = pd.read_csv(csv_path)
            data["fecha"] = pd.to_datetime(data["fecha"], format="%d/%m/%Y %H:%M", dayfirst=True)
            data.set_index("fecha", inplace=True)
            return data
        except Exception as e:
            st.error(f"Error al leer el archivo CSV: {e}")
            return None
    else:
        st.error(f"Archivo {csv_path} no encontrado.")
        return None


# Function to display metrics
def display_metrics(data, filtered_data_by_month, filtered_data_by_categories):
    total_spent = data["precio"].sum()
    total_purchases = data["identificativo de ticket"].nunique()
    avg_spent_per_purchase = data.groupby("identificativo de ticket")["precio"].sum().mean()
    category_with_highest_spent = data.groupby("categoría")["precio"].sum().idxmax()
    total_items_sold = data['item'].nunique()
    avg_spent_per_month = data["precio"].resample('M').sum().mean()
    total_tickets_per_month = data.groupby(data.index.to_period('M')).size().mean()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Gasto Total", value=f"€{total_spent:.2f}")
        st.metric(label="Gasto Promedio por Compra", value=f"€{avg_spent_per_purchase:.2f}")
        st.metric(label="Número Total de Compras", value=total_purchases)
        st.metric(label="Items Vendidos", value=total_items_sold)

    with col2:
        st.metric(label="Categoría con Mayor Gasto", value=category_with_highest_spent)
        st.metric(label="Gasto Promedio Mensual", value=f"€{avg_spent_per_month:.2f}")
        st.metric(label="Tickets por Mes", value=f"{total_tickets_per_month:.2f}")

    with col3:
        st.metric(label="Total Gastado en el Mes Seleccionado",
                  value=f"€{filtered_data_by_month['precio'].sum():.2f}")
        st.metric(label="Número de Compras en el Mes Seleccionado",
                  value=filtered_data_by_month['identificativo de ticket'].nunique())
        st.metric(label="Categoría con Mayor Gasto en el Mes Seleccionado",
                  value=filtered_data_by_month.groupby("categoría")["precio"].sum().idxmax())


# Function to plot charts
def plot_charts(data, filtered_data_by_month):
    col1, col2, col3 = st.columns(3)

    with col1:
        total_price_per_category = data.groupby("categoría")["precio"].sum().reset_index()
        fig_pie = px.pie(total_price_per_category, values='precio', names='categoría',
                         title='Distribución del Gasto por Categoría')
        st.plotly_chart(fig_pie)

    with col2:
        monthly_expense = data["precio"].resample('M').sum().reset_index()
        fig_bar = px.bar(monthly_expense, x='fecha', y='precio', labels={'fecha': 'Mes', 'precio': 'Gasto (€)'})
        st.plotly_chart(fig_bar)

    with col3:
        avg_price_per_category = data.groupby("categoría")["precio"].mean().reset_index().sort_values(
            by="precio", ascending=False)
        fig_bar_avg = px.bar(avg_price_per_category, x='categoría', y='precio',
                             labels={'precio': 'Precio Medio (€)'})
        st.plotly_chart(fig_bar_avg)


# Function to plot detailed analysis
def plot_detailed_analysis(data):
    col1, col2 = st.columns(2)

    with col1:
        daily_expense = data["precio"].resample('D').sum().reset_index()
        fig_line = px.line(daily_expense, x='fecha', y='precio',
                           labels={'fecha': 'Fecha', 'precio': 'Gasto (€)'})
        st.plotly_chart(fig_line)

    with col2:
        top_items = data.groupby('item')['precio'].sum().nlargest(10).reset_index()
        fig_top_items = px.bar(top_items, x='item', y='precio', labels={'item': 'Item', 'precio': 'Gasto (€)'})
        st.plotly_chart(fig_top_items)


# Function to display heatmap
def plot_heatmap(data):
    st.subheader("Heatmap del Gasto por Día y Hora")
    data['day_of_week'] = data.index.dayofweek
    data['hour_of_day'] = data.index.hour
    heatmap_data = data.pivot_table(values='precio', index='hour_of_day', columns='day_of_week', aggfunc='sum',
                                    fill_value=0)
    fig_heatmap = go.Figure(data=go.Heatmap(z=heatmap_data.values,
                                            x=['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado',
                                               'Domingo'], y=list(range(24)), colorscale='Viridis'))
    fig_heatmap.update_layout(xaxis_title='Día de la Semana', yaxis_title='Hora del Día')
    st.plotly_chart(fig_heatmap)


# Main function to execute the program
def main():
    csv_path = "data/mercadata.csv"
    logo_path = "images/logo.png"  # Adjust according to your logo file path

    # # Display the logo
    # if os.path.exists(logo_path):
    #     st.image(logo_path, width=600)
    # else:
    #     st.warning(f"Logo no encontrado en {logo_path}")

    # Load and process CSV data
    data = load_csv_data(csv_path)
    if data is not None and not data.empty:
        # Filter and display metrics and plots
        month_start_dates = data.index.to_period("M").to_timestamp().drop_duplicates().sort_values()
        selected_month_start = st.selectbox("Selecciona el mes", month_start_dates.strftime('%Y-%m'), index=0)
        selected_month_start = pd.Timestamp(selected_month_start)
        filtered_data_by_month = data[data.index.to_period("M").start_time == selected_month_start]

        selected_category = st.selectbox("Selecciona la categoría", data["categoría"].unique())
        filtered_data_by_categories = data[data["categoría"] == selected_category]

        display_metrics(data, filtered_data_by_month, filtered_data_by_categories)
        plot_charts(data, filtered_data_by_month)
        plot_detailed_analysis(data)
        plot_heatmap(data)


if __name__ == "__main__":
    main()