from podite import U64
from dataclasses import dataclass

from dataclasses import dataclass
from typing import List, Tuple, TypeVar
from solders.pubkey import Pubkey as PublicKey
import struct

from gfx_perp_sdk.agnostic.Slabs import combine_u64_to_u128


class CallbackInfo:
    def __init__(self, userAccount: PublicKey, openOrderIdx: int):
        self.userAccount = userAccount
        self.openOrderIdx = openOrderIdx

    @staticmethod
    def deserialize(data: bytes) -> 'CallbackInfo':
        # Assuming PublicKey is the first 32 bytes and openOrderIdx is the next 4 bytes
        user_account_bytes = data[:32]
        open_order_idx = struct.unpack('<Q', data[32:40])[0]

        user_account = PublicKey(user_account_bytes)
        return CallbackInfo(user_account, open_order_idx)


@dataclass
class FillEvent:
    tag: int
    takerSide: int
    makerOrderId: int
    quoteSize: int
    baseSize: int
    LEN: int = 40


@dataclass
class OutEvent:
    tag: int
    side: int
    orderId: int
    baseSize: int
    LEN: int = 40


@dataclass
class EventQueueHeader:
    accountTag: int
    head: int
    count: int
    seq_num: int
    LEN: int = 32  # 8 bytes for each u64 field and 8 bytes for accountTag


class EventQueue:
    # def __init__(self, header: EventQueueHeader, events: List[E], callback_infos: List[C]):
    def __init__(self, header: EventQueueHeader, buffer: bytes, callBackInfoLen: int):
        self.header = header
        self.callBackInfoLen = callBackInfoLen
        capacity = (
            len(buffer) - EventQueueHeader.LEN) // (FillEvent.LEN + 2 * callBackInfoLen)
        # header = buffer[8:EventQueueHeader.LEN]
        self.capacity = capacity
        print("\nself.capacity:", self.capacity)
        eventsBuffer = buffer[EventQueueHeader.LEN:capacity * FillEvent.LEN]
        callBackInfoOffset = capacity * FillEvent.LEN
        callBackInfoBuffer = buffer[callBackInfoOffset:]
        self.eventsBuffer = eventsBuffer
        self.callbackInfoBuffer = callBackInfoBuffer

    def get_fill_out_events(self) -> Tuple[List[Tuple[FillEvent, CallbackInfo, CallbackInfo]], List[Tuple[OutEvent, CallbackInfo, CallbackInfo]]]:
        fill_events = []
        out_events = []

        for i in range(0, self.capacity):
            # Get the corresponding event
            event_start = i * FillEvent.LEN
            event_end = event_start + FillEvent.LEN
            event_chunk = self.eventsBuffer[event_start:event_end]

            if len(event_chunk) < FillEvent.LEN:
                break  # Stop if there are not enough bytes for a complete event
            tag = event_chunk[0]
            # print("\ntag from event_chunk:", tag)

            if tag == 0:  # Assuming 0 indicates FillEvent
                takerSide, quoteSize, makerOrderIdUp, makerOrderIdDown, baseSize = struct.unpack(
                    '<B6xQQQQ', event_chunk[1: FillEvent.LEN])
                makerOrderId = combine_u64_to_u128(
                    makerOrderIdUp, makerOrderIdDown)
                # print("\ni", i)
                # print("\ntag", tag)
                # print("\ntakerSide", takerSide)
                # print("\nquoteSize", quoteSize)
                # print("\nmakerOrderId", makerOrderId)
                # print("\nbaseSize", baseSize)
                fill_event = FillEvent(
                    tag, takerSide, makerOrderId, quoteSize, baseSize)

                # Get the corresponding CallbackInfo
                # 2*i and 2*i+1 are the indices for maker and taker callback_info
                callback_start = i * 2 * self.callBackInfoLen
                callback_maker_end = callback_start + self.callBackInfoLen
                callback_taker_end = callback_maker_end + self.callBackInfoLen

                callback_maker = self.callbackInfoBuffer[callback_start:callback_maker_end]
                callback_taker = self.callbackInfoBuffer[callback_maker_end:callback_taker_end]

                callback_maker = CallbackInfo.deserialize(callback_maker)
                callback_taker = CallbackInfo.deserialize(callback_taker)
                # print("\ncallback_maker.userAccount",
                #       callback_maker.userAccount)
                # print("\ncallback_maker.openOrderIdx",
                #       callback_maker.openOrderIdx)
                # print("\ncallback_taker.userAccount",
                #       callback_taker.userAccount)
                # print("\ncallback_taker.openOrderIdx",
                #       callback_taker.openOrderIdx)
                fill_events.append(
                    (fill_event, callback_maker, callback_taker))
            elif tag == 1:  # Assuming 1 indicates OutEvent
                side, orderIdUp, orderIdDown, baseSize = struct.unpack(
                    '<B14xQQQ', event_chunk[1: FillEvent.LEN])
                orderId = combine_u64_to_u128(orderIdUp, orderIdDown)
                out_event = OutEvent(tag, side, orderId, baseSize)
                # print("\ni", i)
                # print("\ntag", tag)
                # print("\norderId", orderId)
                # print("\nbaseSize", baseSize)
                # Get the corresponding CallbackInfo
                # 2*i and 2*i+1 are the indices for callback_info
                callback_start = i * 2 * self.callBackInfoLen
                callback_maker_end = callback_start + self.callBackInfoLen
                callback_taker_end = callback_maker_end + self.callBackInfoLen

                callback_maker = self.callbackInfoBuffer[callback_start:callback_maker_end]
                callback_taker = self.callbackInfoBuffer[callback_maker_end:callback_taker_end]

                callback_maker = CallbackInfo.deserialize(callback_maker)
                callback_taker = CallbackInfo.deserialize(callback_taker)
                # print("\ncallback_maker.userAccount",
                #       callback_maker.userAccount)
                # print("\ncallback_maker.openOrderIdx",
                #       callback_maker.openOrderIdx)
                # print("\ncallback_taker.userAccount",
                #       callback_taker.userAccount)
                # print("\ncallback_taker.openOrderIdx",
                #       callback_taker.openOrderIdx)
                out_events.append((out_event, callback_maker, callback_taker))
        return (fill_events, out_events)

    @staticmethod
    def deserialize(data: bytes, callBackInfoLen: int) -> 'EventQueue':
        # Deserialize EventQueueHeader
        header_data = data[:EventQueueHeader.LEN]
        accountTag, head, count, seq_num = struct.unpack('<QQQQ', header_data)
        # print("\nheader.accounttag:", accountTag)
        # print("\nheader.head:", head)
        # print("\nheader.count:", count)
        # print("\nheader.seq_num:", seq_num)
        header = EventQueueHeader(
            accountTag,
            head,
            count,
            seq_num
        )

        buffer = data[EventQueueHeader.LEN:]
        return EventQueue(header, buffer, callBackInfoLen)
