import asyncio
from .scenario import States, fsm
from .actions.actions_manager import ActionManager

from project.db.models import StateUserStorage, ChatStorage
from project.backend.session import get_session
from sqlalchemy import delete, exists, select, update, desc
from sqlalchemy.orm import selectinload
import uuid


class MessageHandler:

    async def new_user() -> int:
        session = await get_session()
        while True:
            last_user_id = uuid.uuid4()
            exist_query = select(exists().where(StateUserStorage.user_id == last_user_id))
            exist = await session.scalar(exist_query)
            if not exist:
                newuser = StateUserStorage(user_id=last_user_id, state=States.WAIT_QUERY)
                session.add(newuser)
                await session.commit()
                break
        print("\nuser last  ", last_user_id, '\n')

        return last_user_id

    async def new_message(user_id, message: str):
        session = await get_session()

        query = select(StateUserStorage).where(StateUserStorage.user_id == user_id)
        current_state = (await session.execute(query)).scalar().state

        if current_state == States.WAIT_QUERY:
            current_state = States.GET_QUERY
            fsm.machine.set_state(States.GET_QUERY)
        else:
            return "подожди бот отвечает "

        query = update(StateUserStorage).where(StateUserStorage.user_id == user_id).values(state =States.GET_QUERY)
        await session.execute(query)
        await session.commit()

        bot_answer = None
        print("\nState", current_state)
        
        while True:

            action = await ActionManager.get_action(current_state)
            return_bot_answer , transiotion = await action.handle_transition(user_id, message)
             
            if return_bot_answer :
                bot_answer  = return_bot_answer


            print("\nACTIONS: ", action, transiotion ,"BOT: " ,return_bot_answer, "\n")
            if transiotion == None:

                return bot_answer

            fsm.trigger(transiotion)
            current_state = fsm.state

    async def new_chat(user_id):
        session = await get_session()
        fsm.machine.set_state(States.NEW_CHAT)

        current_state = States.NEW_CHAT

        message = 'Новая тема'

        while True:

            action = await ActionManager.get_action(current_state)
            return_bot_answer ,transiotion = await action.handle_transition(user_id, message)

            print(action, transiotion)
            if transiotion == None:
                return message

            fsm.trigger(transiotion)
            current_state = fsm.state

    async def store_grade(user_id, grade):
        session = await get_session()
        chat_id_query = select(ChatStorage).where(ChatStorage.user_id == user_id).order_by(desc(ChatStorage.dt_created))
        chat_id = await session.execute(chat_id_query)
        chat_id = chat_id.scalar().chat_id
        print(f'Message Grade: {grade}')
        result = await session.execute(
            select(ChatStorage)
            .filter(ChatStorage.chat_id == chat_id, ChatStorage.user_id == user_id)
            .order_by(ChatStorage.dt_created.desc())
            .limit(1)
        )
        # Получаем последнюю запись
        last_record = result.scalar_one_or_none()
        last_record.grade = grade
        await session.commit()


