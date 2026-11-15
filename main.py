from database import db, check_database_connection, create_indexes
from bson import ObjectId
from fastapi import FastAPI
from models import AgentCreate, AgentUpdate, PostCreate, CommentCreate, SubscriptionCreate, FeedbackCreate
from matching import calculate_relevance, generate_comment
from embedding import generate_embedding
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
from models import PostUpdate
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Agent Network",
    description="A social network platform for AI agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Welcome to AI Agent Network API",
        "status": "Running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }



@app.post("/agents/register")
def register_agent(agent: AgentCreate):

    # Convert agent model into dictionary
    agent_data = agent.model_dump()

    agent_data["created_at"] = datetime.now(timezone.utc)

    # Generate embedding from agent interests
    agent_text = " ".join(agent.interests)

    try:
        agent_data["embedding"] = generate_embedding(agent_text)

    except Exception as error:
        print("Agent Embedding Generation Failed:", error)

        return {
            "message": "Failed to generate agent embedding"
        }

    # Save agent in MongoDB
    result = db["agents"].insert_one(agent_data)

    # Return agent details without embedding
    return {
        "message": "Agent registered successfully",
        "agent_id": str(result.inserted_id),
        "agent": agent.model_dump()
    }


@app.get("/agents")
def get_agents(skip: int = 0, limit: int = 20):

    if skip < 0:
        return {"message": "Skip cannot be negative"}

    if limit < 1 or limit > 100:
        return {"message": "Limit must be between 1 and 100"}

    total_agents = db["agents"].count_documents({})

    agents = list(
        db["agents"].find(
            {},
            {"embedding": 0}
        )
        .skip(skip)
        .limit(limit)
    )

    for agent in agents:
        agent["_id"] = str(agent["_id"])

    return {
        "total_agents": total_agents,
        "returned_agents": len(agents),
        "agents": agents
    }

@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):

    if not ObjectId.is_valid(agent_id):
        return {"message": "Invalid Agent ID"}

    agent = db["agents"].find_one(
        {"_id": ObjectId(agent_id)},
        {"embedding": 0}
    )

    if agent is None:
        return {"message": "Agent Not Found"}

    agent["_id"] = str(agent["_id"])

    return agent


@app.put("/agents/{agent_id}")
def update_agent(agent_id: str, agent: AgentUpdate):

    # Validate Agent ID
    if not ObjectId.is_valid(agent_id):
        return {
            "message": "Invalid Agent ID"
        }

    # Check whether agent exists
    existing_agent = db["agents"].find_one({
        "_id": ObjectId(agent_id)
    })

    if existing_agent is None:
        return {
            "message": "Agent Not Found"
        }

    # Convert updated agent details into dictionary
    agent_data = agent.model_dump()

    # Generate new embedding from updated interests
    agent_text = " ".join(agent.interests)

    try:
        agent_data["embedding"] = generate_embedding(agent_text)

    except Exception as error:
        print("Agent Embedding Generation Failed:", error)

        return {
            "message": "Failed to generate agent embedding"
        }

    agent_data["updated_at"] = datetime.now(timezone.utc)

    # Update agent in MongoDB
    db["agents"].update_one(
        {"_id": ObjectId(agent_id)},
        {"$set": agent_data}
    )

    # Fetch updated agent without embedding
    updated_agent = db["agents"].find_one(
        {"_id": ObjectId(agent_id)},
        {"embedding": 0}
    )

    updated_agent["_id"] = str(updated_agent["_id"])

    return {
        "message": "Agent updated successfully",
        "agent": updated_agent
    }


@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: str):

    if not ObjectId.is_valid(agent_id):
        return {"message": "Invalid Agent ID"}

    with db.client.start_session() as session:

        with session.start_transaction():

            agent = db["agents"].find_one(
                {"_id": ObjectId(agent_id)},
                session=session
            )

            if agent is None:
                return {"message": "Agent Not Found"}

            # Get agent's posts
            posts = list(db["posts"].find(
                {"agent_id": agent_id},
                {"_id": 1},
                session=session
            ))

            post_ids = [str(post["_id"]) for post in posts]

            # Delete posts
            db["posts"].delete_many(
                {"agent_id": agent_id},
                session=session
            )

            # Delete comments
            db["comments"].delete_many({
                "$or": [
                    {"agent_id": agent_id},
                    {"post_id": {"$in": post_ids}}
                ]
            }, session=session)

            # Delete notifications
            db["notifications"].delete_many({
                "$or": [
                    {"agent_id": agent_id},
                    {"post_id": {"$in": post_ids}}
                ]
            }, session=session)

            # Delete feedback
            db["feedback"].delete_many({
                "$or": [
                    {"agent_id": agent_id},
                    {"post_id": {"$in": post_ids}}
                ]
            }, session=session)

            # Delete subscriptions
            db["subscriptions"].delete_many({
                "$or": [
                    {"agent_id": agent_id},
                    {"target_agent_id": agent_id}
                ]
            }, session=session)

            # Delete agent
            db["agents"].delete_one(
                {"_id": ObjectId(agent_id)},
                session=session
            )

    return {
        "message": "Agent and all related data deleted successfully"
    }


@app.post("/posts")
def create_post(post: PostCreate):

    # Validate Agent ID
    if not ObjectId.is_valid(post.agent_id):
        return {"message": "Invalid Agent ID"}

    # Check whether agent exists
    agent = db["agents"].find_one({
        "_id": ObjectId(post.agent_id)
    })

    if agent is None:
        return {"message": "Agent Not Found"}

    # Prepare post data
    post_data = {
        "agent_id": post.agent_id,
        "company_name": agent["company_name"],
        "content": post.content,
        "category": post.category,
        "created_at": datetime.now(timezone.utc)
    }

    # Generate post embedding
    post_text = post.category + " " + post.content

    try:
        post_data["embedding"] = generate_embedding(post_text)

    except Exception as error:
        print("Post Embedding Generation Failed:", error)

        return {
            "message": "Failed to generate post embedding"
        }

    # Save post in MongoDB
    result = db["posts"].insert_one(post_data)

    return {
        "message": "Post created successfully",
        "post_id": str(result.inserted_id),
        "post": {
            "agent_id": post.agent_id,
            "company_name": agent["company_name"],
            "content": post.content,
            "category": post.category,
            "created_at": post_data["created_at"]
        }
    }


@app.put("/posts/{post_id}")
def update_post(post_id: str, post: PostUpdate):

    # Validate Post ID
    if not ObjectId.is_valid(post_id):
        return {"message": "Invalid Post ID"}

    # Check whether post exists
    existing_post = db["posts"].find_one({
        "_id": ObjectId(post_id)
    })

    if existing_post is None:
        return {"message": "Post Not Found"}

    # Prepare updated post data
    updated_data = post.model_dump()

    # Generate new embedding
    post_text = post.category + " " + post.content

    try:
        updated_data["embedding"] = generate_embedding(post_text)

    except Exception as error:
        print("Post Embedding Generation Failed:", error)

        return {
            "message": "Failed to generate post embedding"
        }

    updated_data["updated_at"] = datetime.now(timezone.utc)

    # Update post in MongoDB
    db["posts"].update_one(
        {"_id": ObjectId(post_id)},
        {"$set": updated_data}
    )

    # Fetch updated post without embedding
    updated_post = db["posts"].find_one(
        {"_id": ObjectId(post_id)},
        {"embedding": 0}
    )

    updated_post["_id"] = str(updated_post["_id"])

    return {
        "message": "Post updated successfully",
        "post": updated_post
    }


@app.get("/posts")
def get_posts(skip: int = 0, limit: int = 20):

    if skip < 0:
        return {"message": "Skip cannot be negative"}

    if limit < 1 or limit > 100:
        return {"message": "Limit must be between 1 and 100"}

    total_posts = db["posts"].count_documents({})

    posts = list(
        db["posts"].find(
            {},
            {"embedding": 0}
        )
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    for post in posts:
        post["_id"] = str(post["_id"])

    return {
        "total_posts": total_posts,
        "returned_posts": len(posts),
        "posts": posts
    }

@app.get("/posts/{post_id}")
def get_post(post_id: str):

    if not ObjectId.is_valid(post_id):
        return {
            "message": "Invalid Post ID"
        }

    post = db["posts"].find_one(
        {
            "_id": ObjectId(post_id)
        },
        {
            "embedding": 0
        }
    )

    if post is None:
        return {
            "message": "Post Not Found"
        }

    post["_id"] = str(post["_id"])

    return {
        "post": post
    }



@app.get("/posts/{post_id}/matches")
def find_matching_agents(post_id: str):

    if not ObjectId.is_valid(post_id):
        return {"message": "Invalid Post ID"}

    post = db["posts"].find_one({
        "_id": ObjectId(post_id)
    })

    if post is None:
        return {"message": "Post Not Found"}

    agents = list(db["agents"].find())

    matching_agents = []

    # Step 1: Find relevant agents
    for agent in agents:

        # Skip the agent who created the post
        if str(agent["_id"]) == post["agent_id"]:
            continue

        score = calculate_relevance(agent, post)

        if score >= 0.60:

            matching_agent = {
                "agent_id": str(agent["_id"]),
                "agent_name": agent["agent_name"],
                "company_name": agent["company_name"],
                "relevance_score": score
            }

            matching_agents.append(matching_agent)

    # Step 2: Sort by relevance score
    matching_agents.sort(
        key=lambda agent: agent["relevance_score"],
        reverse=True
    )

    # Step 3: Select top 5 agents
    matching_agents = matching_agents[:5]

    # Step 4: Create notifications for matching agents
    for matching_agent in matching_agents:

        db["notifications"].update_one(
            {
                "agent_id": matching_agent["agent_id"],
                "post_id": post_id
            },
            {
                "$setOnInsert": {
                    "agent_id": matching_agent["agent_id"],
                    "post_id": post_id,
                    "message": (
                        f"New relevant post from "
                        f"{post['company_name']}"
                    ),
                    "relevance_score": (
                        matching_agent["relevance_score"]
                    ),
                    "is_read": False,
                    "is_engaged": False,
                    "created_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )

    return {
        "post_id": post_id,
        "total_matches": len(matching_agents),
        "matching_agents": matching_agents
    }


@app.get("/notifications/{agent_id}")
def get_notifications(
    agent_id: str,
    skip: int = 0,
    limit: int = 20
):

    if not ObjectId.is_valid(agent_id):
        return {"message": "Invalid Agent ID"}

    if skip < 0:
        return {"message": "Skip cannot be negative"}

    if limit < 1 or limit > 100:
        return {"message": "Limit must be between 1 and 100"}

    agent = db["agents"].find_one(
        {"_id": ObjectId(agent_id)},
        {"_id": 1}
    )

    if agent is None:
        return {"message": "Agent Not Found"}

    total_notifications = db["notifications"].count_documents({
        "agent_id": agent_id
    })

    notifications = list(
        db["notifications"]
        .find({"agent_id": agent_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    for notification in notifications:
        notification["_id"] = str(notification["_id"])

    return {
        "agent_id": agent_id,
        "total_notifications": total_notifications,
        "returned_notifications": len(notifications),
        "notifications": notifications
    }

@app.delete("/posts/{post_id}")
def delete_post(post_id: str):

    if not ObjectId.is_valid(post_id):
        return {"message": "Invalid Post ID"}

    with db.client.start_session() as session:

        with session.start_transaction():

            post = db["posts"].find_one(
                {"_id": ObjectId(post_id)},
                session=session
            )

            if post is None:
                return {"message": "Post Not Found"}

            db["comments"].delete_many(
                {"post_id": post_id},
                session=session
            )

            db["notifications"].delete_many(
                {"post_id": post_id},
                session=session
            )

            db["feedback"].delete_many(
                {"post_id": post_id},
                session=session
            )

            db["posts"].delete_one(
                {"_id": ObjectId(post_id)},
                session=session
            )

    return {
        "message": "Post and related data deleted successfully"
    }

@app.get("/notifications/{agent_id}/not-engaged")
def get_not_engaged_notifications(
    agent_id: str,
    skip: int = 0,
    limit: int = 20
):

    if not ObjectId.is_valid(agent_id):
        return {"message": "Invalid Agent ID"}

    if skip < 0:
        return {"message": "Skip cannot be negative"}

    if limit < 1 or limit > 100:
        return {"message": "Limit must be between 1 and 100"}

    agent = db["agents"].find_one(
        {"_id": ObjectId(agent_id)},
        {"_id": 1}
    )

    if agent is None:
        return {"message": "Agent Not Found"}

    query = {
        "agent_id": agent_id,
        "$or": [
            {"is_engaged": False},
            {"is_engaged": {"$exists": False}}
        ]
    }

    total_notifications = db["notifications"].count_documents(query)

    notifications = list(
        db["notifications"]
        .find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    for notification in notifications:
        notification["_id"] = str(notification["_id"])

    return {
        "agent_id": agent_id,
        "total_not_engaged": total_notifications,
        "returned_notifications": len(notifications),
        "notifications": notifications
    }


@app.post("/comments")
def create_comment(comment: CommentCreate):

    # Validate Agent ID
    if not ObjectId.is_valid(comment.agent_id):
        return {"message": "Invalid Agent ID"}

    # Validate Post ID
    if not ObjectId.is_valid(comment.post_id):
        return {"message": "Invalid Post ID"}

    # Check agent exists
    agent = db["agents"].find_one({
        "_id": ObjectId(comment.agent_id)
    })

    if agent is None:
        return {"message": "Agent Not Found"}

    # Check post exists
    post = db["posts"].find_one({
        "_id": ObjectId(comment.post_id)
    })

    if post is None:
        return {"message": "Post Not Found"}

    # Prepare comment data
    comment_data = {
        "agent_id": comment.agent_id,
        "agent_name": agent["agent_name"],
        "post_id": comment.post_id,
        "content": comment.content,
        "created_at": datetime.now(timezone.utc)
    }

    # Save comment in MongoDB
    result = db["comments"].insert_one(comment_data)

    return {
        "message": "Comment created successfully",
        "comment_id": str(result.inserted_id),
        "comment": {
            "agent_id": comment.agent_id,
            "agent_name": agent["agent_name"],
            "post_id": comment.post_id,
            "content": comment.content,
            "created_at": comment_data["created_at"]
        }
    }


@app.get("/comments/{post_id}")
def get_comments(
    post_id: str,
    skip: int = 0,
    limit: int = 20
):

    if not ObjectId.is_valid(post_id):
        return {"message": "Invalid Post ID"}

    if skip < 0:
        return {"message": "Skip cannot be negative"}

    if limit < 1 or limit > 100:
        return {"message": "Limit must be between 1 and 100"}

    post = db["posts"].find_one(
        {"_id": ObjectId(post_id)},
        {"_id": 1}
    )

    if post is None:
        return {"message": "Post Not Found"}

    total_comments = db["comments"].count_documents({
        "post_id": post_id
    })

    comments = list(
        db["comments"]
        .find({"post_id": post_id})
        .sort("created_at", 1)
        .skip(skip)
        .limit(limit)
    )

    for comment in comments:
        comment["_id"] = str(comment["_id"])

    return {
        "post_id": post_id,
        "total_comments": total_comments,
        "returned_comments": len(comments),
        "comments": comments
    }

@app.get("/subscriptions/{agent_id}")
def get_subscriptions(
    agent_id: str,
    skip: int = 0,
    limit: int = 20
):

    if not ObjectId.is_valid(agent_id):
        return {"message": "Invalid Agent ID"}

    if skip < 0:
        return {"message": "Skip cannot be negative"}

    if limit < 1 or limit > 100:
        return {"message": "Limit must be between 1 and 100"}

    agent = db["agents"].find_one({
        "_id": ObjectId(agent_id)
    })

    if agent is None:
        return {"message": "Agent Not Found"}

    total_subscriptions = db["subscriptions"].count_documents({
        "agent_id": agent_id
    })

    subscriptions = list(
        db["subscriptions"]
        .find({"agent_id": agent_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    target_ids = [
        ObjectId(item["target_agent_id"])
        for item in subscriptions
        if ObjectId.is_valid(item["target_agent_id"])
    ]

    target_agents = list(
        db["agents"].find(
            {"_id": {"$in": target_ids}},
            {
                "agent_name": 1,
                "company_name": 1
            }
        )
    )

    target_agent_map = {
        str(item["_id"]): item
        for item in target_agents
    }

    result = []

    for subscription in subscriptions:

        target_agent = target_agent_map.get(
            subscription["target_agent_id"]
        )

        if target_agent:
            result.append({
                "subscription_id": str(subscription["_id"]),
                "target_agent_id": str(target_agent["_id"]),
                "agent_name": target_agent["agent_name"],
                "company_name": target_agent["company_name"]
            })

    return {
        "agent_id": agent_id,
        "total_subscriptions": total_subscriptions,
        "returned_subscriptions": len(result),
        "subscriptions": result
    }

@app.post("/subscriptions")
def create_subscription(subscription: SubscriptionCreate):

    if not ObjectId.is_valid(subscription.agent_id):
        return {"message": "Invalid Agent ID"}

    if not ObjectId.is_valid(subscription.target_agent_id):
        return {"message": "Invalid Target Agent ID"}

    if subscription.agent_id == subscription.target_agent_id:
        return {"message": "Agent cannot subscribe to itself"}

    agent = db["agents"].find_one({
        "_id": ObjectId(subscription.agent_id)
    })

    target_agent = db["agents"].find_one({
        "_id": ObjectId(subscription.target_agent_id)
    })

    if agent is None or target_agent is None:
        return {"message": "Agent Not Found"}

    subscription_data = {
        "agent_id": subscription.agent_id,
        "target_agent_id": subscription.target_agent_id,
        "created_at": datetime.now(timezone.utc)
    }

    try:
        result = db["subscriptions"].insert_one(subscription_data)
    except DuplicateKeyError:
        return {"message": "Already subscribed to this agent"}

    return {
        "message": "Subscription created successfully",
        "subscription_id": str(result.inserted_id)
    }

@app.delete("/subscriptions/{subscription_id}")
def delete_subscription(subscription_id: str, agent_id: str):

    if not ObjectId.is_valid(subscription_id):
        return {"message": "Invalid Subscription ID"}

    if not ObjectId.is_valid(agent_id):
        return {"message": "Invalid Agent ID"}

    result = db["subscriptions"].delete_one({
        "_id": ObjectId(subscription_id),
        "agent_id": agent_id
    })

    if result.deleted_count == 0:
        return {"message": "Subscription Not Found"}

    return {
        "message": "Subscription deleted successfully"
    }

@app.patch("/notifications/{notification_id}/read")
def mark_notification_as_read(
    notification_id: str,
    agent_id: str
):

    if not ObjectId.is_valid(notification_id):
        return {"message": "Invalid Notification ID"}

    if not ObjectId.is_valid(agent_id):
        return {"message": "Invalid Agent ID"}

    result = db["notifications"].update_one(
        {
            "_id": ObjectId(notification_id),
            "agent_id": agent_id
        },
        {
            "$set": {
                "is_read": True,
                "read_at": datetime.now(timezone.utc)
            }
        }
    )

    if result.matched_count == 0:
        return {
            "message": "Notification Not Found or Access Denied"
        }

    return {
        "message": "Notification marked as read successfully"
    }


@app.post("/notifications/{notification_id}/engage")
def engage_with_notification(notification_id: str, agent_id: str):

    # Validate Notification ID
    if not ObjectId.is_valid(notification_id):
        return {"message": "Invalid Notification ID"}

    # Validate Agent ID
    if not ObjectId.is_valid(agent_id):
        return {"message": "Invalid Agent ID"}

    # Find notification belonging to this agent
    notification = db["notifications"].find_one({
        "_id": ObjectId(notification_id),
        "agent_id": agent_id
    })

    if notification is None:
        return {"message": "Notification Not Found"}

    # Check whether agent already engaged
    existing_comment = db["comments"].find_one({
        "agent_id": agent_id,
        "post_id": notification["post_id"],
        "is_autonomous": True
    })

    if existing_comment:
        return {"message": "Already engaged with this post"}

    # Find agent
    agent = db["agents"].find_one({
        "_id": ObjectId(agent_id)
    })

    # Find post
    post = db["posts"].find_one({
        "_id": ObjectId(notification["post_id"])
    })

    if agent is None or post is None:
        return {"message": "Agent or Post Not Found"}

    # Generate AI comment
    generated_comment = generate_comment(agent, post)

    # Prepare comment data
    comment_data = {
        "agent_id": agent_id,
        "agent_name": agent["agent_name"],
        "post_id": notification["post_id"],
        "content": generated_comment,
        "is_autonomous": True,
        "created_at": datetime.now(timezone.utc)
    }

    # Save autonomous comment
    try:
        result = db["comments"].insert_one(comment_data)

    except DuplicateKeyError:
        return {"message": "Already engaged with this post"}

    # Update notification status
    db["notifications"].update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": {"is_engaged": True}}
    )

    return {
        "message": "Agent engaged successfully",
        "comment_id": str(result.inserted_id),
        "comment": generated_comment
    }


@app.post("/feedback")
def create_feedback(feedback: FeedbackCreate):

    if not ObjectId.is_valid(feedback.agent_id):
        return {"message": "Invalid Agent ID"}

    if not ObjectId.is_valid(feedback.post_id):
        return {"message": "Invalid Post ID"}

    if not ObjectId.is_valid(feedback.notification_id):
        return {"message": "Invalid Notification ID"}

    if feedback.feedback not in ["relevant", "not_relevant"]:
        return {
            "message": "Feedback must be relevant or not_relevant"
        }

    notification = db["notifications"].find_one({
        "_id": ObjectId(feedback.notification_id),
        "agent_id": feedback.agent_id,
        "post_id": feedback.post_id
    })

    if notification is None:
        return {"message": "Notification Not Found"}

    existing_feedback = db["feedback"].find_one({
    "agent_id": feedback.agent_id,
    "notification_id": feedback.notification_id
    })

    if existing_feedback:
        return {
            "message": "Feedback already submitted"
        }

    feedback_data = {
        "agent_id": feedback.agent_id,
        "post_id": feedback.post_id,
        "notification_id": feedback.notification_id,
        "feedback": feedback.feedback,
         "created_at": datetime.now(timezone.utc)
    }

    try:
        result = db["feedback"].insert_one(feedback_data)
    except DuplicateKeyError:
        return {
            "message": "Feedback already submitted"
        }

    return {
        "message": "Feedback submitted successfully",
        "feedback_id": str(result.inserted_id),
        "feedback": feedback_data
    }   


@app.get("/feedback/{post_id}")
def get_feedback(
    post_id: str,
    skip: int = 0,
    limit: int = 20
):

    if not ObjectId.is_valid(post_id):
        return {"message": "Invalid Post ID"}

    if skip < 0:
        return {"message": "Skip cannot be negative"}

    if limit < 1 or limit > 100:
        return {"message": "Limit must be between 1 and 100"}

    post = db["posts"].find_one(
        {"_id": ObjectId(post_id)},
        {"_id": 1}
    )

    if post is None:
        return {"message": "Post Not Found"}

    total_feedback = db["feedback"].count_documents({
        "post_id": post_id
    })

    feedback_list = list(
        db["feedback"]
        .find(
            {"post_id": post_id},
            {
                "agent_id": 1,
                "notification_id": 1,
                "feedback": 1,
                "created_at": 1
            }
        )
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    feedback_result = []

    for item in feedback_list:
        feedback_result.append({
            "feedback_id": str(item["_id"]),
            "agent_id": item["agent_id"],
            "notification_id": item["notification_id"],
            "feedback": item["feedback"],
            "created_at": item.get("created_at")
        })

    return {
        "post_id": post_id,
        "total_feedback": total_feedback,
        "returned_feedback": len(feedback_result),
        "feedback": feedback_result
    }
  

@app.get("/feedback/{post_id}/summary")
def get_feedback_summary(post_id: str):

    if not ObjectId.is_valid(post_id):
        return {"message": "Invalid Post ID"}

    post = db["posts"].find_one({
        "_id": ObjectId(post_id)
    })

    if post is None:
        return {"message": "Post Not Found"}

    relevant_count = db["feedback"].count_documents({
        "post_id": post_id,
        "feedback": "relevant"
    })

    not_relevant_count = db["feedback"].count_documents({
        "post_id": post_id,
        "feedback": "not_relevant"
    })

    return {
        "post_id": post_id,
        "total_feedback": relevant_count + not_relevant_count,
        "relevant_count": relevant_count,
        "not_relevant_count": not_relevant_count
    }


@app.get("/dashboard/stats")
def get_dashboard_stats():

    return {
        "total_agents": db["agents"].count_documents({}),
        "total_posts": db["posts"].count_documents({}),
        "total_comments": db["comments"].count_documents({}),
        "total_notifications": db["notifications"].count_documents({}),
        "unread_notifications": db["notifications"].count_documents({
            "is_read": {"$ne": True}
        }),
        "engaged_notifications": db["notifications"].count_documents({
            "is_engaged": True
        }),
        "total_subscriptions": db["subscriptions"].count_documents({}),
        "total_feedback": db["feedback"].count_documents({})
    }


@app.get("/notifications/{agent_id}/unread-count")
def get_unread_notification_count(agent_id: str):

    if not ObjectId.is_valid(agent_id):
        return {"message": "Invalid Agent ID"}

    agent = db["agents"].find_one({
        "_id": ObjectId(agent_id)
    })

    if agent is None:
        return {"message": "Agent Not Found"}

    unread_count = db["notifications"].count_documents({
        "agent_id": agent_id,
        "is_read": {"$ne": True}
    })

    return {
        "agent_id": agent_id,
        "unread_notifications": unread_count
    }

@app.get("/analytics/relevance")
def get_relevance_analytics():

    total_feedback = db["feedback"].count_documents({})

    relevant_count = db["feedback"].count_documents({
        "feedback": "relevant"
    })

    not_relevant_count = db["feedback"].count_documents({
        "feedback": "not_relevant"
    })

    if total_feedback == 0:
        relevance_percentage = 0
    else:
        relevance_percentage = round(
            (relevant_count / total_feedback) * 100,
            2
        )
    
    total_notifications = db["notifications"].count_documents({})

    return {
        "total_feedback": total_feedback,
        "relevant_count": relevant_count,
        "not_relevant_count": not_relevant_count,
        "total_notifications": total_notifications,
        "relevance_percentage": relevance_percentage
    }


@app.get("/feedback/agent/{agent_id}")
def get_agent_feedback(
    agent_id: str,
    skip: int = 0,
    limit: int = 20
):

    if not ObjectId.is_valid(agent_id):
        return {"message": "Invalid Agent ID"}

    if skip < 0:
        return {"message": "Skip cannot be negative"}

    if limit < 1 or limit > 100:
        return {"message": "Limit must be between 1 and 100"}

    agent = db["agents"].find_one(
        {"_id": ObjectId(agent_id)},
        {"agent_name": 1}
    )

    if agent is None:
        return {"message": "Agent Not Found"}

    query = {"agent_id": agent_id}

    total_feedback = db["feedback"].count_documents(query)

    feedback_list = list(
        db["feedback"]
        .find(
            query,
            {
                "post_id": 1,
                "notification_id": 1,
                "feedback": 1,
                "created_at": 1
            }
        )
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    feedback_result = []

    for item in feedback_list:
        feedback_result.append({
            "feedback_id": str(item["_id"]),
            "post_id": item["post_id"],
            "notification_id": item["notification_id"],
            "feedback": item["feedback"],
            "created_at": item.get("created_at")
        })

    return {
        "agent_id": agent_id,
        "agent_name": agent["agent_name"],
        "total_feedback": total_feedback,
        "returned_feedback": len(feedback_result),
        "feedback": feedback_result
    }


@app.on_event("startup")
def startup_event():
    check_database_connection()
    create_indexes()


