START_HELLO = """<b>👋 Hello, {first_name} {last_name}!</b>

Welcome to <b>INS Grades Assistant</b>.

With this bot you can:

📅 View your weekly timetable
📚 Track assignments and quizzes
⏰ Never miss important deadlines

Your current plan:
{plan_info}

{upgrade_info}
"""

PREMIUM_USER = "<b>🌟 Premium Plan</b>"
FREE_USER = "<b>🆓 Free Plan</b>"
UPGRADE_PROMPT = "Upgrade to <b>⭐ Premium</b> to unlock assignment tracking and deadline reminders."

ASK_STUDENT_ID = "Please enter your student ID:"
REGISTRATION_SUCCESS = "✅ <b>Registration successful!</b>"
REGISTRATION_ERROR_RETRIEVING = "❌ <b>Error retrieving user after registration.</b>"
REGISTRATION_FAILED = "❌ <b>Registration failed.</b> Please try again."

TIMETABLE_HEADER = "<b>📅 Weekly Timetable</b>"
TIMETABLE_DAY_HEADER = "\n<b>{day}</b>\n"
TIMETABLE_ITEM = """
🕘 <b>{start_time} – {end_time}</b>
📚 {subject}
👨‍🏫 {professor}
🏫 Room: {room}
"""
TIMETABLE_ERROR = "❌ <b>Could not fetch timetable.</b>"

PREMIUM_INFO = """<b>⭐ Premium Features</b>

Upgrade your experience and never miss deadlines.

Premium includes:

📚 Assignment reminders
🧠 Quiz alerts
⏰ Deadline notifications

💰 Price: {price} USD

To activate Premium please send a screenshot of your payment receipt.

After verification your subscription will be activated automatically.
"""

PAYMENT_SUCCESS = "✅ <b>Payment received successfully! Premium activated.</b>"
PAYMENT_FAILED = """❌ <b>Payment verification failed.</b>

Please make sure the receipt is clear and try again.

If the problem continues please contact the administrator.
"""
PAYMENT_ASK_PHOTO = "Please send a photo of your receipt."

ASSIGNMENTS_HEADER = "<b>📚 Available Assignments</b>\n"
ASSIGNMENT_ITEM = """
<b>{subject}</b>
📝 {task}
⏰ Deadline: {deadline}
⌛ Time left: {time_left}

🔗 <a href="{url}">Open Assignment</a>
"""
QUIZZES_SUBHEADER = "\n<b>📝 Quizzes</b>\n"
QUIZ_ITEM = """
<b>{subject}</b>
📝 {title}
⏰ Deadline: {deadline}
⌛ Time left: {time_left}

🔗 <a href="{url}">Open Quiz</a>
"""
ASSIGNMENTS_ERROR = "❌ <b>No assignments found or access denied.</b>"

BTN_TIMETABLE = "📅 Timetable"
BTN_BUY_PREMIUM = "⭐ Buy Premium"
BTN_ASSIGNMENTS = "📚 Assignments"
BTN_BACK = "⬅ Back"

SESSION_EXPIRED = "⚠️ <b>Session expired.</b> Please click /start again."
MAIN_MENU_LABEL = "<b>Main Menu</b>"
