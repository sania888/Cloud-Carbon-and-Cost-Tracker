import plotly.express as px
import pandas as pd

def interactive_monthly_trend(data):
    """
    Create an interactive Plotly line chart showing monthly Cost and Emissions.
    """
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise TypeError("Expected data as dict or pandas DataFrame")
    
    if 'Month' not in data.columns:
        raise KeyError("Expected 'Month' column not found in dataset.")


    # Ensure Month column is datetime
    data['Month'] = pd.to_datetime(data['Month'])
    data = data.sort_values('Month')

    # Aggregate monthly data
    monthly_summary = data.groupby('Month')[['Cost ($)', 'Emissions (kgCO2e)']].sum().reset_index()

    # Reshape for Plotly
    melted = monthly_summary.melt(
        id_vars='Month',
        value_vars=['Cost ($)', 'Emissions (kgCO2e)'],
        var_name='Metric',
        value_name='Value'
    )

    # Create line chart
    fig = px.line(
        melted,
        x='Month',
        y='Value',
        color='Metric',
        title="Monthly Cost and Emissions Over Time",
        markers=True
    )

    # Add slider and range selector
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ]
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        template="plotly_white"
    )

    fig.show()
    return fig
