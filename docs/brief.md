# Taskboard brief · v1

**One-liner.** A simple, reliable place to capture tasks and see what is due next.

**Users.** Individuals managing personal and work tasks who switch between laptop and phone.
Not yet: teams who need to share and assign tasks.

**Problem.** People need one place to capture tasks and see what is due next, because tasks are
scattered across notes, chats and memory. Today they use sticky notes and phone reminders, which
are easily lost and don't show the full picture.

**Application type.** Hosted, responsive web application with a backend API and a database.

**Key journeys.** Capture a task quickly · see what is due next · mark tasks done.

**First useful version** (each has tests in `tests/`):
- Sign up and sign in; signed-out users see nothing private.
- Create, edit and delete tasks; title required (max 200 characters).
- Optional due date: a calendar date, today or later, where "today" is the user's local date.
- Mark as done; done tasks move to a Completed list.
- My tasks: soonest due first, undated last, overdue highlighted with icon and text.
- Users can only ever see and change their own tasks.

**Later.** Email reminders (done), labels (done), priorities, team sharing, mobile app.
**Not doing for now.** Attachments, time tracking, AI suggestions, calendar sync.

**Decided.** "Today" uses the user's time zone, saved on their profile.
**Still open.** How long are deleted tasks kept? (Currently: deleted immediately.)
