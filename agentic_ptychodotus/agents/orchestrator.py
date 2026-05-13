from __future__ import annotations

import logging
import random
from pathlib import Path
from typing import Any
from uuid import UUID
from uuid import uuid4

from agentic_blueprint_catalog.observability.monitored_agent import MonitoredAgent
from agentic_blueprint_catalog.observability.user_agent import UserAgent

from academy.agent import action
from academy.handle import Handle
from agentic_ptychodotus.agents.validator import Validator


class Orchestrator(MonitoredAgent):
    """Orchestrator for running the ptychography pipeline."""

    def __init__(
        self,
        user_agent_handle: Handle[UserAgent],
        reconstructor_handles: list[Handle[Reconstructor]],
        validator_handle: Handle[Validator],
    ) -> None:
        super().__init__(user_agent_handle=user_agent_handle)
        self.reconstructor_handles = reconstructor_handles
        self.validator_handle = validator_handle
        self._active_tasks: dict[UUID, Any] = {}
        logging.info(f'Orchestrator started for {self}')

    @action
    async def reconstruct(self, metadata: str, data_product: bytes) -> str:
        """Reconstruct image with ptychography."""
        data_id = uuid4()
        self._active_tasks[data_id] = {
            'metadata': metadata,
            'data_product': data_product,
        }
        # Trigger sequence
        # slice -> optimize
        logging.info(f'Reconstruct invoked for id:{data_id}')
        data_slice_file = await self.slice(data_id, data_product=data_product)
        logging.info(f'[MOCK] Starting optimizer loop {data_slice_file=}')

        return 'Reconstructed image from data_product'

    @action
    async def slice(self, data_id: UUID, data_product: bytes) -> Path:
        """Slice the image with ptychography."""
        logging.info('[MOCK] Slicing data_product')
        output_path = Path(f'{data_id}.slice.dat')
        with open(output_path, 'wb') as f:
            f.write(data_product)

        logging.info(f'[MOCK] Sliced data_product written to {output_path}')

        return output_path

    @action
    async def optimize(self, data_product_file: Path) -> bytes:
        """Optimization loop.

        todo: This could be done with langgraph or langchain.


        def build_graph() -> StateGraph:
            g = StateGraph(ReconState)

            g.add_node("reconstructor", run_reconstructor)
            g.add_node("validator",     run_validator)
            g.add_node("update_params", update_params)

            g.set_entry_point("reconstructor")
            g.add_edge("reconstructor", "validator")

            g.add_conditional_edges(
            "validator",
            check_quality,
            {"done": END, "update": "update_params"},
            )
            g.add_edge("update_params", "reconstructor")

            return g.compile()
        """
        logging.debug('[MOCK] Optimizing data_product')

        # Call several reconstruction tasks in parallel and wait
        """
        results = await asyncio.gather(*[
            rec_handle.reconstruct_slice(
                data_product_path=data_product_file,
                reconstruct_params={'param': random.randint(1, 5)},
            )
            for rec_handle in self.reconstructor_handles
        ])
        """
        reconstructed_1 = await self.reconstructor_handles[0].reconstruct_slice(
            data_product_path=data_product_file,
            reconstruct_params={'param': random.randint(1, 5)},
        )

        reconstructed_2 = await self.reconstructor_handles[1].reconstruct_slice(
            data_product_path=data_product_file,
            reconstruct_params={'param': random.randint(1, 5)},
        )

        logging.info(f'reconstructed_1 = {reconstructed_1!r}')
        logging.info(f'reconstructed_2 = {reconstructed_2!r}')
        # logger.info(f"[MOCK] Got {len(results)} reconstruction results")
        return b'SOME BYTES'


class Reconstructor(MonitoredAgent):
    """Ptychography reconstruction on a data slice."""

    def __init__(self, user_agent_handle: Handle[UserAgent]) -> None:
        super().__init__(user_agent_handle=user_agent_handle)
        logging.info(f'Reconstructor started for {self}')

    @action
    async def reconstruct_slice(self, data_product_path: Path, reconstruct_params: dict[Any, Any]) -> str:
        """Reconstruct image with ptychography.

        todo: We assume a shared FS between Orchestrator and Reconstructor,
              to simply data product transfers. Fix this maybe with
              ProxyStore

        :param data_product_path: Path to the data product to reconstruct.
        :returns: ???? todo: fix the return type
        """
        # todo: Some reconstruction magic from Albert to fill in here
        logging.info(f'[MOCK]: {self}] Reconstructing data_product {data_product_path}')
        logging.info(f'[MOCK] Got {reconstruct_params=}')
        b64_image = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADklEQVQI12P4z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=='
        return b64_image
