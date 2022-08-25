from sessions.AutoMLSession import AutoMLSession
from .AbstractAgent import IAbstractBlackboardAgent
from Controller_bgrpc import SessionStatus

class AutoMLSessionAgent(IAbstractBlackboardAgent):
    blackboard_key = 'session'

    def __init__(self, blackboard, controller, session: AutoMLSession):
        super().__init__(blackboard, controller, 'automl-session')
        self.session = session

    def CanContribute(self) -> bool:
        return self.GetState() != self.session.get_session_status().to_dict()
        
    def DoContribute(self) -> None:
        session_status = self.session.get_session_status()

        self.UpdateState({
            'id': self.session.get_id(),
            'status': session_status.status, # FIXME: session_status.to_dict()
            'configuration': self.session.get_configuration(),
        })

        if session_status.status != SessionStatus.SESSION_STATUS_BUSY:
            self._log.info(f'Session {self.session.get_id()} is inactive, stopping controller loop.')
            self.Unregister()
            raise StopIteration('AutoML session inactive, stopping..')

        return session_status