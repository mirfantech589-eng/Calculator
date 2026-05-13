# =========================================================
# AI CALCULATOR - ALL IN ONE FILE
# Technologies:
# - Flask Backend
# - HTML/CSS/JS Frontend
# - SymPy Math Engine
# - OpenAI AI Integration (Optional)
#
# INSTALL:
# pip install flask sympy openai
#
# RUN:
# python app.py
#
# OPEN:
# http://127.0.0.1:5000
# =========================================================

from flask import Flask, request, jsonify, render_template_string
from sympy import sympify
from sympy import symbols, solve
import math
import re

# OPTIONAL AI
# Uncomment if using OpenAI
# from openai import OpenAI

app = Flask(__name__)

# =========================================================
# OPTIONAL OPENAI SETUP
# =========================================================

# client = OpenAI(
#     api_key="YOUR_OPENAI_API_KEY"
# )

# =========================================================
# HTML FRONTEND
# =========================================================

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Calculator</title>

    <style>

        body{
            background:#111;
            font-family:Arial;
            color:white;
            display:flex;
            justify-content:center;
            align-items:center;
            height:100vh;
            margin:0;
        }

        .container{
            width:420px;
            background:#1e1e1e;
            padding:20px;
            border-radius:15px;
            box-shadow:0px 0px 20px rgba(0,0,0,0.5);
        }

        h1{
            text-align:center;
            margin-bottom:20px;
        }

        #display{
            width:100%;
            height:60px;
            font-size:28px;
            margin-bottom:15px;
            border:none;
            border-radius:10px;
            padding-left:10px;
            background:#333;
            color:white;
        }

        .buttons{
            display:grid;
            grid-template-columns:repeat(4,1fr);
            gap:10px;
        }

        button{
            height:60px;
            font-size:22px;
            border:none;
            border-radius:10px;
            cursor:pointer;
            background:#444;
            color:white;
        }

        button:hover{
            background:#666;
        }

        .equal{
            background:#ff9800;
        }

        .clear{
            background:red;
        }

        .ai-box{
            margin-top:20px;
        }

        textarea{
            width:100%;
            height:80px;
            border-radius:10px;
            border:none;
            padding:10px;
            font-size:16px;
            background:#333;
            color:white;
        }

        .ai-btn{
            width:100%;
            margin-top:10px;
            background:#2196f3;
        }

        #result{
            margin-top:15px;
            font-size:20px;
            color:#00ff99;
            min-height:30px;
        }

    </style>
</head>

<body>

<div class="container">

    <h1>AI Calculator</h1>

    <input type="text" id="display" readonly>

    <div class="buttons">

        <button onclick="append('7')">7</button>
        <button onclick="append('8')">8</button>
        <button onclick="append('9')">9</button>
        <button onclick="append('/')">/</button>

        <button onclick="append('4')">4</button>
        <button onclick="append('5')">5</button>
        <button onclick="append('6')">6</button>
        <button onclick="append('*')">*</button>

        <button onclick="append('1')">1</button>
        <button onclick="append('2')">2</button>
        <button onclick="append('3')">3</button>
        <button onclick="append('-')">-</button>

        <button onclick="append('0')">0</button>
        <button onclick="append('.')">.</button>
        <button class="equal" onclick="calculate()">=</button>
        <button onclick="append('+')">+</button>

        <button onclick="append('(')">(</button>
        <button onclick="append(')')">)</button>
        <button onclick="append('**')">^</button>
        <button onclick="append('sqrt(')">√</button>

        <button class="clear" onclick="clearDisplay()">C</button>

    </div>

    <div id="result"></div>

    <div class="ai-box">

        <h3>AI Math Assistant</h3>

        <textarea id="aiInput"
        placeholder="Example:
What is 25% of 400?
Solve x^2 - 5x + 6"></textarea>

        <button class="ai-btn" onclick="askAI()">
            Ask AI
        </button>

    </div>

</div>

<script>

    function append(value){
        document.getElementById('display').value += value;
    }

    function clearDisplay(){
        document.getElementById('display').value = '';
        document.getElementById('result').innerHTML = '';
    }

    async function calculate(){

        let expression =
        document.getElementById('display').value;

        let response = await fetch('/calculate',{
            method:'POST',
            headers:{
                'Content-Type':'application/json'
            },
            body:JSON.stringify({
                expression:expression
            })
        });

        let data = await response.json();

        document.getElementById('result').innerHTML =
        "Result: " + data.result;
    }

    async function askAI(){

        let question =
        document.getElementById('aiInput').value;

        let response = await fetch('/ai',{
            method:'POST',
            headers:{
                'Content-Type':'application/json'
            },
            body:JSON.stringify({
                question:question
            })
        });

        let data = await response.json();

        document.getElementById('result').innerHTML =
        data.answer;
    }

</script>

</body>
</html>
"""

# =========================================================
# SECURITY VALIDATION
# =========================================================

def is_safe_expression(expression):

    allowed_chars = "0123456789+-*/().% sqrt"

    for char in expression:
        if char not in allowed_chars:
            return False

    return True

# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

# =========================================================
# BASIC CALCULATOR API
# =========================================================

@app.route("/calculate", methods=["POST"])
def calculate():

    data = request.json
    expression = data.get("expression", "")

    expression = expression.replace("^", "**")

    if not is_safe_expression(expression):
        return jsonify({
            "result": "Invalid characters detected"
        })

    try:

        result = sympify(expression)

        return jsonify({
            "result": str(result)
        })

    except Exception as e:

        return jsonify({
            "result": f"Error: {str(e)}"
        })

# =========================================================
# AI ENGINE
# =========================================================

@app.route("/ai", methods=["POST"])
def ai():

    data = request.json
    question = data.get("question", "").lower()

    try:

        # =================================================
        # PERCENTAGE
        # =================================================

        if "%" in question:

            nums = re.findall(r'\d+', question)

            if len(nums) >= 2:

                percent = float(nums[0])
                number = float(nums[1])

                result = (percent / 100) * number

                return jsonify({
                    "answer": f"{percent}% of {number} = {result}"
                })

        # =================================================
        # QUADRATIC EQUATION
        # =================================================

        if "solve" in question:

            question = question.replace("solve", "")
            question = question.replace("^", "**")

            x = symbols('x')

            expr = sympify(question)

            result = solve(expr, x)

            return jsonify({
                "answer": f"Solution: {result}"
            })

        # =================================================
        # BASIC NATURAL LANGUAGE
        # =================================================

        if "add" in question:

            nums = re.findall(r'\d+', question)

            total = sum(map(float, nums))

            return jsonify({
                "answer": f"Answer: {total}"
            })

        # =================================================
        # SQUARE ROOT
        # =================================================

        if "square root" in question:

            nums = re.findall(r'\d+', question)

            if nums:

                number = float(nums[0])

                result = math.sqrt(number)

                return jsonify({
                    "answer":
                    f"Square root of {number} = {result}"
                })

        # =================================================
        # OPTIONAL OPENAI AI
        # =================================================

        """
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role":"user",
                    "content":question
                }
            ]
        )

        ai_answer = response.choices[0].message.content

        return jsonify({
            "answer": ai_answer
        })
        """

        # =================================================
        # FALLBACK
        # =================================================

        return jsonify({
            "answer":
            "AI could not understand the question."
        })

    except Exception as e:

        return jsonify({
            "answer": f"Error: {str(e)}"
        })

# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print("\\n===================================")
    print(" AI CALCULATOR RUNNING ")
    print("===================================")
    print(" Open browser:")
    print(" http://127.0.0.1:5000")
    print("===================================\\n")

    app.run(debug=True)