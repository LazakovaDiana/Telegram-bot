import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Данные для примера
df_projects = pd.DataFrame({
    'Задача': ['Задача А', 'Задача Б', 'Задача В'],
    'Начало': ['2024-12-12', '2024-12-12', '2024-12-12'],
    'Окончание': ['2024-12-12', '2024-12-12', '2024-12-12'],
    'Статус': ['Активный', 'Завершено', 'Приостановлено'],
    'Прогресс': [30, 70, 20]
})

# Инициализация приложения
app = dash.Dash(__name__)

# Макет приложения
app.layout = html.Div([
    html.H1('Процент выполненных задач'),
    dcc.Dropdown(
        id='project-dropdown',
        options=[{'label': i, 'value': i} for i in df_projects['Задача'].unique()],
        value=df_projects['Задача'].unique()[0],
        clearable=False
    ),
    html.Br(),
    html.Div(id='project-details'),
    dcc.Graph(id='progress-graph')
])


# Обработчик событий для обновления информации о проекте
@app.callback(
    Output('project-details', 'children'),
    Input('project-dropdown', 'value')
)
def update_details(selected_project):
    filtered_df = df_projects.query("Задача == @selected_project")
    details = []
    for _, row in filtered_df.iterrows():
        details.append(html.P(f"Начало: {row['Начало']}"))
        details.append(html.P(f"Окончание: {row['Окончание']}"))
        details.append(html.P(f"Статус: {row['Статус']}"))

    return details


# Обработчик событий для обновления графика прогресса
@app.callback(
    Output('progress-graph', 'figure'),
    Input('project-dropdown', 'value')
)
def update_progress_graph(selected_project):
    filtered_df = df_projects.query("Задача == @selected_project")
    fig = px.bar(filtered_df, x='Задача', y='Прогресс', color='Статус', title='Прогресс выполнения работ')
    return fig


# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)