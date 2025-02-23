from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import plotly.express as px
import json

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the Titanic dataset
df = pd.read_csv("titanic.csv")

class Query(BaseModel):
    text: str

# Helper functions for different analyses
def analyze_survival_rate():
    survived = df['Survived'].sum()
    total = len(df)
    rate = (survived / total * 100)
    
    fig = px.pie(
        values=[survived, total - survived],
        names=['Survived', 'Did Not Survive'],
        title='Overall Survival Rate',
        color_discrete_sequence=['#4f46e5', '#e5e7eb']
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return {
        'text': f"Out of {total} passengers, {survived} survived, resulting in a survival rate of {rate:.1f}%.",
        'plot': json.loads(fig.to_json())
    }

def analyze_by_class():
    class_stats = df.groupby('Pclass')['Survived'].agg(['count', 'sum']).reset_index()
    class_stats['rate'] = class_stats['sum'] / class_stats['count'] * 100
    
    fig = px.bar(
        class_stats,
        x='Pclass',
        y='rate',
        title='Survival Rate by Passenger Class',
        labels={'Pclass': 'Passenger Class', 'rate': 'Survival Rate (%)'},
        color_discrete_sequence=['#4f46e5']
    )
    
    text = "\n".join([
        f"Class {row['Pclass']}: {row['rate']:.1f}% survival rate ({int(row['sum'])} out of {int(row['count'])})"
        for _, row in class_stats.iterrows()
    ])
    
    return {'text': text, 'plot': json.loads(fig.to_json())}

def analyze_by_gender():
    gender_stats = df.groupby('Sex')['Survived'].agg(['count', 'sum']).reset_index()
    gender_stats['rate'] = gender_stats['sum'] / gender_stats['count'] * 100
    
    fig = px.bar(
        gender_stats,
        x='Sex',
        y='rate',
        title='Survival Rate by Gender',
        labels={'Sex': 'Gender', 'rate': 'Survival Rate (%)'},
        color_discrete_sequence=['#4f46e5']
    )
    
    text = "\n".join([
        f"{row['Sex']}: {row['rate']:.1f}% survival rate ({int(row['sum'])} out of {int(row['count'])})"
        for _, row in gender_stats.iterrows()
    ])
    
    return {'text': text, 'plot': json.loads(fig.to_json())}

def analyze_by_age():
    df['AgeGroup'] = pd.cut(
        df['Age'],
        bins=[0, 12, 30, 50, 100],
        labels=['Children', 'Young Adults', 'Adults', 'Elderly']
    )
    
    age_stats = df.groupby('AgeGroup')['Survived'].agg(['count', 'sum']).reset_index()
    age_stats['rate'] = age_stats['sum'] / age_stats['count'] * 100
    
    fig = px.bar(
        age_stats,
        x='AgeGroup',
        y='rate',
        title='Survival Rate by Age Group',
        labels={'AgeGroup': 'Age Group', 'rate': 'Survival Rate (%)'},
        color_discrete_sequence=['#4f46e5']
    )
    
    text = "\n".join([
        f"{row['AgeGroup']}: {row['rate']:.1f}% survival rate ({int(row['sum'])} out of {int(row['count'])})"
        for _, row in age_stats.iterrows()
    ])
    
    return {'text': text, 'plot': json.loads(fig.to_json())}

def analyze_gender_percentage():
    male_count = len(df[df['Sex'] == 'male'])
    total_count = len(df)
    male_percentage = (male_count / total_count) * 100
    return {'text': f"{male_percentage:.1f}% of passengers were male on the Titanic."}

def analyze_age_histogram():
    fig = px.histogram(df, x="Age", nbins=30, title="Distribution of Passenger Ages", color_discrete_sequence=['#4f46e5'])
    return {'text': "Here's a histogram of passenger ages.", 'plot': json.loads(fig.to_json())}

def analyze_average_fare():
    avg_fare = df['Fare'].mean()
    return {'text': f"The average ticket fare was ${avg_fare:.2f}."}

def analyze_passengers_by_port():
    port_stats = df['Embarked'].value_counts().reset_index()
    port_stats.columns = ['Port', 'Passenger Count']
    
    fig = px.bar(
        port_stats,
        x='Port',
        y='Passenger Count',
        title='Number of Passengers by Embarkation Port',
        labels={'Port': 'Embarkation Port', 'Passenger Count': 'Count'},
        color_discrete_sequence=['#4f46e5']
    )
    
    return {'text': "Here’s a breakdown of how many passengers embarked from each port.", 'plot': json.loads(fig.to_json())}

@app.post("/analyze")
async def analyze_query(query: Query):
    query_text = query.text.lower()
    
    if 'survival rate' in query_text or 'survived' in query_text:
        return analyze_survival_rate()
    elif 'class' in query_text:
        return analyze_by_class()
    elif 'gender' in query_text or 'men' in query_text or 'women' in query_text:
        return analyze_by_gender()
    elif 'age' in query_text and 'histogram' in query_text:
        return analyze_age_histogram()
    elif 'age' in query_text:
        return analyze_by_age()
    elif 'percentage of passengers were male' in query_text:
        return analyze_gender_percentage()
    elif 'average ticket fare' in query_text:
        return analyze_average_fare()
    elif 'embarked' in query_text or 'port' in query_text:
        return analyze_passengers_by_port()
    else:
        return {
            'text': "I'm not sure how to answer that question. Try asking about survival rates, demographics, or fares!",
            'plot': None
        }
