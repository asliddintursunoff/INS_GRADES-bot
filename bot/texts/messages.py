START_MESSAGE = """✨ <b>Welcome to Ins Grades Study Bot!</b> ✨

Stay on top of your classes and never miss a deadline again! Here's what our bot can do for you:

📚 <b>Free Features:</b>

🗓 <b>Timetable View</b> – Check all your classes at a glance.

⏰ <b>Morning Reminder</b> – Get a friendly notification every morning about today's classes.

⏱ <b>15-Minute Pre-Class Alert</b> – Never be late with reminders just before your class starts.

💎 <b>Premium Upgrade</b> – Only 5 000 so'm! <i>(Totally worth it)</i>

📝 <b>Assignment Reminders</b> – Stay on track with all your homework.

📝 <b>Quiz Reminders</b> – Prepare ahead and ace every quiz.

🚀 <b>Never Miss Anything</b> – All important events delivered straight to you.

🔥 <b>Upgrade today and make your study life easier, smarter, and stress-free!</b>"""

START_WELCOME = """👋 <b>Welcome back!</b>

With Premium you get:

📚 Assignment reminders
🧠 Quiz alerts
⏰ Deadline notifications
📅 Easy timetable access

💰 <b>Premium price: only 5 000 so'm</b>

Activate Premium to unlock all features."""

ASK_STUDENT_ID = "Please enter your <b>Student ID</b> (e.g., <i>U2410252</i>):"
INVALID_STUDENT_ID = "❌ <b>Incorrect Student ID.</b>\n\nPlease enter a valid ID starting with <b>U</b> followed by <b>7 digits</b> (e.g., <i>U2410252</i>):"
CONFIRM_REGISTRATION = "Confirming registration for Student ID: <b>{student_id}</b>\n\nIs this correct?"
NOT_REGISTERED = "⚠️ <b>Bro, you are not registered!</b>\n\nPlease register again to use the bot features."

REGISTRATION_SUCCESS = "✅ <b>Registration successful!</b>"
SESSION_EXPIRED = "⚠️ <b>Session expired.</b> Please click /start again."

PREMIUM_ACTIVATION = """⭐ <b>Premium Activation</b>

Price: <b>5 000 so'm</b>

Payment methods:
• Payme
• Click

📷 Send a screenshot of your payment receipt.

⏳ Verification takes about <b>1–3 minutes</b>.

If something goes wrong contact admin:
👤 @asliddin_tursunoff"""

RECEIPT_EXAMPLE_TEXT = """📷 <b>Receipt Example</b>

Your screenshot should look similar to these examples.

Make sure the following are visible:

• receiver name
• receiver card
• payment amount
• transaction ID"""

TIMETABLE_HEADER = "📅 <b>{name}</b> — Group: <b>{group}</b>"
TIMETABLE_DAY_HEADER = "\n\n📅 <b>{day}</b>"
TIMETABLE_ITEM = "\n🕒 <b>{start_time}–{end_time}</b> | 📘 <i>{abbr}</i> — {subject} | 🏫 {room}"

ASSIGNMENTS_HEADER = "📚 <b>Available Tasks</b>\n"
ASSIGNMENT_ITEM = """
📝 {subject_name}
📌 {name}
Type: {type}
⏰ Deadline: {deadline}
⌛ Time left: {time_left}

🔗 <a href="{url}">Open Task</a>
"""

PAYMENT_WAITING = "⏳ <b><i>Checking your receipt...</i></b>\n\nIt might take <b>1–3 minutes</b>, please wait! 🕒"

PAYMENT_ERROR = """❌ <b>Payment verification failed.</b>

{error_details}

Please send the <b>correct</b> receipt image again or click the <b>Back</b> button.

If the problem continues, contact admin:
👤 @asliddin_tursunoff"""

BTN_TIMETABLE = "📅 Timetable"
BTN_BUY_PREMIUM = "⭐ Premium"
BTN_ASSIGNMENTS = "📚 Assignments"
BTN_BACK = "⬅ Back"
BTN_YES = "✅ Yes"
BTN_NO = "❌ No"

PAYMENT_ASK_PHOTO = "Please send a photo of your receipt."
ASSIGNMENTS_ERROR = "❌ <b>No assignments found or access denied.</b>"
TIMETABLE_ERROR = "❌ <b>Could not fetch timetable.</b>"
