"""
    Loading data from database into State Machine for a single chat type.
    Needs updates to move to multiple chat types.
    Run it with an "init_db" argument to fill database with a test data.

    First run:
    python load_state_machine.py init_db

"""

from os import environ
import sys

from db_worker import SqliteDbWorker
from models import FrameElemType, FrameElem, Frame, StateMachine

db = SqliteDbWorker()

# init db - only for the first run
if len(sys.argv) > 1 and sys.argv[1] == 'init_db' or environ.get('INIT_TEST_DB'):
    db.init_db()

frame_elem_types = db.get_elem_types()

frames = db.get_dialog_frames()
for frame in frames:
    frame_elems = db.get_frame_elems(id_frame=frame.id_frame)
    frame.frame_elems = frame_elems
    if not frame_elems:
        frame.next_frame = db.get_next_frame(id_frame=frame.id_frame)


db.close()

state_machine = StateMachine(frames=frames)
# print(state_machine)
# print(stateMachine)
# for i in stateMachine.frames.values():
#     print(i, '\n')


'''
# start if needed
next_frame = state_machine.get_next_frame(0)
assert next_frame.id_frame == 1

# 1 -> 2
next_frame = state_machine.get_next_frame(1)
assert next_frame.id_frame == 2

# 2 -> 3 if 'Ok'
next_frame = state_machine.get_next_frame(2, 'Ok')
assert next_frame.id_frame == 3

# 2 -> 1 if 'Back'
next_frame = state_machine.get_next_frame(2, 'Back')
assert next_frame.id_frame == 1

# 3 -> 1 if 'To start'
next_frame = state_machine.get_next_frame(3, 'To start')
assert next_frame.id_frame == 1

# 3 -> 2 if 'Back'
next_frame = state_machine.get_next_frame(3, 'Back')
assert next_frame.id_frame == 2

# 3 -> 4 if 'Finish'
next_frame = state_machine.get_next_frame(3, 'Finish')
assert next_frame.id_frame == 4

# last frame without next
next_frame = state_machine.get_next_frame(4)
assert next_frame is None

# non-existing frame
next_frame = state_machine.get_next_frame(6)
assert next_frame is None
'''
print('StateMachine created')
