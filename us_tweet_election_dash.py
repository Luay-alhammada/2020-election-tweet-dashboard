#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="US Election Dash",
    page_icon="🗽", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

#111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

@st.cache_data
def load_data(url):
    return pd.read_csv(url)

# Use raw URLs from GitHub
merged_df = load_data('https://raw.githubusercontent.com/Luay-alhammada/2020-election-tweet-dashboard/refs/heads/main/usa_tweet.csv')
sentiment_distribution = load_data('https://raw.githubusercontent.com/Luay-alhammada/2020-election-tweet-dashboard/refs/heads/main/sentiment_distribution.csv')
user = load_data('https://raw.githubusercontent.com/Luay-alhammada/2020-election-tweet-dashboard/refs/heads/main/usa_user.csv')
data_info = pd.read_csv('https://raw.githubusercontent.com/Luay-alhammada/2020-election-tweet-dashboard/refs/heads/main/Data%20Info.csv')

# Center-align the title using HTML
title = "<h1 style='text-align:center; font-size: 30px;'>Tweets Analysis of the 2020 U.S. Presidential Election </h1>"

# Display the title in Streamlit
st.markdown(title, unsafe_allow_html=True)




col1, col2,col3 = st.columns([1.5,5,1.5]) 
#  unique dates list
with col1:
  st.markdown('<h1 style="color: IndianRed;font-size: 30px;">Map Configuration</h1>', unsafe_allow_html=True)
# Dropdown for date selection outside the sidebar
  date_options = ["All Days"] + list(merged_df['date'].unique())
  selected_date = st.selectbox("Select Date", date_options)
  input_color = st.selectbox("Select Metrics ", ['tweet_count', 'total_likes', 'sentiment_avg', 'total_retweets', 'total_followers'])

# Filter the data based on the selected date
if selected_date == "All Days":
    filtered_data = merged_df.groupby("states_code").agg({
        'tweet_count': 'sum',
        'total_likes': 'sum',
        'sentiment_avg': 'mean',  # Average sentiment
        'total_retweets': 'sum',
        'total_followers':'sum',
        'state': 'first',  # first state name 
        'most_common_issues': lambda x: x.mode()[0] if not x.mode().empty else None,  # Most common issue
        'top_hashtags': lambda x: x.mode()[0] if not x.mode().empty else None,  # Most liked hashtag
    }).reset_index()
else:
    filtered_data = merged_df[merged_df['date'] == selected_date]

# Set color scale
color_scale = "RdBu" if input_color == 'sentiment_avg' else "Blues"
domain_mid = 0 if input_color == 'sentiment_avg' else None

# Function to create the choropleth map
def make_usa_map(filtered_data, input_color, color_scale, domain_mid, selected_date):
    fig = go.Figure(go.Choropleth(
        locations=filtered_data['states_code'],  # State codes
        z=filtered_data[input_color],  # Data for the color scale
        locationmode="USA-states",
        colorscale=color_scale,
        colorbar_title=input_color.replace("_", " ").title(),
        hovertext=[
            f"State: {row['state']}<br>"
            f"Tweet Count: {row['tweet_count']:,}<br>"
            f"Total Likes: {row['total_likes']:,}<br>"
            f"followers count: {row['total_followers']:,}<br>"
            f"Sentiment Avg: {row['sentiment_avg']:.3f}<br>"
            f"Top issue: {row['most_common_issues']}<br>"
            f"Top Hashtag by likes: {row['top_hashtags']}"
            for _, row in filtered_data.iterrows()
        ],
        hoverinfo="text",
        showscale=True,
        zmid=domain_mid
    ))

    fig.update_geos(
        scope='usa',
        projection=go.layout.geo.Projection(type='albers usa')
    )
    # Update the title dynamically
    # title_suffix = "All Days" if selected_date == "All Days" else f"on {selected_date}"
    fig.update_layout(
        # title_text=f"USA Map for {input_color.replace('_', ' ').title()} {title_suffix}",
        # title_x=0.3,
        
        geo_scope='usa',
        width=600,
        height=500,
        margin={"r": 0, "t": 50, "l": 0, "b": 22}
    )

    return fig
# Display the map

with col2:
    fig = make_usa_map(filtered_data, input_color, color_scale, domain_mid, selected_date)
    st.plotly_chart(fig, use_container_width=True)

with col3:
       
    st.markdown('<h1 style="color: IndianRed;font-size: 30px;">Dataset Summary</h1>', unsafe_allow_html=True)
    html_table = data_info.to_html(index=False, border=0)
    # Display the HTML table
    st.markdown(html_table, unsafe_allow_html=True)

#2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222
# Multi-select for candidates
st.markdown('<h1 style="color: IndianRed;font-size: 30px;">Select Candidates</h1>', unsafe_allow_html=True)
selected_candidates = []
for candidate in sentiment_distribution['candidates'].unique():
    if st.checkbox(candidate):
        selected_candidates.append(candidate)

# Filter dataframe based on selected candidates
if selected_candidates:  # Check if at least one candidate is selected
    filtered_df = sentiment_distribution[sentiment_distribution['candidates'].isin(selected_candidates)]
else:
    filtered_df = sentiment_distribution 


# Generate Word Cloud
words = ' '.join(filtered_df['top_issues'])
if words.strip():
    wordcloud = WordCloud(width=400, height=200, background_color='white').generate(words)
else:
    wordcloud = None

# Add custom CSS for layout and styling
# Add custom CSS for layout and styling
st.markdown("""
    <style>
        .center-text {
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
            height: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# Layout: Define columns
col1, col2, col3 = st.columns([1, 1.5, 1])

# Word Cloud Visualization
with col1:
    if wordcloud:
        st.markdown('<h1 style="color: IndianRed;font-size: 30px;">Top Topics</h1>', unsafe_allow_html=True)
        # st.markdown('<div class="center-text"><h3>Top Topics</h3></div>', unsafe_allow_html=True)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        fig.tight_layout()
        st.pyplot(fig)
    else:
        st.markdown('<div class="center-text"><h3>No Data for Word Cloud</h3></div>', unsafe_allow_html=True)

# Pie Chart Visualization
with col2:
    st.markdown('<h1 style="color: IndianRed;font-size: 30px;  text-align: center;">Sentiment Distribution</h1>', unsafe_allow_html=True)
    # st.markdown('<div class="center-text"><h3>Sentiment Distribution</h3></div>', unsafe_allow_html=True)
    pie_chart = px.pie(
        filtered_df,
        names='sentiment category',
        values='tweet_count',
        color='sentiment category',
        color_discrete_map={
            'positive': 'darkgreen',
            'negative': 'crimson',
            'neutral': 'snow'
        }
    )
    pie_chart.update_layout(height=400)
    st.plotly_chart(pie_chart, use_container_width=True)

# Bar Chart Visualization
with col3:
    st.markdown('<h1 style="color: IndianRed;font-size: 30px;  text-align: center;">Engagement Metrics</h1>', unsafe_allow_html=True)
    # st.markdown('<div class="center-text"><h3>Engagement Metrics</h3></div>', unsafe_allow_html=True)
    bar_chart = px.bar(
        filtered_df,
        x='sentiment category',
        y=['likes', 'retweet_count', 'tweet_count'],
        barmode='group',
        color_discrete_sequence=['#4169E1', '#1E90FF', '#87CEEB']
    )
    bar_chart.update_layout(
        height=400,
        xaxis_title="Sentiment Category",
        yaxis_title="Counts",
        legend_title="Metrics"
    )
    st.plotly_chart(bar_chart, use_container_width=True)


# 33333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333

user_cleaned = user.dropna(subset=['before_23_oct_sentiment', 'after_23_oct_sentiment'])

# Add a filter for candidates
candidates_options = user_cleaned['candidates'].unique()
selected_candidates = st.radio(
    "Select Candidate(s)", 
    candidates_options, 
    index=0
)

# Filter selected candidates
filtered_data = user_cleaned[user_cleaned['candidates'] == selected_candidates]

# Update your transition matrix and other visualizations based on the filtered data
transition_matrix_filtered = pd.crosstab(
    filtered_data['before_23_oct_sentiment'],
    filtered_data['after_23_oct_sentiment'],
    rownames=['Before October 23, 2020'],
    colnames=['After October 23, 2020']
)

# Normalize by row to get percentages for the filtered data
transition_matrix_percentage_filtered = transition_matrix_filtered.div(transition_matrix_filtered.sum(axis=1), axis=0) * 100

col1, col2,col3 = st.columns([4, 1,1])

with col1:
    st.markdown('<h1 style="color: IndianRed;font-size: 30px;">Users Sentiment Transitions Before & After Debate Day</h1>', unsafe_allow_html=True)
    # st.markdown('<div><h4>Users Sentiment Transitions Before & After Debate Day</h4></div>', unsafe_allow_html=True)
    
    # Prepare data for the Sankey diagram with the filtered data
    source = [
        0, 0, 0,  # Transitions from Negative (row 0 in transition_matrix)
        1, 1, 1,  # Transitions from Neutral (row 1)
        2, 2, 2   # Transitions from Positive (row 2)
    ]
    target = [
        3, 4, 5,  # To Negative, Neutral, Positive
        3, 4, 5,
        3, 4, 5
    ]
    values = transition_matrix_percentage_filtered.values.flatten()  # Flatten the matrix into a list
    
    # Labels for the nodes
    labels = [
        "Before: Negative", "Before: Neutral", "Before: Positive",  # Source labels
        "After: Negative", "After: Neutral", "After: Positive"      # Target labels
    ]
    
    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            label=labels,
            color=['crimson', 'snow', 'darkgreen'] * 2,  # Colors for before and after
            
        ),
        link=dict(
            
            source=source,
            target=target,
            value=values,
            
        )
    )])
    
    fig.update_layout(
        
        width=800,  # Set the width of the Sankey diagram (adjust as needed)
        height=500  # Set the height of the Sankey diagram (adjust as needed)
    )

    st.plotly_chart(fig)

