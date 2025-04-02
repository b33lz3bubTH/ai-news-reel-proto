"""
ndtv latest news > loop each > fetch news > generate video > upload to youtube short
curl -X 'POST' \
  'http://127.0.0.1:8081/tenants/{{tenant_id: str}}/socials/post?tenant_id=227f461f-a20c-4e93-8871-931196dd8f4e' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "post_body": "News Testing",
  "medias": [
    "/tmp/b61e8720-6648-4fed-aa2c-f0ed3bdc104b_reel.mp4"
  ],
  "platform": "youtube"
}
'
"""
import re
import sys
import os
import asyncio
import requests
import time
import json
from pathlib import Path
from threading import Thread
from fastapi import Depends
from concurrent.futures import ThreadPoolExecutor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.utils.news_trackers import NewsTrackerService
from src.core.genai.text_summarize import Summarizer
from src.core.genai.tts_piper import PiperTextToSpeech
from src.core.genai.atv_ffmpeg import VideoGenerator

from src.plugins.scrapers.sites.ndtv import NdtvLatestScraper, NdtvNewsScraper, NdtvSportsScraper
from src.plugins.pipeline_xcavator import BaseTask, Pipeline as PipelineManager
from src.datasource.sqlite import get_db_v2 as get_db
from src.datasource.sqlalchemy.model_base import create_tables


class NewsScrapperTask(BaseTask):

    def __init__(self, name: str, url: str):
        super().__init__(name)
        self.url = url

    async def run(self, xcom: dict[str, any]) -> any:
        print("ndtv news scrapper task: ", self.name)
        service = NdtvNewsScraper()
        if "sports.ndtv" in self.url:
            service = NdtvSportsScraper()

        article = service.run(self.url)
        xcom["article"] = article
        xcom["url"] = self.url
        xcom["tags"] = xcom.get("tags", ["#news"])

        if "sports.ndtv" in self.url:
            xcom["tags"].append("#sports")


class TextSummarization(BaseTask):

    async def run(self, xcom: dict[str, any]) -> any:
        print("text-summarize task: ", self.name)
        service = Summarizer(6)
        article = xcom.get("article", {}).get("article_text", "")
        text = ' '.join(article) if isinstance(article, list) else article
        summary = service.generate(text)
        xcom["article_summarized"] = summary


class AudioGen(BaseTask):

    async def run(self, xcom: dict[str, any]) -> any:
        print("Audio upload task: ", self.name)
        service = PiperTextToSpeech()
        summary = xcom.get("article_summarized")
        if summary and len(summary) > 150:
            audio = service.generate(summary)
            xcom["audio"] = audio
        else:
            print(f"{self.name} has low summery, skipping")


class VideoGen(BaseTask):

    async def run(self, xcom: dict) -> any:
        print("Video upload task: ", self.name)
        media = xcom.get("article").get("media")
        service = VideoGenerator(image_path=media, reel=True)
        audio = xcom.get("audio")

        video_path = service.generate(audio)
        xcom["video"] = video_path


class YouTubeUploadTask(BaseTask):

    def __init__(self, name: str, tenant_id: str, on_complete: any):
        super().__init__(name)
        self.tenant_id = tenant_id
        self.on_complete = on_complete

    async def _upload_video(self, url: str, payload: dict,
                            headers: dict) -> None:
        """Helper method to perform the upload in a separate thread."""
        try:
            response = requests.post(url,
                                     json=payload,
                                     headers=headers,
                                     timeout=10)  # Set a timeout
            if response.status_code == 200:
                print(
                    f"{self.name}: Successfully uploaded video. Response: {response.json()}"
                )
            else:
                print(
                    f"{self.name}: Upload failed with status {response.status_code}"
                )

        except Exception as e:
            print(
                f"{self.name}: Upload encountered an error: {e} (continuing anyway)"
            )

    async def run(self, xcom: dict):
        print("Youtube upload task: ", self.name)
        video_path = xcom.get("video")
        article = xcom.get("article_summarized")
        article_source = xcom.get(
            "url")  # Assuming the URL is stored in xcom under "url"

        if not video_path:
            print(f"{self.name}: No video found in xcom, skipping upload")
            return

        # Append source and project info to the article summary
        if article and article_source:
            article += f" Story Ref: {article_source}, posting this for echoware.co.in gen ai project. "
            article += ' '.join(xcom.get("tags"))
        else:
            article = "News Testing"  # Fallback if article or source is missing

        url = f"http://127.0.0.1:8081/tenants/socials/post?tenant_id={self.tenant_id}"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "post_body": article,
            "medias": [video_path],
            "platform": "youtube"
        }

        # Fire and forget: Run the upload in a separate thread
        await self._upload_video(url, payload, headers)
        if self.on_complete:
            self.on_complete()

        print(f"{self.name}: Upload initiated in background thread")


"""
if __name__ == "__main__":
    tenant_id = "227f461f-a20c-4e93-8871-931196dd8f4e"
    latest_news = NdtvLatestScraper().run("https://www.ndtv.com/latest#pfrom=home-ndtv_mainnavigation")

    pipeline_managers = []

    for latest_article in latest_news[:5]:
        print("news: ", latest_article.get("title"))
        h_manager = PipelineManager()
        if latest_article.get("link"):
            h_manager.add_task(NewsScrapperTask(latest_article.get("title"), latest_article.get("link")))
            h_manager.add_task(TextSummarization(latest_article.get("title")))
            h_manager.add_task(AudioGen(latest_article.get("title")))
            h_manager.add_task(VideoGen(latest_article.get("title")))
            h_manager.add_task(YouTubeUploadTask(latest_article.get("title"), tenant_id=tenant_id))

        pipeline_managers.append(h_manager)

    async def run_managers(managers: list[any]):
        tasks = [manager.run() for manager in managers]
        await asyncio.gather(*tasks)

    asyncio.run(run_managers(pipeline_managers))
"""


def on_complete(tenant_id: str, url: str):
    db = next(get_db())
    news_tracker_service = NewsTrackerService(db=db)
    data = news_tracker_service._prepare(tenant_id, url)
    news_tracker_service.create(data)

class NewsProcessor:
    def __init__(self, tenant_id: str, batch_size: int = 20, fetch_interval: int = 980, max_concurrent: int = 2):
        self.tenant_id = tenant_id
        self.batch_size = batch_size
        self.fetch_interval = fetch_interval
        self.max_concurrent = max_concurrent  # Limit to 2 concurrent tasks
        self.pipeline_managers: list[PipelineManager] = []
        self.last_fetch_time = 0
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.running = True

    async def fetch_and_queue_articles(self):
        """Fetch articles and queue only unprocessed ones."""
        if time.time() - self.last_fetch_time < self.fetch_interval and self.pipeline_managers:
            print(f"Skipping fetch: Last fetch was {(time.time() - self.last_fetch_time):.0f}s ago")
            return

        print("Fetching latest news...")
        latest_news = NdtvLatestScraper().run("https://www.ndtv.com/latest#pfrom=home-ndtv_mainnavigation")
        for article in latest_news:
            link = article.get("link")
            if not link:
                continue

            news_tracker_service = NewsTrackerService(db=next(get_db()))
            # Check if already processed once per fetch cycle
            if news_tracker_service.find_record(self.tenant_id, link):
                print("already processed; ", link)
                continue  # Skip silently without repeated messages

            print(f"Queueing new article: {article['title']}")
            h_manager = PipelineManager()
            h_manager.add_task(NewsScrapperTask(article["title"], link))
            h_manager.add_task(TextSummarization(article["title"]))
            h_manager.add_task(AudioGen(article["title"]))
            h_manager.add_task(VideoGen(article["title"]))
            h_manager.add_task(
                YouTubeUploadTask(
                    article["title"],
                    tenant_id=self.tenant_id,
                    on_complete=lambda t=self.tenant_id, u=link: on_complete(t, u)
                )
            )
            self.pipeline_managers.append(h_manager)

        self.last_fetch_time = time.time()

    def run_pipeline_sequentially(self, pipeline: PipelineManager) -> None:
        """Run a single pipeline synchronously in a thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(pipeline.run())
            print(f"Completed pipeline for {pipeline.tasks[0].name}")
        except Exception as e:
            print(f"Error in pipeline {pipeline.tasks[0].name}: {e}")
        finally:
            loop.close()

    async def process_articles(self):
        """Process queued articles with controlled concurrency."""
        while self.pipeline_managers and self.running:
            # Take a batch up to batch_size
            batch = self.pipeline_managers[:self.batch_size]
            del self.pipeline_managers[:self.batch_size]

            # Submit tasks to executor, respecting max_concurrent
            futures = []
            for manager in batch:
                future = self.executor.submit(self.run_pipeline_sequentially, manager)
                futures.append(future)

            # Wait for all tasks in the batch to complete
            for future in futures:
                future.result()  # Blocks until the task is done

            print(f"Processed batch of {len(batch)} articles")

    async def run(self):
        """Main loop with fetch-process-wait cycle."""
        while self.running:
            await self.fetch_and_queue_articles()

            if self.pipeline_managers:
                await self.process_articles()
            else:
                print("No new articles to process")

            for i in range(self.fetch_interval, -1, -1):
                sys.stdout.write(f"\rWaiting {i}s before next fetch...")  # \r rewrites the current line
                sys.stdout.flush()  # Forces immediate display
                await asyncio.sleep(1)  # Async sleep for 1 second
            print()  # Move to a new line after countdown finishes

    def shutdown(self):
        """Gracefully shut down the processor."""
        self.running = False
        self.executor.shutdown(wait=True)
        print("Shutdown complete")


if __name__ == "__main__":
    create_tables()
    tenant_id = "35e1f3aa-1c51-40cb-acb9-88f604078fd7"
    news_processor = NewsProcessor(tenant_id)
    try:
        asyncio.run(news_processor.run())
    except KeyboardInterrupt:
        print("Shutting down...")
        news_processor.shutdown()
            # Wait briefly between batches
