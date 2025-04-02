from typing import Any, Dict, List, Optional


class BaseTask:

    def __init__(self, name: str):
        """Initialize the task with a name."""
        self.name = name

    async def run(self, xcom: Dict[str, Any]) -> Any:
        """Override this method to execute the task. Returns data for next task."""
        raise NotImplementedError

    async def rollback(self, xcom: Dict[str, Any]):
        """Override this method for rollback logic. Optional."""
        pass


class Pipeline:
    def __init__(self):
        """Initialize the pipeline with an empty task list and xcom shared storage."""
        self.tasks: List[BaseTask] = []
        self.xcom = {}  # Shared storage
        self.executed_tasks = []  # Track executed tasks for rollback

    def add_task(self, task: BaseTask):
        """Add a task to the pipeline."""
        self.tasks.append(task)

    async def run(self):
        """Run the pipeline asynchronously, executing tasks sequentially. Rolls back if any task fails."""
        try:
            for task in self.tasks:
                print(f"Running: {task.name}")
                result = await task.run(self.xcom)
                self.xcom[f"{task.name}"] = result  # Store result in xcom
                self.executed_tasks.append(task)  # Track for rollback
        except Exception as e:
            await self.rollback()
            print("e:", e)

    async def rollback(self):
        """Execute rollback for successfully completed tasks in reverse order."""
        while self.executed_tasks:
            task = self.executed_tasks.pop()
            print(f"Rolling back: {task.name}")
            await task.rollback(self.xcom)


# Example Task Implementations
"""

class Task1(BaseTask):

    async def run(self, xcom: Dict[str, Any]) -> Any:
        xcom["task1_data"] = "Processed by Task 1"
        print("Task 1 executed")
        return "Task1_Result"

    async def rollback(self, xcom: Dict[str, Any]):
        print("Rolling back Task 1")


class Task2(BaseTask):

    async def run(self, xcom: Dict[str, Any]) -> Any:
        xcom["task2_data"] = f"Received {xcom.get('task1_data')} from Task 1"
        print("Task 2 executed")
        return "Task2_Result"


class Task3(BaseTask):

    async def run(self, xcom: Dict[str, Any]) -> Any:
        print("Task 3 executed")
        raise ValueError("Simulated error in Task 3")  # Triggers rollback

    async def rollback(self, xcom: Dict[str, Any]):
        print("Rolling back Task 3")

"""
"""
# Running the pipeline
async def main():
    pipeline = Pipeline()
    pipeline.add_task(Task1("Task1"))
    pipeline.add_task(Task2("Task2"))  # No rollback for Task2
    pipeline.add_task(Task3("Task3"))  # This will trigger rollback

    try:
        await pipeline.run()
    except Exception as e:
        print(f"Pipeline failed: {e}")

asyncio.run(main())
"""
