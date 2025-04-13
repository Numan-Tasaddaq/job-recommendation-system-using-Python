Job Recommendation System with Text Processing and AI Integration

In this project, I developed a Flask-based job recommendation system that processes and analyzes job descriptions from a CSV file using text processing techniques such as TF-IDF and CountVectorizer. The system leverages cosine similarity to match user queries with relevant job descriptions, offering personalized job recommendations.

Key features:

Text Preprocessing: Combines multiple fields from job descriptions into a unified text representation for better search relevance.

Cosine Similarity: Uses cosine similarity to measure the relevance between user queries and job descriptions.

AI Integration: Integrates Google’s Gemini API (formerly known as PaLM) to generate detailed, human-like responses based on the query and job data.

Flask Framework: Implements a web interface using Flask to handle user queries and present matching job information in an intuitive format.

The system also includes a mechanism to handle and display job-specific details such as salary, job type, and location, ensuring users get comprehensive information.

Languages and Libraries Used:

Languages: Python

Libraries: Flask, Pandas, Scikit-learn (TF-IDF, CountVectorizer, Cosine Similarity), Google Generative AI API (Gemini), NumPy