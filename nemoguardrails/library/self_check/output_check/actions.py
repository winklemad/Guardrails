# SPDX-FileCopyrightText: Copyright (c) 2023-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from typing import Optional

from nemoguardrails import RailsConfig
from nemoguardrails.actions import action
from nemoguardrails.actions.llm.utils import llm_call, warn_if_truncated
from nemoguardrails.actions.rail_outcome import RailOutcome
from nemoguardrails.context import llm_call_info_var
from nemoguardrails.llm.taskmanager import LLMTaskManager
from nemoguardrails.llm.types import Task
from nemoguardrails.logging.explain import LLMCallInfo
from nemoguardrails.types import LLMModel

log = logging.getLogger(__name__)


def _self_check_outcome(allowed: bool) -> RailOutcome:
    return RailOutcome.allow() if allowed else RailOutcome.block()


@action(is_system_action=True)
async def self_check_output(
    llm_task_manager: LLMTaskManager,
    context: Optional[dict] = None,
    llm: Optional[LLMModel] = None,
    config: Optional[RailsConfig] = None,
    **kwargs,
) -> RailOutcome:
    """Checks if the output from the bot.

    Prompt the LLM, using the `self_check_output` task prompt, to determine if the output
    from the bot should be allowed or not.

    The LLM call should return "yes" if the output is bad and should be blocked
    (this is consistent with self_check_input_prompt).

    Returns:
        RailOutcome.allow() if the output should be allowed, RailOutcome.block() otherwise.
    """

    _MAX_TOKENS = 1024
    context = context or {}
    bot_response = context.get("bot_message")
    user_input = context.get("user_message")
    bot_thinking = context.get("bot_thinking")

    task = Task.SELF_CHECK_OUTPUT

    if not bot_response:
        return _self_check_outcome(False)

    prompt = llm_task_manager.render_task_prompt(
        task=task,
        context={
            "user_input": user_input,
            "bot_response": bot_response,
            "bot_thinking": bot_thinking,
        },
    )
    stop = llm_task_manager.get_stop_tokens(task=task)
    max_tokens = llm_task_manager.get_max_tokens(task=task)
    max_tokens = max_tokens or _MAX_TOKENS
    temperature = config.lowest_temperature if config is not None else 0.0

    llm_call_info_var.set(LLMCallInfo(task=task.value))

    llm_response = await llm_call(
        llm,
        prompt,
        stop=stop,
        llm_params={
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
    )
    warn_if_truncated(llm_response, task.value)
    response = llm_response.content

    log.info(f"Output self-checking result is: `{response}`.")

    if llm_task_manager.has_output_parser(task):
        result = llm_task_manager.parse_task_output(task, output=response)
    else:
        result = llm_task_manager.parse_task_output(task, output=response, forced_output_parser="is_content_safe")

    is_safe = bool(result[0])

    return _self_check_outcome(is_safe)
