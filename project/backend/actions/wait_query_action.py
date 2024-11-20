from project.backend.scenario import Transitions
import asyncio
from project.backend.scenario import States, fsm

from project.db.models import StateUserStorage, ChatStorage
from project.backend.session import get_session
from sqlalchemy import delete, exists, select, update,desc
import uuid

class WaitQuery:
	async def handle_event(user_id: int, message: str)-> tuple[str,Transitions]:
		return None,None
	async def handle_transition(user_id :int, message: str)-> tuple[str,Transitions]:
		session = await get_session()
		query = update(StateUserStorage).where(StateUserStorage.user_id == user_id).values(state =States.WAIT_QUERY)
		await session.execute(query)
		await session.commit()

		return None,None