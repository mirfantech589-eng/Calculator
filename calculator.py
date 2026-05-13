from flask import Flask, request, jsonify, render_template_string

from sympy import sympify, symbols, solve

import math

import re

import os
 
app = Flask(__name__)
 
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

            min-height:100vh;

            margin:0;

            padding:20px;

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

            box-sizing:border-box;

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

            height:100px;

            border-radius:10px;

            border:none;

            padding:10px;

            font-size:16px;

            background:#333;

            color:white;

            box-sizing:border-box;

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

            word-wrap:break-word;

        }
</style>
</head>
 
<body>
 
<div class="container">
<h1>AI Calculator</h1>
 
    <input type="text" id="display" readonly>
 
    <div class="buttons">
<button onclick="appendValue('7')">7</button>
<button onclick="appendValue('8')">8</button>
<button onclick="appendValue('9')">9</button>
<button onclick="appendValue('/')">/</button>
 
        <button onclick="appendValue('4')">4</button>
<button onclick="appendValue('5')">5</button>
<button onclick="appendValue('6')">6</button>
<button onclick="appendValue('*')">*</button>
 
        <button onclick="appendValue('1')">1</button>
<button onclick="appendValue('2')">2</button>
<button onclick="appendValue('3')">3</button>
<button onclick="appendValue('-')">-</button>
 
        <button onclick="appendValue('0')">0</button>
<button onclick="appendValue('.')">.</button>
<button class="equal" onclick="calculate()">=</button>
<button onclick="appendValue('+')">+</button>
 
        <button onclick="appendValue('(')">(</button>
<button onclick="appendValue(')')">)</button>
<button onclick="appendValue('**')">^</button>
<button onclick="appendValue('sqrt(')">√</button>
 
        <button class="clear" onclick="clearDisplay()">C</button>
</div>
 
    <div id="result"></div>
 
    <div class="ai-box">
<h3>AI Math Assistant</h3>
 
        <textarea id="aiInput" placeholder="Examples:

5 + 5

25% of 400

square root 144

solve x^2 - 5*x + 6"></textarea>
 
        <button class="ai-btn" onclick="askAI()">Ask AI</button>
</div>
</div>
 
<script>

    function appendValue(value){

        document.getElementById('display').value += value;

    }
 
    function clearDisplay(){

        document.getElementById('display').value = '';

        document.getElementById('result').innerHTML = '';

    }
 
    async function calculate(){

        let expression = document.getElementById('display').value;
 
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

        document.getElementById('result').innerHTML = "Result: " + data.result;

    }
 
    async function askAI(){

        let question = document.getElementById('aiInput').value;
 
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

        document.getElementById('result').innerHTML = data.answer;

    }
</script>
 
</body>
</html>

"""
 
# =========================================================

# SECURITY VALIDATION

# =========================================================
 
def is_safe_expression(expression):

    pattern = r'^[0-9+\-*/().%\s^sqrt]+$'

    return bool(re.match(pattern, expression))
 
 
# =========================================================

# HOME PAGE

# =========================================================
 
@app.route("/")

def home():

    return render_template_string(HTML_PAGE)
 
 
# =========================================================

# BASIC CALCULATOR

# =========================================================
 
@app.route("/calculate", methods=["POST"])

def calculate_route():

    data = request.json

    expression = data.get("expression", "")
 
    expression = expression.replace("^", "**")
 
    if not is_safe_expression(expression):

        return jsonify({"result": "Invalid characters detected"})
 
    try:

        result = sympify(expression)

        return jsonify({"result": str(result)})
 
    except Exception as e:

        return jsonify({"result": f"Error: {str(e)}"})
 
 
# =========================================================

# AI ENGINE

# =========================================================
 
@app.route("/ai", methods=["POST"])

def ai():

    data = request.json

    question = data.get("question", "").lower()
 
    try:

        # Addition

        if "add" in question or "+" in question:

            nums = re.findall(r'-?\d+\.?\d*', question)

            total = sum(map(float, nums))

            return jsonify({"answer": f"Answer: {total}"})
 
        # Subtraction

        if "subtract" in question or "-" in question:

            nums = re.findall(r'-?\d+\.?\d*', question)

            if len(nums) >= 2:

                result = float(nums[0]) - float(nums[1])

                return jsonify({"answer": f"Answer: {result}"})
 
        # Multiplication

        if "multiply" in question or "*" in question:

            nums = re.findall(r'-?\d+\.?\d*', question)

            if len(nums) >= 2:

                result = float(nums[0]) * float(nums[1])

                return jsonify({"answer": f"Answer: {result}"})
 
        # Division

        if "divide" in question or "/" in question:

            nums = re.findall(r'-?\d+\.?\d*', question)

            if len(nums) >= 2:

                result = float(nums[0]) / float(nums[1])

                return jsonify({"answer": f"Answer: {result}"})
 
        # Percentage

        if "%" in question or "percent" in question:

            nums = re.findall(r'-?\d+\.?\d*', question)

            if len(nums) >= 2:

                percent = float(nums[0])

                number = float(nums[1])

                result = (percent / 100) * number

                return jsonify({"answer": f"{percent}% of {number} = {result}"})
 
        # Square root

        if "square root" in question or "sqrt" in question:

            nums = re.findall(r'-?\d+\.?\d*', question)

            if nums:

                number = float(nums[0])

                result = math.sqrt(number)

                return jsonify({"answer": f"Square root of {number} = {result}"})
 
        # Power

        if "power" in question or "^" in question:

            nums = re.findall(r'-?\d+\.?\d*', question)

            if len(nums) >= 2:

                result = float(nums[0]) ** float(nums[1])

                return jsonify({"answer": f"Answer: {result}"})
 
        # Solve equation

        if "solve" in question:

            question = question.replace("solve", "").strip()

            question = question.replace("^", "**")
 
            x = symbols('x')

            expr = sympify(question, evaluate=False)

            result = solve(expr, x)
 
            return jsonify({"answer": f"Solution: {result}"})
 
        # Direct expression

        try:

            expression = question.replace("^", "**")

            result = sympify(expression)

            return jsonify({"answer": f"Result: {result}"})

        except:

            pass
 
        return jsonify({

            "answer": "Try examples like:<br>"

                      "5 + 5<br>"

                      "25% of 400<br>"

                      "square root 144<br>"

                      "solve x^2 - 5*x + 6"

        })
 
    except Exception as e:

        return jsonify({"answer": f"Error: {str(e)}"})
 
 
# =========================================================

# START SERVER

# =========================================================
 
if __name__ == "__main__":

    print("\n===================================")

    print("AI CALCULATOR RUNNING")

    print("Open browser: http://127.0.0.1:5000")

    print("===================================\n")
 
    app.run(

        host="127.0.0.1",

        port=5000,

        debug=False

    )
 
