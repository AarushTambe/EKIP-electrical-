import streamlit as st

from db.database import fetch_one, fetch_all


def get_dashboard_counts():
    """Get basic application statistics."""

    users = fetch_one(
        "SELECT COUNT(*) AS count FROM users;"
    )

    subjects = fetch_one(
        "SELECT COUNT(*) AS count FROM subjects;"
    )

    documents = fetch_one(
        "SELECT COUNT(*) AS count FROM documents;"
    )

    pending = fetch_one(
        """
        SELECT COUNT(*) AS count
        FROM submissions
        WHERE status = 'pending';
        """
    )

    return {
        "users": users["count"],
        "subjects": subjects["count"],
        "documents": documents["count"],
        "pending": pending["count"],
    }


def get_recent_submissions():
    """Get recent source submissions."""

    return fetch_all(
        """
        SELECT
            submissions.id,
            submissions.title,
            submissions.source_file,
            submissions.status,
            submissions.created_at,
            users.name AS submitted_by,
            subjects.name AS subject_name
        FROM submissions
        JOIN users
            ON submissions.submitted_by = users.id
        LEFT JOIN subjects
            ON submissions.subject_id = subjects.id
        ORDER BY submissions.created_at DESC
        LIMIT 10;
        """
    )


def show_dashboard(user):
    """Display the EKIP administrator dashboard."""

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    with st.sidebar:

        st.title("⚡ EKIP")

        st.caption(
            "Electrical Knowledge & Intelligence Platform"
        )

        st.divider()

        st.caption("ADMINISTRATOR")

        st.write(
            f"Logged in as: **{user['name']}**"
        )

        st.caption(
            f"Username: {user['username']}"
        )

        st.caption("Role: Administrator")

        st.divider()

        st.caption("ADMIN")

        st.write("📊 Dashboard")
        st.write("📥 Submissions")
        st.write("📚 Documents")

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.title("⚡ EKIP Admin Dashboard")

    st.caption(
        "Manage the Electrical Engineering knowledge platform."
    )

    st.divider()

    # --------------------------------------------------------
    # OVERVIEW
    # --------------------------------------------------------

    st.subheader("Overview")

    try:
        counts = get_dashboard_counts()

    except Exception as error:

        st.error(
            f"Could not load dashboard data: {error}"
        )

        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Users",
            counts["users"],
        )

    with col2:
        st.metric(
            "Subjects",
            counts["subjects"],
        )

    with col3:
        st.metric(
            "Documents",
            counts["documents"],
        )

    with col4:
        st.metric(
            "Pending Submissions",
            counts["pending"],
        )

    st.divider()

    # --------------------------------------------------------
    # RECENT SUBMISSIONS
    # --------------------------------------------------------

    st.subheader("Recent Submissions")

    try:
        submissions = get_recent_submissions()

    except Exception as error:

        st.error(
            f"Could not load submissions: {error}"
        )

        return

    if not submissions:

        st.info(
            "No source submissions have been made yet."
        )

    else:

        for submission in submissions:

            with st.container(border=True):

                col1, col2 = st.columns([4, 1])

                with col1:

                    st.write(
                        f"### {submission['title']}"
                    )

                    st.caption(
                        f"File: {submission['source_file']}"
                    )

                    st.caption(
                        f"Submitted by: "
                        f"{submission['submitted_by']}"
                    )

                    if submission["subject_name"]:

                        st.caption(
                            f"Subject: "
                            f"{submission['subject_name']}"
                        )

                with col2:

                    st.write(
                        f"**{submission['status'].capitalize()}**"
                    )

    st.divider()

    # --------------------------------------------------------
    # CURRENT SCOPE
    # --------------------------------------------------------

    st.subheader("System Status")

    st.info(
        "Submission approval and document ingestion "
        "will be enabled in the next project phases."
    )