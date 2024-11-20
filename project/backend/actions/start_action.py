from project.backend.scenario import Transitions
import asyncio

class StartAction:

	async def handle_event(user_id: int, message: str)-> tuple[str,Transitions]:
		return None,Transitions.USER_AUTHORISED
	async def handle_transition(user_id: int, message: str)-> tuple[str,Transitions]:
		chatlist[user_id].append({"assistand" : "привет я бот"})
		return None,Transitions.USER_AUTHORISED