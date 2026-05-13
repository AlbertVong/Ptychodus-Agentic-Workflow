from __future__ import annotations

import asyncio
import os
import pickle
from concurrent.futures import ThreadPoolExecutor

from dotenv import find_dotenv
from dotenv import load_dotenv

from academy.exchange.cloud import HttpExchangeFactory
from academy.logging import init_logging
from academy.manager import Manager
from agentic_ptychodotus.agents.orchestrator import Orchestrator
from agentic_ptychodotus.agents.orchestrator import Reconstructor
from agentic_ptychodotus.agents.validator import Validator

load_dotenv(find_dotenv('.env'))


async def main() -> None:
    """Launch agents."""
    init_logging()

    async with await Manager.from_exchange_factory(
        factory=HttpExchangeFactory(),
        # executors=ProcessPoolExecutor(max_workers=8),
        executors=ThreadPoolExecutor(max_workers=4),
    ) as manager:
        with open('user_agent_handle.pkl', 'rb') as f:
            user_agent_id = pickle.load(f)
            user_agent_handle = manager.get_handle(user_agent_id)

        validator_handle = await manager.launch(
            Validator,
            kwargs={
                'user_agent_handle': user_agent_handle,
                'openai_ai_model': os.environ['OPENAI_API_MODEL'],
                'openai_api_key': os.environ['OPENAI_API_KEY'],
                'openai_base_url': os.environ['OPENAI_API_BASE_URL'],
            },
        )

        reconstructor_handles = [
            await manager.launch(Reconstructor, kwargs={'user_agent_handle': user_agent_handle}),
            await manager.launch(Reconstructor, kwargs={'user_agent_handle': user_agent_handle}),
        ]

        orchestrator_handle = await manager.launch(
            Orchestrator,
            kwargs={
                'user_agent_handle': user_agent_handle,
                'reconstructor_handles': reconstructor_handles,
                'validator_handle': validator_handle,
            },
        )

        # Trigger a flow
        await orchestrator_handle.reconstruct(metadata='Some bogus metadata', data_product=b'VERY BIG BYTES')
        await manager.wait([orchestrator_handle], raise_error=True)


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
