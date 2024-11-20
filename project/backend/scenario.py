from enum import Enum, auto

from transitions import Machine

class States(str, Enum):
	START = auto(),
	WAIT_QUERY = auto(),
	GET_QUERY = auto() ,
	NEW_CHAT = auto(),
	CHECK_QUERY = auto()

class Transitions(str, Enum):
    USER_AUTHORISED = auto(),
    SUCCESS = auto(),
    FAIL = auto()

class FSM:
    machine: Machine


transitions: list[dict[str, States | Transitions]] = [
    {
        "source": States.START,
        "trigger": Transitions.USER_AUTHORISED,
        "dest": States.WAIT_QUERY,
    },
    {
        "source": States.GET_QUERY,
        "trigger": Transitions.SUCCESS,
        "dest": States.WAIT_QUERY,
    },
    {
        "source": States.GET_QUERY,
        "trigger": Transitions.FAIL,
        "dest": States.CHECK_QUERY,
    },
    	{
        "source": States.NEW_CHAT,
        "trigger": Transitions.SUCCESS,
        "dest": States.WAIT_QUERY,
    },
    {
        "source": States.NEW_CHAT,
        "trigger": Transitions.FAIL,
        "dest": States.CHECK_QUERY,
    },
]

fsm = FSM()

_machine = Machine(
    model=fsm, states=States, transitions=transitions, initial=States.START
)

fsm.machine = _machine
