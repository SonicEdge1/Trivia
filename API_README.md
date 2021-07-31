# Project README - Udacity Trivia API

## API Reference

### Getting Started 
- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration. 
- Authentication: This version of the application does not require authentication or API keys. 

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return four error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found 
- 405: Method Not Allowed
- 422: Not Processable 

### Endpoints 
#### GET /categories 
- General: 
    - Returns a dictionary of categories, success value, and total number of categories 
 
- Sample: `curl http://127.0.0.1:5000/categories`

``` 
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "success": true, 
  "total_categories": 6
}
```

#### GET /questions 
- General: 
    - Returns a list of trivia questions, question categories, the current_category, success value, and total number of questions 
    - Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1.
 
- Sample: `curl http://127.0.0.1:5000/categories?page=1`

``` 
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "current_category": "Science", 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
    {
      "answer": "Tom Cruise", 
      "category": 5, 
      "difficulty": 4, 
      "id": 4, 
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    }
  ], 
  "success": true, 
  "total_questions": 2
}
```

#### DELETE /questions/{question_id}
- General:
    - Deletes the trivia question of the given ID if it exists. Returns the ID of the deleted question, the question's text, and success value.
- `curl -X DELETE http://127.0.0.1:5000/questions/6`
```
{
  "deleted_question_text": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?", 
  "deleted_question_id": 6, 
  "success": true
}
```

#### POST /questions
- General:
    - Creates a new trivia question using a submitted question object in the request body containing a string question, answer, and category, and an integer difficulty.  Returns the new question ID, question text, total questions, and success value.  
    - Sample Request Body:
    ```
        {
            'question': 'Trivia Question Text',
            'answer': 'Answer Text',
            'difficulty': 4,
            'category': '5'
        }
    ```        
- `curl -X POST -H "Content-Type: application/json" -d '{"question":"How many different actors have portrayed the character James Bond in the 26 films released between 1962-2015?", "answer":"Seven", "difficulty":"4", "category":"5"}' http://127.0.0.1:5000/questions`
```
{
  "new_question_id": 44, 
  "question": "How many different actors have portrayed the character James Bond in the 26 films released between 1962-2015?", 
  "success": true, 
  "total_questions": 36
}
```

#### POST /questions
- General:
    - Performs a search for trivia questions based on a given search term.  Returns the success value, any questions having text that matches the search term, the current category, and total number of questions found.
    - In the case where a search finds no questions, the success value will be OK and the total number of questions found will be 0.  
    - Sample Request Body:
    ```
        {
            'searchTerm': 'This isn't the term you're looking for' 
        }
    ```        
- `curl -X POST -H "Content-Type: application/json" -d '{"searchTerm":"soccer"}' http://127.0.0.1:5000/questions`
```
{
  "current_category": "Sports", 
  "questions": [
    {
      "answer": "Brazil", 
      "category": 6, 
      "difficulty": 3, 
      "id": 10, 
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    }, 
    {
      "answer": "Uruguay", 
      "category": 6, 
      "difficulty": 4, 
      "id": 11, 
      "question": "Which country won the first ever soccer World Cup in 1930?"
    }
  ], 
  "success": true, 
  "total_questions": 2
}
```

#### GET /categories/{category_id}/questions
- General:
    - Returns a list of trivia questions that match the category ID given in the url.  Will also return the success value, total questions in the given category and the current game category.
- `curl http://127.0.0.1:5000/categories/5/questions`
```
{
  "current_category": "Entertainment", 
  "questions": [
    {
      "answer": "Back to the Future", 
      "category": 5, 
      "difficulty": 3, 
      "id": 24, 
      "question": "What movie trilogy centers around history altering events occurring on November 12, 1955?"
    }, 
    {
      "answer": "blowin in the wind", 
      "category": 5, 
      "difficulty": 2, 
      "id": 26, 
      "question": "Where can you find the answer to how many roads a man must walk down before they call him a man?"
    }
  ], 
  "success": true, 
  "total_questions": 2
}

```
 @app.route('/quizzes', methods=['POST'])
#### POST /quizzes
- General:
    - Returns the next question to be played in the quiz, the current game category, the success value, and total number of questions returned.
    - Questions are selected based on a given category in the request body.  A category with an id of 0 will return a questions of any category.
    - Note that to play a game in one category, that a minimum of 6 questions are required to be available in that category. If there are less than 6 available, this will return a success of OK, but the number of questions will show 0.
    - Sample Request Body:
    ```
    {
        "quiz_category": {"type": "Science", "id": "1"},
        "previous_questions": [20, 21, 22, 27, 28]
    }
    ```
- `curl -X POST -H "Content-Type: application/json" -d '{"previous_questions":[20, 21, 22, 27, 28], "quiz_category":{"type": "Science", "id": "1"}}' http://127.0.0.1:5000/quizzes`
```
{
{
  "question": {
    "answer": "Paleontology", 
    "category": 1, 
    "difficulty": 2, 
    "id": 29, 
    "question": "What branch of science studies ancient life on Earth?"
  }, 
  "quiz_category": {
    "id": "1", 
    "type": "Science"
  }, 
  "success": true, 
  "total_questions": 1
}
```