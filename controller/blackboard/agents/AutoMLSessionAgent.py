from sessions.AutoMLSession import AutoMLSession
from .AbstractAgent import IAbstractBlackboardAgent
from Controller_bgrpc import SessionStatus

class AutoMLSessionAgent(IAbstractBlackboardAgent):
    def __init__(self, blackboard, session: AutoMLSession):
        super().__init__(blackboard, session.get_id())
        self.session = session

    def CanContribute(self) -> bool:
        return self.blackboard.common_state.get('session', {}) != self.session.get_session_status().to_dict()
        
    def DoContribute(self) -> None:
        session_status = self.session.get_session_status()

        self.blackboard.common_state.update({
            'session': session_status.to_dict()
        })

        if self.session.get_session_status().status != SessionStatus.SESSION_STATUS_BUSY:
            print(f'Session {self.session.get_id()} is inactive, stopping controller loop.')
            self.session.controller.StopLoop()

        return session_status