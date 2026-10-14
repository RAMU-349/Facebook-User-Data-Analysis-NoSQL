import os
from datetime import datetime

import pandas as pd
import streamlit as st
from pymongo import MongoClient
from pymongo.errors import PyMongoError


st.set_page_config(
    page_title="Facebook User Data Analysis",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Facebook User Data Analysis Using NoSQL")
st.caption(
    "A MongoDB-based demonstration of user activity, CRUD operations, "
    "filtering, and aggregation."
)

DEFAULT_URI = "mongodb://localhost:27017"
DATABASE_NAME = "facebook_analysis"
COLLECTION_NAME = "facebook_users"

SAMPLE_USERS = [
    {
        "user_id": 101,
        "name": "User A",
        "age_group": "18-25",
        "posts": 12,
        "likes_received": 150,
        "comments_received": 35,
        "shares_received": 20,
        "friends_count": 320,
    },
    {
        "user_id": 102,
        "name": "User B",
        "age_group": "26-35",
        "posts": 8,
        "likes_received": 90,
        "comments_received": 18,
        "shares_received": 12,
        "friends_count": 250,
    },
    {
        "user_id": 103,
        "name": "User C",
        "age_group": "18-25",
        "posts": 20,
        "likes_received": 240,
        "comments_received": 60,
        "shares_received": 35,
        "friends_count": 410,
    },
    {
        "user_id": 104,
        "name": "User D",
        "age_group": "36-45",
        "posts": 5,
        "likes_received": 45,
        "comments_received": 10,
        "shares_received": 5,
        "friends_count": 180,
    },
    {
        "user_id": 105,
        "name": "User E",
        "age_group": "26-35",
        "posts": 15,
        "likes_received": 180,
        "comments_received": 42,
        "shares_received": 25,
        "friends_count": 350,
    },
]


def make_dataframe(documents):
    """Convert MongoDB documents to a display-friendly DataFrame."""
    if not documents:
        return pd.DataFrame()

    frame = pd.DataFrame(documents)

    if "_id" in frame.columns:
        frame = frame.drop(columns=["_id"])

    return frame


def get_collection(uri):
    """Connect to MongoDB and return the collection."""
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    collection = client[DATABASE_NAME][COLLECTION_NAME]
    return client, collection


with st.sidebar:
    st.header("⚙️ Database Settings")

    mongo_uri = st.text_input(
        "MongoDB connection URI",
        value=os.getenv("MONGODB_URI", DEFAULT_URI),
        type="password",
        help="Use a local MongoDB URI or your MongoDB Atlas connection URI.",
    )

    st.caption(f"Database: `{DATABASE_NAME}`")
    st.caption(f"Collection: `{COLLECTION_NAME}`")

    connect_clicked = st.button("Connect to MongoDB", use_container_width=True)

    if connect_clicked:
        st.session_state["check_connection"] = True

    st.divider()
    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "View Users",
            "CRUD Operations",
            "Activity Filters",
            "Aggregation Analysis",
        ],
    )


try:
    client, collection = get_collection(mongo_uri)
except (PyMongoError, ValueError) as exc:
    st.error("Could not connect to MongoDB.")
    st.info(
        "Start your local MongoDB server, or enter a valid MongoDB Atlas "
        "connection URI in the sidebar."
    )
    with st.expander("Connection error details"):
        st.code(str(exc))
    st.stop()


def load_users():
    return list(collection.find({}, {"_id": 0}).sort("user_id", 1))


def seed_sample_data():
    """Insert demonstration records only when the collection is empty."""
    if collection.count_documents({}) == 0:
        collection.insert_many(SAMPLE_USERS)
        return len(SAMPLE_USERS)
    return 0


if page == "Dashboard":
    st.subheader("Dashboard Overview")

    left, right = st.columns([3, 1])

    with left:
        st.write(
            "Explore anonymized demonstration records using a MongoDB "
            "NoSQL document database."
        )

    with right:
        if st.button("Insert Sample Dataset", type="primary"):
            try:
                inserted = seed_sample_data()
                if inserted:
                    st.success(f"Inserted {inserted} sample records.")
                else:
                    st.info(
                        "The collection already contains data. "
                        "Existing records were not changed."
                    )
                st.rerun()
            except PyMongoError as exc:
                st.error(f"Could not insert sample records: {exc}")

    users = load_users()

    if not users:
        st.warning("The collection is empty. Click Insert Sample Dataset.")
    else:
        df = make_dataframe(users)

        total_users = len(df)
        total_posts = int(df["posts"].sum())
        total_likes = int(df["likes_received"].sum())
        total_comments = int(df["comments_received"].sum())
        total_shares = int(df["shares_received"].sum())

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Users", total_users)
        c2.metric("Posts", total_posts)
        c3.metric("Likes Received", total_likes)
        c4.metric("Comments", total_comments)
        c5.metric("Shares", total_shares)

        st.subheader("User Activity Overview")

        chart_columns = [
            "name",
            "posts",
            "likes_received",
            "comments_received",
            "shares_received",
        ]

        st.bar_chart(df.set_index("name")[chart_columns[1:]])

        st.subheader("Age Group Summary")

        age_summary = (
            df.groupby("age_group", as_index=False)
            .agg(
                users=("user_id", "count"),
                total_posts=("posts", "sum"),
                total_likes=("likes_received", "sum"),
                average_friends=("friends_count", "mean"),
            )
        )

        age_summary["average_friends"] = age_summary[
            "average_friends"
        ].round(2)

        st.dataframe(age_summary, use_container_width=True)

        st.download_button(
            "Download Dashboard Data (CSV)",
            df.to_csv(index=False).encode("utf-8"),
            file_name="facebook_user_analysis.csv",
            mime="text/csv",
        )


elif page == "View Users":
    st.subheader("👥 User Records")

    users = load_users()

    if users:
        df = make_dataframe(users)
        st.dataframe(df, use_container_width=True)

        search_name = st.text_input("Search by name")
        if search_name:
            filtered = df[
                df["name"].str.contains(
                    search_name, case=False, na=False
                )
            ]
            st.dataframe(filtered, use_container_width=True)

        st.download_button(
            "Export All Users to CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="facebook_users.csv",
            mime="text/csv",
        )
    else:
        st.info("No records found. Insert the sample dataset from Dashboard.")


elif page == "CRUD Operations":
    st.subheader("➕ Create, Read, Update and Delete")

    operation = st.selectbox(
        "Select operation",
        ["Add User", "Update User", "Delete User"],
    )

    if operation == "Add User":
        with st.form("add_user_form"):
            user_id = st.number_input(
                "User ID", min_value=1, step=1
            )
            name = st.text_input("Display Name")
            age_group = st.selectbox(
                "Age Group", ["18-25", "26-35", "36-45", "46+"]
            )

            posts = st.number_input("Posts", min_value=0, step=1)
            likes = st.number_input(
                "Likes Received", min_value=0, step=1
            )
            comments = st.number_input(
                "Comments Received", min_value=0, step=1
            )
            shares = st.number_input(
                "Shares Received", min_value=0, step=1
            )
            friends = st.number_input(
                "Friends Count", min_value=0, step=1
            )

            submitted = st.form_submit_button("Add User")

        if submitted:
            if not name.strip():
                st.error("Please enter a display name.")
            elif collection.find_one({"user_id": int(user_id)}):
                st.error("That user ID already exists.")
            else:
                document = {
                    "user_id": int(user_id),
                    "name": name.strip(),
                    "age_group": age_group,
                    "posts": int(posts),
                    "likes_received": int(likes),
                    "comments_received": int(comments),
                    "shares_received": int(shares),
                    "friends_count": int(friends),
                }

                try:
                    collection.insert_one(document)
                    st.success("User added successfully.")
                    st.rerun()
                except PyMongoError as exc:
                    st.error(f"Insert failed: {exc}")

    elif operation == "Update User":
        users = load_users()

        if not users:
            st.info("There are no users to update.")
        else:
            ids = [int(user["user_id"]) for user in users]
            selected_id = st.selectbox("Select User ID", ids)
            current = collection.find_one({"user_id": selected_id})

            with st.form("update_user_form"):
                name = st.text_input("Display Name", current["name"])
                age_group = st.selectbox(
                    "Age Group",
                    ["18-25", "26-35", "36-45", "46+"],
                    index=[
                        "18-25", "26-35", "36-45", "46+"
                    ].index(current["age_group"]),
                )
                posts = st.number_input(
                    "Posts", min_value=0, step=1,
                    value=int(current["posts"])
                )
                likes = st.number_input(
                    "Likes Received", min_value=0, step=1,
                    value=int(current["likes_received"])
                )
                comments = st.number_input(
                    "Comments Received", min_value=0, step=1,
                    value=int(current["comments_received"])
                )
                shares = st.number_input(
                    "Shares Received", min_value=0, step=1,
                    value=int(current["shares_received"])
                )
                friends = st.number_input(
                    "Friends Count", min_value=0, step=1,
                    value=int(current["friends_count"])
                )

                submitted = st.form_submit_button("Save Changes")

            if submitted:
                if not name.strip():
                    st.error("Please enter a display name.")
                else:
                    try:
                        collection.update_one(
                            {"user_id": selected_id},
                            {
                                "$set": {
                                    "name": name.strip(),
                                    "age_group": age_group,
                                    "posts": int(posts),
                                    "likes_received": int(likes),
                                    "comments_received": int(comments),
                                    "shares_received": int(shares),
                                    "friends_count": int(friends),
                                    "updated_at": datetime.now().isoformat(),
                                }
                            },
                        )
                        st.success("User updated successfully.")
                        st.rerun()
                    except PyMongoError as exc:
                        st.error(f"Update failed: {exc}")

    else:
        users = load_users()

        if not users:
            st.info("There are no users to delete.")
        else:
            ids = [int(user["user_id"]) for user in users]
            selected_id = st.selectbox("User ID to delete", ids)

            confirm = st.checkbox(
                "I confirm that I want to delete this record."
            )

            if st.button("Delete Selected User", type="primary"):
                if not confirm:
                    st.warning("Confirm the deletion first.")
                else:
                    try:
                        result = collection.delete_one(
                            {"user_id": selected_id}
                        )
                        if result.deleted_count:
                            st.success("User deleted successfully.")
                            st.rerun()
                        else:
                            st.warning("User record was not found.")
                    except PyMongoError as exc:
                        st.error(f"Delete failed: {exc}")


elif page == "Activity Filters":
    st.subheader("🔍 Filter and Sort Activity")

    users = load_users()

    if not users:
        st.info("Insert the sample dataset from Dashboard first.")
    else:
        df = make_dataframe(users)

        age_groups = sorted(df["age_group"].dropna().unique().tolist())
        selected_groups = st.multiselect(
            "Select age groups",
            age_groups,
            default=age_groups,
        )

        min_posts = st.number_input(
            "Minimum number of posts", min_value=0, value=0, step=1
        )
        min_likes = st.number_input(
            "Minimum likes received", min_value=0, value=0, step=1
        )

        sort_by = st.selectbox(
            "Sort by",
            [
                "posts",
                "likes_received",
                "comments_received",
                "shares_received",
                "friends_count",
            ],
        )

        descending = st.checkbox("Highest values first", value=True)

        filtered = df[
            df["age_group"].isin(selected_groups)
            & (df["posts"] >= min_posts)
            & (df["likes_received"] >= min_likes)
        ].sort_values(sort_by, ascending=not descending)

        st.write(f"Matching records: {len(filtered)}")
        st.dataframe(filtered, use_container_width=True)

        st.download_button(
            "Download Filtered Results",
            filtered.to_csv(index=False).encode("utf-8"),
            file_name="filtered_facebook_users.csv",
            mime="text/csv",
        )


elif page == "Aggregation Analysis":
    st.subheader("📈 MongoDB Aggregation Analysis")

    analysis = st.selectbox(
        "Choose an analysis",
        [
            "Activity by Age Group",
            "Top Users by Likes",
            "Overall Activity Summary",
        ],
    )

    if analysis == "Activity by Age Group":
        pipeline = [
            {
                "$group": {
                    "_id": "$age_group",
                    "user_count": {"$sum": 1},
                    "total_posts": {"$sum": "$posts"},
                    "total_likes": {"$sum": "$likes_received"},
                    "total_comments": {"$sum": "$comments_received"},
                    "total_shares": {"$sum": "$shares_received"},
                }
            },
            {"$sort": {"_id": 1}},
        ]

    elif analysis == "Top Users by Likes":
        pipeline = [
            {
                "$project": {
                    "_id": 0,
                    "user_id": 1,
                    "name": 1,
                    "age_group": 1,
                    "likes_received": 1,
                    "posts": 1,
                }
            },
            {"$sort": {"likes_received": -1}},
        ]

    else:
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "user_count": {"$sum": 1},
                    "total_posts": {"$sum": "$posts"},
                    "total_likes": {"$sum": "$likes_received"},
                    "total_comments": {"$sum": "$comments_received"},
                    "total_shares": {"$sum": "$shares_received"},
                    "average_posts": {"$avg": "$posts"},
                    "average_likes": {"$avg": "$likes_received"},
                }
            },
            {"$project": {"_id": 0}},
        ]

    try:
        results = list(collection.aggregate(pipeline))

        if results:
            result_df = pd.DataFrame(results)
            st.dataframe(result_df, use_container_width=True)
            st.download_button(
                "Download Aggregation Results",
                result_df.to_csv(index=False).encode("utf-8"),
                file_name="mongodb_aggregation_results.csv",
                mime="text/csv",
            )
        else:
            st.info("No aggregation results. Add data first.")
    except PyMongoError as exc:
        st.error(f"Aggregation failed: {exc}")


st.divider()
st.caption(
    "Academic demonstration only. The sample dataset is synthetic and "
    "does not contain actual Facebook user data."
)

client.close()