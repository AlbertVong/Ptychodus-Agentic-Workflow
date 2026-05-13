from __future__ import annotations

import logging
from typing import Any

from agentic_blueprint_catalog.observability.monitored_agent import MonitoredAgent
from agentic_blueprint_catalog.observability.user_agent import UserAgent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from academy.agent import action
from academy.handle import Handle

prompt = """You are an expert in ptychography and coherent diffractive imaging (CDI).
Evaluate the quality of the reconstructed ptychographic image provided.

## Image Metadata
{image_metadata}

## Evaluation Criteria
Assess the image on each of the following dimensions and give a score from 1-5 with a brief justification:

1. **Spatial Resolution** — Are fine structural features sharp and well-resolved? Look for edge sharpness and absence of blurring.
2. **Phase Contrast Quality** — Is the phase channel (if present) smooth, artefact-free, and physically interpretable?
3. **Noise & Artefacts** — Are there ringing artefacts, Gibbs phenomena, probe artefacts, or reconstruction ghosts?
4. **Probe Consistency** — Does the amplitude/phase suggest a well-converged, physically reasonable probe?
5. **Background Uniformity** — Is the vacuum/background region flat and free of fringes or drift streaks?
6. **Convergence Indicators** — Based on visual appearance, does the reconstruction appear well-converged or under-iterated?

## Output Format
Return your evaluation as:

### Scores
| Criterion | Score (1-5) | Justification |
|---|---|---|
| Spatial Resolution | | |
| Phase Contrast Quality | | |
| Noise & Artefacts | | |
| Probe Consistency | | |
| Background Uniformity | | |
| Convergence Indicators | | |

### Overall Quality Score: X/5

### Summary
A 2-3 sentence overall assessment.

### Recommendations
Suggest specific reconstruction parameter adjustments or data collection improvements if quality is lacking.
"""


class Validator(MonitoredAgent):
    """Validates ptychographic reconstruction quality using a vision model."""

    def __init__(
        self,
        user_agent_handle: Handle[UserAgent],
        openai_ai_model: str,
        openai_api_key: str,
        openai_base_url: str,
    ) -> None:
        super().__init__(user_agent_handle=user_agent_handle)
        self._metadata: dict[int, str] = {}
        self.model = ChatOpenAI(
            model=openai_ai_model,
            api_key=openai_api_key,
            base_url=openai_base_url,
        )
        logging.warning(f'Starting validator pointed at {openai_base_url}')

    @action
    async def update_metadata(
        self,
        experiment_id: int,
        experiment_metadata: str,
    ) -> None:
        """Update metadata info for the experiment."""
        self._metadata[experiment_id] = experiment_metadata

    @action
    async def validate_image(
        self,
        experiment_id: int,
        b64_image: str,
    ) -> dict[Any, Any]:
        """Validate the image using an image model.

        :param experiment_id: Experiment ID
        :param b64_image: base64 encoded image data str
        """
        additional_info = self._metadata[experiment_id]
        response = self.model.invoke(
            [
                HumanMessage(
                    content=[
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:image/jpeg;base64,{b64_image}',
                            },
                        },
                        {
                            'type': 'text',
                            'text': prompt.format(image_metadata=additional_info),
                        },
                    ],
                ),
            ],
        )
        return {'result': response.content}
