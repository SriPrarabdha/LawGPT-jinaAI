import asyncio
import os
from typing import Dict

import aiohttp
from pydantic import BaseModel, ValidationError

os.environ["OPENAI_API_KEY"] = "your key"
class Response(BaseModel):
    result: str
    error: str
    stdout: str


class HumanPrompt(BaseModel):
    prompt: str



async def hitl_client(url: str, name: str, question: str, envs: Dict = {}):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(f'{url}/{name}') as ws:
            print(f'Connected to {url}/{name}.')

            await ws.send_json(
                {
                    "question": question,
                    "envs": envs if envs else {},
                }
            )

            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close cmd':
                        await ws.close()
                        break
                    else:
                        try:
                            response = Response.parse_raw(msg.data)
                            print(response.result, end='')
                        except ValidationError:
                            try:
                                prompt = HumanPrompt.parse_raw(msg.data)
                                answer = input(prompt.prompt + '\n')
                                await ws.send_str(answer)
                            except ValidationError:
                                print(f'Unknown message: {msg.data}')

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print('ws connection closed with exception %s' % ws.exception())
                else:
                    print(msg)


asyncio.run(
    hitl_client(
        url='wss://langchain-810cd8b175.wolf.jina.ai',
        name='get_answers',
        question="tell me about that which i like",
        envs={
            'OPENAI_API_KEY': os.environ['OPENAI_API_KEY'],
        }
    )
)


