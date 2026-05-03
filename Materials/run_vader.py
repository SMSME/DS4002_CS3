import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# load data from scraped reviews
df = pd.read_csv("../DATA/uva_reviews_final.csv")

# initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# define scoring function
def get_sentiment(text):
    # return compound score between -1 and 1
    scores = analyzer.polarity_scores(str(text))
    return scores['compound']

# use the scoring function to create a new column 'sentiment_score'
print("Running VADER analysis on reviews...")
df['sentiment_score'] = df['text'].apply(get_sentiment)

# assign labels to sentiment scores for future visualization
def get_label(score):
    if score >= 0.05:
        return 'Positive'
    elif score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

# apply the labeling function to the sentiment scores
df['sentiment_label'] = df['sentiment_score'].apply(get_label)

# save results to csv
output_filename = "../DATA/uva_reviews_with_sentiment.csv"
df.to_csv(output_filename, index=False)

print(f"\nSaved to {output_filename}")
print("\nAverage Sentiment by Group")
print(df.groupby('group')['sentiment_score'].mean())

print("\nSentiment Counts by Group")
print(df.groupby(['group', 'sentiment_label']).size())