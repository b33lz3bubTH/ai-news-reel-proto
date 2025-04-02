import sys
import os
import asyncio
# Add the parent directory of 'src' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.genai.tts_piper import PiperTextToSpeech
from src.core.genai.atv_ffmpeg import VideoGenerator
from src.core.genai.text_summarize import Summarizer

async def bootstrap():
    service = PiperTextToSpeech()
    #v_service = VideoGenerator(image_path="/tmp/template.jpeg")
    v_service = VideoGenerator(image_path="https://images.unsplash.com/photo-1566895291281-ea63efd4bdbc")
    new_article = """
    Merchant Navy Officer's Body Crushed in Mixer? Postmortem Report Reveals Shocking Details
According to the latest findings of the postmortem report, after murdering the merchant navy officer, his wife and lover may have crushed the body in a mixer.
    Meerut: Days after the bone-chilling murder of a merchant navy officer in UP's Meerut, its postmortem report has made shocking revelations. As per the initial findings of the postmortem report, the accused, Muskan Rastogi and her lover Sahil Shukla, have reportedly crushed the deceased's body parts in a mixer.

Merchant Navy Officer's Body Crushed in Mixer? Shocking Details in Postmortem Report
The preliminary information revealed in the postmortem report of Saurabh Rajput, the Merchant Navy officer killed by his wife and her lover in Meerut, states that the two accused had crushed some pieces of the body in a mixer. Body pieces have also been found in the postmortem and further reports are awaited.
    Meerut Murder: How Did Muskan Rastogi and Sahil Shukla Hide Saurabh Rajput's Body?
According to the latest update, the accused, Muskan Rastogi and her lover Sahil Shukla, after stabbing Saurabh Rajput to death and dismembering his body, had hid it in different places. The torso was placed in the bed box at Muskan's house and the rest of the body parts were taken to Sahil's house where they were hidden in a cement drum.

Merchant Navy Officer Murdered By Wife and Her Lover | What We Know So Far
Meerut Murder That Shocked the Nation: A Merchant Navy officer, Saurabh Rajput, who had returned to UP's Meerut from United Kingdom (UK), was murdered by his wife and her lover, Muskan Rastogi and Sahil Shukla respectively, in his sleep. The wife and her lover first stabbed him to death, cut his body into several pieces and then hid the body parts in a cement drum.

How Was Saurabh Rajput Murdered: The murder was executed after a four-month planning by the Merchant Navy officer's wife, Muskan Rastogi. She had bought two knives ‘to cut chicken’ a few days before the murder and also got sleeping pills prescribed from the doctor, for anxiety. Muskan used the pills to put her husband to sleep and then stabbed him using the knives; her lover then cut the body into pieces.

How Did Muskan Rastogi Avoid Suspicion: After committing the crime and concealing the body, Muskan Rastogi and her lover went to the hills for a holiday but told her neighbours and family, that she has gone with her husband. To make people believe that everything is normal, she carried her husband's phone with her and kept uploading photos and videos from his social media account.

How Was Muskan Rastogi, Sahil Shukla Caught?: According to one report, Muskan Rastogi had to vacate her house and during the process, the labourer was removing the cement drum and found it extremely heavy. The drum got uncovered during the shifting and the labourer smelt something foul; he informed the police and the two were eventually caught.

As per another report, when Muskan and Sahil were on their holiday after the murder, she was out of money and made an attempt to use the cards of her deceased husband that did not work; she then called her family, asking for money and eventually, she was caught. It was her parents who informed the police and have demanded death penalty for their daughter.
    """
    print("article: ", new_article.strip()[:50], len(new_article))
    article = await Summarizer(3).generate(new_article.strip())
    print("summerized: ", article, len(article))
    audio = await service.generate(article)
    print("audio: ", audio)
    video = await v_service.generate(audio)
    print("video: ", video)



if __name__ == "__main__":
    asyncio.run(bootstrap())
