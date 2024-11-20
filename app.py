from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv
import streamlit


# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key
openai.api_key = api_key

# Initialize Flask app
app = Flask(__name__)

# In-memory database for courses
courses = {}

# Function to get response from OpenAI
def get_openai_response(question):
    try:
        # Call OpenAI API
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert course creator"},
                {"role": "user", "content": question},
            ],
            max_tokens=200,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}

# API route to generate and add course content (POST)
@app.route('/courses', methods=['POST'])
def add_course():
    data = request.get_json()
    course_id = data.get('id')
    course_description = data.get('course_description')
    number_of_words = data.get('number_of_words')
    learner_type = data.get('learner_type')

    # Validate input
    try:
        number_of_words = int(number_of_words)  # Convert to integer
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input. 'number_of_words' must be an integer."}), 400

    if not course_id or not course_description or not learner_type:
        return jsonify({"error": "Invalid input. Provide ID, description, and learner type."}), 400

    if course_id in courses:
        return jsonify({"error": "Course ID already exists."}), 409

    # Generate course content using OpenAI
    question = f"{course_description} in {number_of_words} words write the course for {learner_type}."
    response = get_openai_response(question)

    if isinstance(response, dict) and "error" in response:
        return jsonify({"error": response["error"]}), 500

    courses[course_id] = response
    return jsonify({"message": "Course added successfully.", "course_id": course_id, "content": response}), 201

# API route to retrieve course(s) (GET)
@app.route('/courses', methods=['GET'])
def get_courses():
    course_id = request.args.get('id')
    if course_id:
        course = courses.get(course_id)
        if course:
            return jsonify({"course_id": course_id, "content": course}), 200
        return jsonify({"error": "Course not found."}), 404
    return jsonify({"courses": courses}), 200

# API route to update an existing course (PUT)
@app.route('/courses/<course_id>', methods=['PUT'])
def update_course(course_id):
    if course_id not in courses:
        return jsonify({"error": "Course not found."}), 404

    data = request.get_json()
    course_description = data.get('course_description')
    number_of_words = data.get('number_of_words')
    learner_type = data.get('learner_type')

    # Validate input
    if not course_description or not isinstance(number_of_words, int) or not learner_type:
        return jsonify({"error": "Invalid input. Provide description, word count, and learner type."}), 400

    # Generate updated course content using OpenAI
    question = f"{course_description} in {number_of_words} words write the course for {learner_type}."
    response = get_openai_response(question)

    if isinstance(response, dict) and "error" in response:
        return jsonify({"error": response["error"]}), 500

    courses[course_id] = response
    return jsonify({"message": "Course updated successfully.", "course_id": course_id, "content": response}), 200

# API route to delete a course (DELETE)
@app.route('/courses/<course_id>', methods=['DELETE'])
def delete_course(course_id):
    if course_id not in courses:
        return jsonify({"error": "Course not found."}), 404

    del courses[course_id]
    return jsonify({"message": "Course deleted successfully.", "course_id": course_id}), 200

# Start the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

