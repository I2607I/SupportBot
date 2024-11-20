from project.backend.scenario import Transitions
from project.db.models import StateUserStorage, ChatStorage
import asyncio
from project.backend.session import get_session
from sqlalchemy import delete, exists, select, desc, update
from project.tasks.worker import mock_ml_request


class GetQueryActions:
    async def handle_transition(user_id, message: str)-> tuple[str,Transitions]:
        session = await get_session()

        chat_id_query = select(StateUserStorage).where(StateUserStorage.user_id == user_id)
        chat_id = await session.execute(chat_id_query)
        chat_id = chat_id.scalar().chat_id

        answer_message = select(ChatStorage).where(ChatStorage.user_id == user_id,
                                                   ChatStorage.chat_id == chat_id).order_by(
            desc(ChatStorage.dt_created))
        answer_message = (await session.execute(answer_message)).scalars()
        history = ''
        for i in answer_message:
            history = f'{i.sender}: {i.message} {i.grade}\n' + history

        task = mock_ml_request.delay(message, history)
        bot_answer, accuracy_score, history = task.get()

        chat_id_query = select(StateUserStorage).where(StateUserStorage.user_id == user_id)

        chat_id = await session.scalar(chat_id_query)
        chat_id = chat_id.chat_id
        print("\n get query Chat_id ", chat_id, "\n")

        query = ChatStorage(user_id=user_id, chat_id=chat_id, message=message, sender="user", )
        session.add(query)
        await session.commit()

        query = ChatStorage(user_id=user_id, chat_id=chat_id, message=bot_answer, sender="assistant", accuracy = accuracy_score )
        session.add(query)
        await session.commit()
        return bot_answer ,Transitions.SUCCESS



async def handle_event(user_id: int, message: str):
    return Transitions.SUCCESS
