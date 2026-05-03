# this script for creates the exploratory plots

# all imports 
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# all path related information in order to access appropriate directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if os.path.basename(SCRIPT_DIR) == "SCRIPTS":
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
else:
    PROJECT_ROOT = SCRIPT_DIR

DATA_DIR = os.path.join(PROJECT_ROOT, "DATA")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "OUTPUT")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# this is the path to the CSV with the sentiment analysis already done 
csv_path = os.path.join(DATA_DIR, "uva_reviews_with_sentiment.csv")

# here we are going to read the data in the csv file
df = pd.read_csv(csv_path)


# these are for customizing the output graphs as UVA themed
UVA_BLUE = "#232D4B"
UVA_ORANGE = "#E57200"

# this is to set the theme of the graphs
sns.set_theme(
    style="whitegrid",
    font="DejaVu Sans",
    rc={
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11
    }
)

# in order to diferentiate between the two disciplines we are using two different UVA colors
palette = {
    "STEM": UVA_BLUE,
    "Humanities": UVA_ORANGE
}

# for each of the plots, i want to save them to the output directory
def save_and_show(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    # plt.show()
    plt.close()


# this section of code is for plot 1 which simply
# displays the amount of reviews per discipline at UVA
plt.figure(figsize=(6,4))
sns.countplot(data=df, x="group", palette=palette)
plt.title("Student Review Volume by Discipline at UVA")
plt.xlabel("Discipline")
plt.ylabel("Number of Reviews")
save_and_show("reviews_by_group.png")


# this is for plot 2 which is histogram which displays
# the distribution of review sentiment scores across disciplines
plt.figure(figsize=(8,5))
sns.histplot(
    data=df,
    x="sentiment_score",
    hue="group",
    bins=30,
    kde=True,
    palette=palette,
    alpha=0.7
)
plt.title("Distribution of Review Sentiment Scores")
plt.xlabel("VADER Sentiment Score (−1 = Negative, +1 = Positive)")
plt.ylabel("Number of Reviews")
save_and_show("sentiment_distribution.png")


# this section is for plot 3 which is a boxplot comparison of the two disciplines
plt.figure(figsize=(6,4))
sns.boxplot(
    data=df,
    x="group",
    y="sentiment_score",
    palette=palette
)
plt.axhline(0, linestyle="--", color="gray", linewidth=1)
plt.title("Comparison of Review Sentiment by Discipline")
plt.xlabel("Discipline")
plt.ylabel("Sentiment Score")
save_and_show("sentiment_boxplot.png")


# this is the section of code contributing to plot 4 
# which just shows the counts of positive, neutral, 
# and negative reviews across disciplines
plt.figure(figsize=(8,5))
sns.countplot(
    data=df,
    x="group",
    hue="sentiment_label",
    palette=[UVA_BLUE, "gray", UVA_ORANGE]
)
plt.title("Distribution of Sentiment Labels Across Disciplines")
plt.xlabel("Discipline")
plt.ylabel("Number of Reviews")
save_and_show("sentiment_labels.png")



# this is the section of code contributing to plot 5
# which simply shows the volumes of review for each 
# department (such as PHIL, APMA, etc)
plt.figure(figsize=(10,5))
sns.countplot(
    data=df,
    x="department",
    order=df["department"].value_counts().index,
    color=UVA_BLUE
)
plt.title("Review Volume by Department at UVA")
plt.xlabel("Department")
plt.ylabel("Number of Reviews")
save_and_show("reviews_by_department.png")


# this is the section of code contributing to plot 6
# which displays the average sentiment score per department

dept_sentiment = (
    df.groupby("department")["sentiment_score"]
      .mean()
      .reset_index()
)

plt.figure(figsize=(10,5))
sns.barplot(
    data=dept_sentiment,
    x="department",
    y="sentiment_score",
    color=UVA_ORANGE
)
plt.axhline(0, linestyle="--", color="gray", linewidth=1)
plt.title("Average Review Sentiment by Department")
plt.xlabel("Department")
plt.ylabel("Average Sentiment Score")
save_and_show("avg_sentiment_by_department.png")

# Plot 7: Distribution of Student Ratings (1.0 - 5.0)
plt.figure(figsize=(8,5))
sns.countplot(
    data=df,
    x="rating",
    color=UVA_BLUE
)
plt.title("Distribution of Student Ratings")
plt.xlabel("Rating (1.0 - 5.0)")
plt.ylabel("Number of Reviews")
save_and_show("rating_distribution.png")


# Plot 8: Distribution of Reviews Over Time (Date)
# clean the date column by removing "Updated " and converting to datetime
df['clean_date'] = pd.to_datetime(df['date'].str.replace("Updated ", "", regex=False), errors='coerce')
df['year'] = df['clean_date'].dt.year

plt.figure(figsize=(8,5))
sns.histplot(
    data=df,
    x="year",
    discrete=True,
    color=UVA_ORANGE,
    shrink=0.8
)
plt.title("Volume of Reviews Posted by Year")
plt.xlabel("Year")
plt.ylabel("Number of Reviews")
# rotate x-axis labels if there are many years to improve readability
plt.xticks(rotation=45)
save_and_show("reviews_over_time.png")


# Plot 9: Distribution of Review Lengths (Text)
# we will create a new column for the character count of each review to visualize the distribution of review lengths
df['char_count'] = df['text'].astype(str).apply(len)

plt.figure(figsize=(8,5))
sns.histplot(
    data=df,
    x="char_count",
    bins=40,
    color=UVA_BLUE,
    kde=True
)
plt.title("Distribution of Review Character Counts")
plt.xlabel("Character Count")
plt.ylabel("Frequency")
save_and_show("review_length_distribution.png")


# Plot 10: Top 10 Most Reviewed Courses
top_courses = df["course"].value_counts().head(10).reset_index()
top_courses.columns = ["course", "count"]

plt.figure(figsize=(10,5))
sns.barplot(
    data=top_courses,
    x="count",
    y="course",
    color=UVA_ORANGE
)
plt.title("Top 10 Most Reviewed Courses")
plt.xlabel("Number of Reviews")
plt.ylabel("Course")
save_and_show("top_courses.png")
