from flask import Flask, request, render_template, redirect, session, url_for
import mysql.connector


app = Flask(__name__)
app.secret_key = "fitzone_secret_key"


# ===============================
# DATABASE CONNECTION
# ===============================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="gym_db"
)

cursor = db.cursor()

# ===============================
# ROUTES
# ===============================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/plans")
def plans():
    return render_template("plans.html")


@app.route("/programs")
def programs():
    return render_template("programs.html")


@app.route("/gallery")
def gallery():
    return render_template("gallery.html")


# ===============================
# CONTACT
# ===============================

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]

        sql = "INSERT INTO contact (name, email, phone, message) VALUES (%s, %s, %s, %s)"
        values = (name, email, phone, message)
        cursor.execute(sql, values)
        db.commit()

        return "Message Sent Successfully!"

    return render_template("contact.html")


# ===============================
# REGISTER
# ===============================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form['fullname']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        dob = request.form['dob']
        gender = request.form['gender']
        height = request.form['height']
        weight = request.form['weight']
        goal = request.form['goal']
        plan = request.form['plan']
        medical_info = request.form['medical_info']
        emergency_name = request.form['emergency_name']
        emergency_number = request.form['emergency_number']

        sql = """
        INSERT INTO members 
        (fullname, email, mobile, password, dob, gender, height, weight, goal, plan, medical_info, emergency_name, emergency_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (fullname, email, mobile, password, dob, gender,
                  height, weight, goal, plan,
                  medical_info, emergency_name, emergency_number)

        cursor.execute(sql, values)
        db.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/register/<program_name>")
def register_program(program_name):
    return render_template("register.html", program=program_name)


# ===============================
# LOGIN
# ===============================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        sql = "SELECT * FROM members WHERE email=%s AND password=%s"
        values = (email, password)

        cursor.execute(sql, values)
        user = cursor.fetchone()

        if user:
            session["user"] = user[1]   # fullname
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Email or Password"

    return render_template("login.html")


# ===============================
# DASHBOARD (Protected Page)
# ===============================

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=session["user"])


# ===============================
# BMI CALCULATOR
# ===============================

@app.route("/bmi", methods=["GET", "POST"])
def bmi():
    if "user" not in session:
        return redirect(url_for("login"))

    result = None

    if request.method == "POST":
        try:
            height = float(request.form["height"])
            weight = float(request.form["weight"])

            # Convert cm to meters
            height = height / 100  

            bmi_value = weight / (height * height)
            result = round(bmi_value, 2)

        except:
            result = "Invalid Input"

    return render_template("bmi.html", result=result)


# ===============================
# SMART CALORIE CALCULATOR
# ===============================


@app.route("/calorie", methods=["GET", "POST"])
def calorie():
    if "user" not in session:
        return redirect(url_for("login"))

    result = None

    if request.method == "POST":
        weight = float(request.form["weight"])
        height = float(request.form["height"])
        age = int(request.form["age"])
        gender = request.form["gender"]
        activity = float(request.form["activity"])
        goal = request.form["goal"]

        # BMR Calculation
        if gender == "Male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        # TDEE
        calories = bmr * activity

        # Goal Adjustment
        if goal == "Weight Loss":
            calories -= 500
        elif goal == "Muscle Gain":
            calories += 400

        result = round(calories)

    return render_template("calorie.html", result=result)


# ===============================
# DIET PLANNER
# ===============================

@app.route("/diet", methods=["GET", "POST"])
def diet():
    if "user" not in session:
        return redirect(url_for("login"))

    plan = None

    if request.method == "POST":
        calories = int(request.form["calories"])
        goal = request.form["goal"]

        if goal == "Weight Loss":
            protein_percent = 0.40
            carb_percent = 0.35
            fat_percent = 0.25
        elif goal == "Muscle Gain":
            protein_percent = 0.35
            carb_percent = 0.45
            fat_percent = 0.20
        else:
            protein_percent = 0.30
            carb_percent = 0.40
            fat_percent = 0.30

        protein = round((calories * protein_percent) / 4)
        carbs = round((calories * carb_percent) / 4)
        fats = round((calories * fat_percent) / 9)

        plan = {
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fats": fats,
            "goal": goal
        }

    return render_template("diet.html", plan=plan)


# ===============================
# AI WORKOUT GENERATOR
# ===============================
@app.route("/ai-workout", methods=["GET", "POST"])
def ai_workout():
    if "user" not in session:
        return redirect(url_for("login"))

    workout_plan = None

    if request.method == "POST":
        goal = request.form["goal"]
        days = int(request.form["days"])
        level = request.form["level"]

        workout_plan = generate_workout(goal, days, level)

    return render_template("ai_workout.html", workout_plan=workout_plan)


# ===============================
# WORKOUT GENERATOR FUNCTION
# ===============================
def generate_workout(goal, days, level):

    plan = {}

    # ==============================
    # MUSCLE GAIN
    # ==============================
    if goal == "Muscle Gain":

        if days >= 6:
            split = ["Push", "Pull", "Legs", "Push", "Pull", "Legs"]
        elif days == 5:
            split = ["Chest", "Back", "Legs", "Shoulders", "Arms"]
        else:
            split = ["Upper Body", "Lower Body", "Rest", "Upper Body"]

        exercises = {
            "Push": "Flat Bench Press 3x10,\n"
                    "Incline Bench Press 3x10,"
                    "Chest Flies 3x10,"
                    "Shoulder Press 3x12,"
                    "Lateral Raises 3x10,"
                    "Tricep Pushdowns 3x12,"
                    "French Curls 3x10",
            "Pull": "Pull-ups 2x8, Barbell Rows 3x10,Lat Pulldown 3x10 , Bicep Curls 3x12, Hammer Curls 3x12",
            "Legs": "Squats 4x8, Leg Press 3x12, Hamstring Curls 3x12,Leg Extensions 3x12, Calf Raises 2x15",
            "Chest": "Incline Press 3x10, Chest Fly 3x12,Pushups 3x15",
            "Back": "Lat Pulldown 4x10, Seated Row 3x12,Deadlifts 3x8",
            "Shoulders": "Overhead Press 4x8, Lateral Raises 3x15,Rear Delt Fly 3x12",
            "Arms": "Barbell Curl 3x12, Tricep Pushdown 3x12,Preacher Curl 3x10, Skull Crushers 3x10",
            "Upper Body": "Bench Press, Rows, Shoulder Press (3x10 each)",
            "Lower Body": "Squats, Lunges, Leg Curl (3x12 each)"
        }

    # ==============================
    # WEIGHT LOSS
    # ==============================
    elif goal == "Weight Loss":

        split = ["Full Body + Cardio"] * days

        exercises = {
            "Full Body + Cardio":
            "Circuit Training 30 mins + 20 mins Treadmill + Core Workout"
        }

    # ==============================
    # STRENGTH
    # ==============================
    elif goal == "Strength":

        split = ["Heavy Upper", "Heavy Lower"] * (days // 2)

        exercises = {
            "Heavy Upper":
            "Bench Press 5x5, Pull-ups 5x5, Overhead Press 5x5",

            "Heavy Lower":
            "Squats 5x5, Deadlift 5x5, Leg Press 4x8"
        }

    # ==============================
    # EXPERIENCE LEVEL ADJUSTMENT
    # ==============================

    volume_note = ""

    if level == "Beginner":
        volume_note = "Focus on form. Moderate weight."
    elif level == "Intermediate":
        volume_note = "Progressive overload recommended."
    elif level == "Advanced":
        volume_note = "High intensity. Add drop sets & supersets."

    # ==============================
    # BUILD FINAL PLAN
    # ==============================

    for i in range(len(split)):
        day_name = f"Day {i+1}"
        workout_type = split[i]

        if workout_type in exercises:
            plan[day_name] = exercises[workout_type] + " | " + volume_note
        else:
            plan[day_name] = "Rest or Active Recovery"

    return plan



# ===============================
# LOGOUT
# ===============================

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


# ===============================
# RUN APP
# ===============================

if __name__ == "__main__":
    app.run(debug=True)