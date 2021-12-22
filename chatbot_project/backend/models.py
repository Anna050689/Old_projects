"""
    Main models for representing a State Machine for a single chat.

    FrameElemType (dialog_frame_elem_type table)
        Logical enum for the frame elems: button, link etc.
    FrameElem (dialog_frame_elem table)
        Specific elements for a frame: Button 'Ok' etc. Has next_frame reference.
    Frame (dialog_frame table)
        Single step of dialog. Has a text message, elements if exist and the next_frame reference
        if elements don's exist.
    StateMachine
        State Machine representation for a single dialog type.
        Has a dict of frames (idFrame: Frame) and method to get the next frame depending on condition
"""

from typing import List, Union


# TODO add validation on fields
class Check:
    @staticmethod
    def parse_string(string, min_length=1, max_length=None):
        string = str(string).replace("'", "''")
        if min_length and len(string) < min_length or max_length and len(string) > max_length:
            raise ValueError
        return string


class InitContact:
    def __init__(self, first_name: str, last_name: str, phone: str, email: str) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email

    def __repr__(self) -> str:
        return f"InitContact(first_name='{self.first_name}', last_name='{self.last_name}'," \
               f" phone='{self.phone}', email='{self.email}')"


class ContactWithChat(InitContact):
    def __init__(self, first_name: str, last_name: str, phone: str, email: str, id_chat: int) -> None:
        super().__init__(first_name, last_name, phone, email)
        self.id_chat = id_chat

    def __repr__(self) -> str:
        return f"ContactWithChat(first_name='{self.first_name}', last_name='{self.last_name}'," \
               f" phone='{self.phone}', email='{self.email}', id_chat={self.id_chat})"


class FrameElemType:
    def __init__(self, id_type: int, title: str) -> None:
        self.id_type = id_type
        self.title = title

    def __repr__(self) -> str:
        return f"FrameElemType(id_type={self.id_type}, title='{self.title}')"


class FrameElem:
    def __init__(self, type: FrameElemType, text: str, id_dialog_frame_elem: int, next_frame) -> None:
        self.id_dialog_frame_elem = id_dialog_frame_elem
        self.frame_elem_type = type
        self.frame_elem_text = text

        self.next_frame = next_frame

    def __repr__(self) -> str:
        return f"FrameElem(frame_elem_type={self.frame_elem_type}, " \
               f"id_dialog_frame_elem={self.id_dialog_frame_elem}, " \
               f"next_frame={self.next_frame}, " \
               f"frame_elem_text='{self.frame_elem_text}')"

    def check_condition(self, condition: str) -> bool:
        return self.frame_elem_text == condition


class Frame:
    def __init__(self, id_frame: int, frame_message: str, frame_num: int, frame_elems: List[FrameElem] = None) -> None:
        self.id_frame = id_frame
        self.frame_num = frame_num

        self.frame_message = frame_message
        self.frame_elems = frame_elems

        self.next_frame = None

    def get_next_frame(self, condition: str = None) -> Union[FrameElem]:
        if not self.frame_elems:
            return self
        else:
            for i in self.frame_elems:
                if i.check_condition(condition=condition):
                    return i

    def __repr__(self) -> str:
        return f"Frame(id_frame={self.id_frame}, frame_message='{self.frame_message}', " \
               f"frame_elems={self.frame_elems}, frame_num={self.frame_num}, next_frame={self.next_frame})"


class StateMachine:
    def __init__(self, frames: List[Frame]) -> None:
        self.frames = {
            i.id_frame: i for i in frames
        }
        # self.update_next_frames()

    '''
    def update_next_frames(self):
        for frame in self.frames.values():
            if frame.next_frame:
                frame.next_frame = self.frames[frame.next_frame]
            else:
                for elem in frame.frame_elems:
                    elem.next_frame = self.frames[elem.next_frame]
    '''

    def get_next_frame(self, id_frame: int = None, condition: str = None) -> Union[Frame, None]:
        next_frame = None
        if id_frame:
            cur_frame = self.frames.get(id_frame)
            if cur_frame:
                # print(cur_frame)
                next_frame = cur_frame.get_next_frame(condition=condition)
                if next_frame:
                    next_frame = self.frames.get(next_frame.next_frame)
        else:
            for frame in self.frames.values():
                if frame.frame_num == 1:
                    next_frame = frame
        return next_frame

    def __repr__(self) -> str:
        return f"StateMachine(frames={list(self.frames.values())})"
