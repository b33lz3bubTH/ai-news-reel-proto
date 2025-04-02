from sqlalchemy import Column, Integer, String, JSON, UniqueConstraint, Boolean, DateTime, ForeignKey, event
from sqlalchemy.dialects.postgresql import UUID
from src.datasource.sqlalchemy.model_base import BaseModel


class PostQueueStages:
    processing = "processing"
    completed = "completed"
    failed = "failed"


class PostProcessingStatusStages:
    success = "success"
    failed = "failed"
    error = "error"


class Posts(BaseModel):
    __tablename__ = "posts"
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    post_id = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    extras = Column(JSON)

    __table_args__ = (UniqueConstraint('tenant_id',
                                       'platform',
                                       'post_id',
                                       name='tenant_post_platform_uc'), )


class PostQueue(BaseModel):
    __tablename__ = "post_queue"

    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(String, nullable=False, default=PostQueueStages.processing)
    post_data = Column(JSON, nullable=True)

    __table_args__ = (UniqueConstraint('tenant_id',
                                       'id',
                                       name='tenant_postqueue_uc'), )


class PostProcessingLogs(BaseModel):
    __tablename__ = "post_processing_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_queue_id = Column(UUID(as_uuid=True),
                           ForeignKey("post_queue.id"),
                           nullable=False)
    status = Column(String, nullable=False)  # processing, completed, or error
    message = Column(String,
                     nullable=True)  # Store error messages or success details

@event.listens_for(PostQueue, 'after_insert')
def queue_processing_listner(mapper, connection, target):
    print(f"Inserted in PostQueue {target.id}: ", target)



"""
To handle this case efficiently, where you need to return an ID immediately upon receiving the data and then process the post asynchronously in the background, the flow would look like this:

---

### **Flow Design:**

1. **Step 1: Receive the Request & Create an Entry in `PostQueue` (Asynchronously)**
   - When `{platform: "twitter", "text": "hello"}` arrives, immediately create an entry in the `PostQueue` table with:
     - `status = "processing"`
     - `post_data = {"platform": "twitter", "text": "hello"}`
     - A **UUID** `id` is generated automatically (or by your backend).
   - **Return this `UUID` to the user immediately** as a response to the request.
     Example returned response:
     ```json
     {
       "queue_id": "abc12345-queue-id",  # UUID
       "status": "processing"
     }
     ```
   - This ensures the user doesn't have to wait for the post to be completed.

---

2. **Step 2: Background Processing (Asynchronous Worker Service)**
   - In the background, an asynchronous worker picks up entries from the `PostQueue` table with `status = "processing"`.

3. **Step 3: Posting to External Service**
   - The worker sends the `post_data` to the external service.
   - The external service returns `{platform: "twitter", "post_id": "xyz7890"}`.

---

4. **Step 4: Insert into `Posts` Table & Update `PostQueue` Table**
   - Insert the processed post into the `Posts` table:
     ```json
     {
       "tenant_id": "1234-abcd-tenant-id",
       "platform": "twitter",
       "post_id": "xyz7890",
       "extras": {"text": "hello"}
     }
     ```
   - Update the corresponding `PostQueue` entry:
     - Set `status = "completed"`.

---

5. **Step 5: Log the Processing Result (Optional)**
   - Insert a success message into the `PostProcessingLogs` table:
     ```json
     {
       "post_queue_id": "abc12345-queue-id",
       "status": "success",
       "message": "Post processed successfully."
     }
     ```

---

### **Sample Code for Fast Return with Background Processing:**

```python
import uuid
from sqlalchemy.orm import Session
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

# Endpoint to handle post creation request
@app.post("/create-post/")
def create_post(data: dict, background_tasks: BackgroundTasks, db: Session):
    # Generate a unique queue ID
    queue_id = str(uuid.uuid4())

    # Insert the post into `PostQueue` table
    post_queue_entry = {
        "id": queue_id,
        "tenant_id": "1234-abcd-tenant-id",
        "status": "processing",
        "post_data": data  # Save the raw incoming post data
    }
    db.add(PostQueue(**post_queue_entry))
    db.commit()

    # Add the processing task to be done in the background
    background_tasks.add_task(process_post, queue_id, data)

    # Return queue ID immediately to the user
    return {"queue_id": queue_id, "status": "processing"}


def process_post(queue_id: str, data: dict):
    # Background worker task to handle post processing
    external_response = send_to_external_post_service(data)  # {platform: "twitter", post_id: "xyz7890"}

    # Insert processed post into `Posts` table and update the queue
    db_post_entry = {
        "tenant_id": "1234-abcd-tenant-id",
        "platform": external_response["platform"],
        "post_id": external_response["post_id"],
        "extras": data
    }
    db.add(Posts(**db_post_entry))
    db.query(PostQueue).filter(PostQueue.id == queue_id).update({"status": "completed"})
    db.commit()

    # Log the result (optional)
    db.add(PostProcessingLogs(post_queue_id=queue_id, status="success", message="Post processed successfully."))
    db.commit()
```

---

### **Expected Flow (With Timing)**

1. **User Request (Immediate Response)**:
   - User sends `{platform: "twitter", "text": "hello"}`.
   - The server immediately inserts the data into `PostQueue` and returns:
     ```json
     {
       "queue_id": "abc12345-queue-id",
       "status": "processing"
     }
     ```

2. **Background Processing (Worker/Asynchronous Task)**:
   - The worker picks up the `post_data` from `PostQueue`.
   - Sends the data to the external posting service and gets back `{platform: "twitter", post_id: "xyz7890"}`.
   - Inserts the processed post into the `Posts` table and updates the `PostQueue` status to `"completed"`.

---

### **Final Database State Example:**

#### `PostQueue` Table (Updated After Completion):
| id                      | tenant_id            | status     | post_data                          |
|-------------------------|----------------------|------------|------------------------------------|
| abc12345-queue-id        | 1234-abcd-tenant-id  | completed  | {"platform": "twitter", "text": "hello"} |

#### `Posts` Table:
| tenant_id               | platform | post_id   | extras                         |
|-------------------------|----------|-----------|-------------------------------|
| 1234-abcd-tenant-id      | twitter  | xyz7890   | {"text": "hello"}              |

#### `PostProcessingLogs` Table:
| id  | post_queue_id       | status   | message                              |
|-----|---------------------|----------|--------------------------------------|
| 1   | abc12345-queue-id   | success  | "Post processed successfully."       |

---

### **Advantages of This Approach:**
- **Fast User Response:** Users get the queue ID instantly.
- **Background Processing:** Heavy tasks are moved to a background worker to avoid blocking the main server.
- **Trackable Status:** Users can later query the `PostQueue` table using `queue_id` to check the status (`processing`, `completed`, or `failed`).

This flow ensures optimal user experience by minimizing waiting time while still keeping the post-processing trackable and reliable.

"""
