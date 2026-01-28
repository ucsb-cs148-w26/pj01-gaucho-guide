import pandas as pd


def process_reddit_for_rag(csv_path):
    df = pd.read_csv(csv_path)
    rag_documents = []

    for _, row in df.iterrows():
        # Construct a narrative text chunk
        # We combine title and body for better context
        content = f"Reddit thread from r/{row['subreddit']}. \nTitle: {row['title']}\nDetails: {row['text']}"

        # Add Metadata (Crucial for citations in RAG)
        metadata = {
            "source": "Reddit",
            "url": row['url'],
            "score": row['score']  # usable for filtering low-quality info later
        }

        rag_documents.append({"text": content, "metadata": metadata})

    return rag_documents


def process_rmp_for_rag(csv_path):
    df = pd.read_csv(csv_path)
    rag_documents = []

    for _, row in df.iterrows():
        # Convert stats into a descriptive sentence
        content = (
            f"Professor {row['professor']} teaches in the {row['department']} department. "
            f"They have an overall quality rating of {row['rating']}/5.0 "
            f"and a difficulty rating of {row['difficulty']}/5.0. "
            f"This data is based on {row['num_ratings']} student ratings."
        )

        metadata = {
            "source": "RateMyProfessor",
            "url": row['link'],
            "entity": row['professor']
        }

        rag_documents.append({"text": content, "metadata": metadata})

    return rag_documents


# --- usage ---
#reddit_docs = process_reddit_for_rag("ucsb_reddit_data.csv")
rmp_docs = process_rmp_for_rag("ucsb_rmp_data.csv")


print(rmp_docs[0]['text'])
