import streamlit as st
import pandas as pd
import os
import matplotlib as plt



# Set the root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the path to your data files
fantasy_projections_path = os.path.join(ROOT_DIR, 'simulation_results', 'fantasy_projections.csv')
ipl_prediction_path = os.path.join(ROOT_DIR, 'simulation_results', 'win_probability.csv')

# Load the datasets
fantasy_projections_df = pd.read_csv(fantasy_projections_path)
ipl_prediction_df = pd.read_csv(ipl_prediction_path)

st.set_page_config(
    page_title="Fantasy Projection",
    page_icon="🏏",
    layout="wide"
)



# Sidebar Filters
st.sidebar.header('Filters')
# Name Filter
unique_names = fantasy_projections_df['name'].sort_values().unique()
selected_name = st.sidebar.multiselect('Name', unique_names)

# Match Number Filter
unique_match_numbers = sorted(fantasy_projections_df['matchnumber'].unique())
selected_match_number = st.sidebar.selectbox('Match Number', ['All'] + unique_match_numbers, index=0)

# Role Filter
unique_roles = fantasy_projections_df['position'].sort_values().unique()
selected_role = st.sidebar.multiselect('Position', unique_roles)

# Team Filter
unique_teams = fantasy_projections_df['team'].sort_values().unique()
selected_team = st.sidebar.multiselect('Team', unique_teams)

# Initialize condition as True for all rows
condition = pd.Series([True] * len(fantasy_projections_df), index=fantasy_projections_df.index)

# Apply filters
if selected_name:
    condition &= fantasy_projections_df['name'].isin(selected_name)
if selected_match_number != 'All':
    condition &= fantasy_projections_df['matchnumber'] == int(selected_match_number)
if selected_role:
    condition &= fantasy_projections_df['position'].isin(selected_role)
if selected_team:
    condition &= fantasy_projections_df['team'].isin(selected_team)

filtered_df = fantasy_projections_df.loc[condition]

# Prepare the player stats with total fantasy points
player_stats = filtered_df.groupby(['name', 'team', 'position']).agg(
    total_fpoints=('fpoints_projected', lambda x: x.mean() * 14),
).reset_index()

# Sort by total_fpoints in descending order
player_stats = player_stats.sort_values(by='total_fpoints', ascending=False)


tab1,tab2=st.tabs(['Projection','Team Win Probability'])



with tab1:

    # Styled Title
    st.markdown(f"""
    <div style="background-color:#800080; color:white; text-align:center; padding:15px; border-radius:10px;">
        <div style="font-size:30px;"><b>Fantasy Projection</b></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


    # Using columns to create space between tables
    col1, spacer, col2 = st.columns([2.5, 0.1, 4])

    with col1:


        st.markdown(f"""
            <div style="background-color:#800080; color:white; text-align:center; padding:10px; border-radius:10px;">
                <div style="font-size:20px;"><b>Season Projection</b></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        # Apply custom styling to the DataFrame
        st.dataframe(player_stats.style.format({'total_fpoints': "{:.2f}"})
                    .background_gradient(cmap='coolwarm')
                    .set_properties(**{'text-align': 'left', 'border': '1px solid white'}), height=600,use_container_width=True,hide_index=True)

    with col2:

        st.markdown(f"""
        <div style="background-color:#800080; color:white; text-align:center; padding:10px; border-radius:10px;">
            <div style="font-size:20px;"><b>Match Projection</b></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
        filtered_df1 = filtered_df
        filtered_df1 = filtered_df1[['matchnumber','name', 'team', 'position', 'fpoints_projected','runs_projected','wickets_projected','opponent']].sort_values(by=['matchnumber','fpoints_projected'], ascending=[True,False])
        filtered_df1['matchnumber']=(filtered_df1['matchnumber']).astype(int)
        filtered_df1['runs_projected']=filtered_df1['runs_projected'].round().astype(int)
        filtered_df1['wickets_projected']=filtered_df1['wickets_projected'].round().astype(int)
        
        # Apply custom styling to the DataFrame
        st.dataframe(filtered_df1.style.format({'fpoints_projected': "{:.2f}"})
                    .background_gradient(cmap='coolwarm', subset=['fpoints_projected'])
                    .set_properties(**{'text-align': 'left', 'border': '1px solid white'})
                    , height=600, use_container_width=True, hide_index=True)

        # Custom CSS to enhance the Streamlit default styles
        st.markdown("""
        <style>
            .css-18e3th9 {
                flex: 1;
            }
            .st-cx {
                max-width: 100%;
            }
            .st-bx {
                color: #f63366;
            }
            .dataframe { 
                border: none;
            }
            .dataframe th {
                font-size: 16px;
            }
            .dataframe td {
                font-size: 14px;
            }
        </style>
        """, unsafe_allow_html=True)


with tab2:
    # Adjusted function to match the current DataFrame structure
    def highlight_win_probability(row):
        # Background colors
        higher_color_bg = 'background-color: #006400;'  # Soft Green
        lower_color_bg = 'background-color: #8B0000;'   # Soft Red

        # Text color
        text_color = 'color: #FFFFFF;'  # Light gray for better visibility
        font_weight = 'font-weight: bold;'  # Bold font

        # Combining background and text color styles
        higher_style = f'{higher_color_bg} {text_color} {font_weight}'
        lower_style = f'{lower_color_bg} {text_color} {font_weight}'

        if row['Home_Team_win_percentage'] > row['Away_Team_win_percentage']:
            return ['', '', '', higher_style, lower_style]
        else:
            return ['', '', '', lower_style, higher_style]

    # Filter and rename columns as before
    ipl_prediction_df = ipl_prediction_df[['match_number', 'team1name', 'team2name', 'team1_win_percentage', 'team2_win_percentage']]\
        .rename(columns={
            'match_number': 'match',
            'team1name': 'HomeTeam',
            'team2name': 'AwayTeam',
            'team1_win_percentage': 'Home_Team_win_percentage',
            'team2_win_percentage': 'Away_Team_win_percentage'
        })
    ipl_prediction_df['Home_Team_win_percentage']=ipl_prediction_df['Home_Team_win_percentage'].astype(int)
    ipl_prediction_df['Away_Team_win_percentage']=ipl_prediction_df['Away_Team_win_percentage'].astype(int)

    # Apply the styling
    styled_df = ipl_prediction_df.style.apply(highlight_win_probability, axis=1)

    # Display in Streamlit
    st.dataframe(styled_df, height=1200, use_container_width=False,hide_index=True)

