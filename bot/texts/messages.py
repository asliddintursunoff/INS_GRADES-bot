START_WELCOME = """👋 <b>Welcome to INS Assistant</b>

This bot helps you stay on track at university.

With Premium you get:

📚 Assignment reminders
🧠 Quiz alerts
⏰ Deadline notifications
📅 Easy timetable access

No more missed deadlines.

💰 <b>Premium price: only 5 000 so'm</b>

Activate Premium to start using the bot."""

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
TIMETABLE_DAY_HEADER = "\n📅 <b>{day}</b>"
TIMETABLE_ITEM = "\n🕒 {start_time}–{end_time} | 📘 {abbr} — {subject} | 🏫 {room}"

ASSIGNMENTS_HEADER = "📚 <b>Available Tasks</b>\n"
ASSIGNMENT_ITEM = """
📝 {subject_name}
📌 {name}
Type: {type}
⏰ Deadline: {deadline}
⌛ Time left: {time_left}

🔗 <a href="{url}">Open Task</a>
"""

PAYMENT_ERROR = """❌ Payment verification failed.

Please send a clear screenshot of the correct receipt and wait 1–3 minutes.

If the problem continues contact admin:
👤 @asliddin_tursunoff"""

BTN_TIMETABLE = "📅 Timetable"
BTN_BUY_PREMIUM = "⭐ Premium"
BTN_ASSIGNMENTS = "📚 Assignments"
BTN_BACK = "⬅ Back"

ASK_STUDENT_ID = "Please enter your student ID:"
REGISTRATION_SUCCESS = "✅ <b>Registration successful!</b>"
SESSION_EXPIRED = "⚠️ <b>Session expired.</b> Please click /start again."
PAYMENT_SUCCESS = "✅ <b>Payment received successfully! Premium activated.</b>"
PAYMENT_ASK_PHOTO = "Please send a photo of your receipt."
ASSIGNMENTS_ERROR = "❌ <b>No assignments found or access denied.</b>"
TIMETABLE_ERROR = "❌ <b>Could not fetch timetable.</b>"
