from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai  # Configure the Gemini API
from sklearn.feature_extraction.text import CountVectorizer

# Configure the Gemini API
api_key = "Add you API Key"
genai.configure(api_key=api_key)

app = Flask(__name__)

# Load and preprocess data
df = pd.read_csv("jobs.csv")
vectorizer = CountVectorizer(stop_words='english')

# Preprocess job descriptions
df['job_description'] = (
    df['Business Title'].fillna('') + ' ' +
    df['Civil Service Title'].fillna('') + ' ' +
    df['Job Description'].fillna('') + ' ' +
    df['Minimum Qual Requirements'].fillna('') + ' ' +
    df['Preferred Skills'].fillna('') + ' ' +
    df['Additional Information'].fillna('')
)

# Fit the vectorizer
tfidf_matrix = vectorizer.fit_transform(df['job_description'].tolist())

# To track previously matched jobs
previous_jobs = pd.DataFrame()

def extract_job_title(query, df):
    job_titles = df['Business Title'].str.lower().tolist()
    query = query.lower()
    for title in job_titles:
        if title in query:
            return title
    return None

def retrieve_relevant_document(query, df, vectorizer, tfidf_matrix):
    extracted_title = extract_job_title(query, df)
    matching_jobs = pd.DataFrame()

    if extracted_title:
        # Find all jobs that match the extracted title
        matching_jobs = df[df['Business Title'].str.contains(extracted_title, case=False, na=False)]

    if matching_jobs.empty:
        # If no matching job title is found, fall back to cosine similarity
        query_vector = vectorizer.transform([query])
        cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        most_similar_idx = cosine_similarities.argsort()[::-1]  # Sort in descending order

        for idx in most_similar_idx:
            if cosine_similarities[idx] > 0.2:  # If the similarity is above a threshold
                matching_jobs = pd.concat([matching_jobs, df.iloc[[idx]]])


    if matching_jobs.empty:
        return pd.DataFrame()  # Return an empty DataFrame if no matches found

    return matching_jobs

def handle_salary(salary):
    # Handle cases where salary might be missing, NaN, or invalid
    try:
        # Convert to float if it's a valid number
        salary = float(salary)
        return salary
    except (ValueError, TypeError):
        return "Salary information not available"  # Return a default message if the salary is invalid

def generate_response_with_retrieval(query, matched_jobs):
    if matched_jobs.empty:
        return "No job found in the given document."

    response_text = ""
    for _, matched_row in matched_jobs.iterrows():
        job_id = matched_row['Job ID']
        job_title = matched_row['Business Title']
        job_description = matched_row['job_description']
        salary_from = handle_salary(matched_row['Salary Range From'])
        salary_to = handle_salary(matched_row['Salary Range To'])
        full_time_part_time = matched_row['Full-Time/Part-Time indicator']
        work_location = matched_row['Work Location']

        # Format details for each job
        salary_info = f"Salary Range: {salary_from} to {salary_to}" if isinstance(salary_from, str) else f"Salary Range: {salary_from} to {salary_to}"
        work_status = f"Job Type: {full_time_part_time}" if full_time_part_time else "Job Type: Not specified"
        location_info = f"Work Location: {work_location}" if work_location else "Work Location: Not specified"
        
        response_text += f"\n\nJob Information (ID: {job_id}, Title: {job_title}):\n\n{job_description}\n\n{salary_info}\n{work_status}\n{location_info}"

    prompt = f"Answer the following question: \n\n{query}\n\n{response_text}"

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    global previous_jobs
    user_query = request.json.get("query")

    # Check for "this job" or "these jobs" in the user query
    if "this job" in user_query.lower() or "these jobs" in user_query.lower():
        if previous_jobs.empty:
            return jsonify({"response": "No previous job data available for reference."})
        else:
            response = generate_response_with_retrieval(user_query, previous_jobs)
            return jsonify({"response": response})

    # Otherwise, process the query as usual
    matched_jobs = retrieve_relevant_document(user_query, df, vectorizer, tfidf_matrix)

    if matched_jobs.empty:
        return jsonify({"response": "No job found in the given document matching the query."})

    # Update the previous jobs data
    previous_jobs = matched_jobs

    response = generate_response_with_retrieval(user_query, matched_jobs)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
