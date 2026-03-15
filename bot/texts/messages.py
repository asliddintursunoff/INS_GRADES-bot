START_MESSAGE = """✨ <b>Welcome to Ins Grades Study Bot!</b> ✨

📚 <b>Features:</b>
🗓 <b>Timetable</b> – All classes at a glance.
⏰ <b>Reminders</b> – Daily morning class lists.
⏱ <b>Alerts</b> – 15 minutes before class starts.

💎 <b>Premium Upgrade</b> – Only 5 000 so'm!
📝 <b>Assignments</b> – Stay on track with homework.
📝 <b>Quizzes</b> – Prepare and ace every quiz.
🚀 <b>Deadline Alerts</b> – Never miss an event.

🔥 <b>Upgrade for a stress-free study life!</b>"""

START_WELCOME = """👋 <b>Welcome back!</b>

💎 <b>Premium Benefits:</b>
📚 Assignment reminders
🧠 Quiz alerts
⏰ Deadline notifications

💰 <b>Price: 5 000 so'm</b>"""

ASK_STUDENT_ID = "Enter your <b>Student ID</b> (e.g., <i>U2410252</i>):"
INVALID_STUDENT_ID = "❌ <b>Incorrect ID.</b>\n\nUse <b>U + 7 digits</b> (e.g., <i>U2410252</i>):"
CONFIRM_REGISTRATION = "Confirm Student ID: <b>{student_id}</b>\n\nCorrect?"
NOT_REGISTERED = "⚠️ <b>Bro, you are not registered!</b>\n\nRegister now to start using the bot."

REGISTRATION_SUCCESS = "✅ <b>Registration successful!</b>"
SUBSCRIPTION_EXPIRED = "⚠️ <b>Subscription expired!</b>\n\nPlease subscribe again to access Assignments and Quizzes."

PREMIUM_ACTIVATION = """⭐ <b>Premium Activation</b>

💎 <b>Premium Features:</b>
📝 <b>Reminders</b> about new <b>assignments</b>.
🧠 <b>Alerts</b> for upcoming <b>quizzes</b>.
⏰ <b>Notifications</b> for all <b>deadlines</b>.

💰 Price: <b>5 000 so'm</b>
💳 Card: <code>5614 6868 3508 2374</code>
👤 Holder: <b>ASLIDDIN TURSUNOV</b>
<i>(Tap card number to copy)</i>

Pay with <b>Click</b> or <b>Payme</b> and send the <b>screenshot</b> here.

⏳ Verification: <b>1–3 minutes</b>.

Admin: 👤 @asliddin_tursunoff"""

RECEIPT_EXAMPLE_TEXT = """📷 <b>Receipt Example</b>

Visible items needed:
• Receiver name & card
• Amount & Transaction ID"""

TIMETABLE_HEADER = "📅 <b>{name}</b> — <b>{group}</b>"
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

PAYMENT_WAITING = "⏳ <b><i>Checking receipt...</i></b>\n\nWait <b>1–3 minutes</b>! 🕒"

PAYMENT_SUCCESS = """✅ <b>Premium activated!</b>

You now have <b>Premium</b> subscription.
Every day you will get <b>reminders</b> about new <b>assignments</b> and <b>quizzes</b>.

Enjoy your study! 🚀"""

PAYMENT_ERROR = """❌ <b>Verification failed.</b>

{error_details}

Send the <b>correct</b> image or click <b>Back</b>.
Admin: 👤 @asliddin_tursunoff"""

BTN_TIMETABLE = "📅 Timetable"
BTN_BUY_PREMIUM = "⭐ Premium"
BTN_ASSIGNMENTS = "📚 Assignments"
BTN_BACK = "⬅ Back"
BTN_YES = "✅ Yes"
BTN_NO = "❌ No"

PAYMENT_ASK_PHOTO = "Please send a photo of your receipt."
SESSION_EXPIRED = "⚠️ <b>Session expired.</b> Try /start."
ASSIGNMENTS_EMPTY = "📚 <b>No assignments yet.</b>"
ASSIGNMENTS_ERROR = "❌ <b>Could not fetch assignments.</b>"
TIMETABLE_ERROR = "❌ <b>Could not fetch timetable.</b>"
