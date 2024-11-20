from project.backend.scenario import Transitions
import asyncio
from project.backend.scenario import States, fsm

from project.db.models import StateUserStorage, ChatStorage
from project.backend.session import get_session
from sqlalchemy import delete, exists, select, update,desc
import uuid


class ChatHandler:
	async def handle_transition(user_id , message: str = ' ')-> tuple[str,Transitions]:
		try:
			session = await get_session()
			chat_id = uuid.uuid4()
			print("\nNEW chat_id" , chat_id)

			query = update(StateUserStorage).where(StateUserStorage.user_id == user_id).values(chat_id = chat_id, state =States.NEW_CHAT)
			await session.execute(query)
			await session.commit()


			return None,Transitions.SUCCESS
		except:
			return None,Transitions.FAIL
	async def handle_event(user_id: int, message: str):
		return Transitions.SUCCESS
