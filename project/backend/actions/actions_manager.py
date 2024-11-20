from project.backend.actions.get_query_action import GetQueryActions
from project.backend.actions.new_chat_action import ChatHandler
from project.backend.actions.start_action import StartAction
from project.backend.actions.wait_query_action import WaitQuery
from project.backend.actions.check_query_actions import CheckQuery
from project.backend.scenario import States
import asyncio


class ActionManager:

    async def get_action(state: States):

        mapping = {
            States.START: StartAction,
            States.WAIT_QUERY: WaitQuery,
            States.GET_QUERY: GetQueryActions,
            States.CHECK_QUERY: CheckQuery,
            States.NEW_CHAT: ChatHandler,
        }
        try:
            return mapping[state]
        except KeyError as e:
            raise KeyError(f"Cant find action for fsm State {state}") from e
