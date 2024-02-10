from dataclasses import dataclass
from typing import List, Tuple
import struct

from gfx_perp_sdk.agnostic.Slabs import combine_u64_to_u128, CallbackInfo


@dataclass
class FillEvent:
    tag: int
    takerSide: int
    makerOrderId: int
    quoteSize: int
    baseSize: int
    LEN: int = 40

@dataclass
class FillEventInfo:
    fill_event: FillEvent
    maker_callback_info: CallbackInfo
    taker_callback_info: CallbackInfo

    def to_json(self):
        return {
            "eventType": "FillEvent",
            "takerSide": self.fill_event.takerSide,
            "makerOrderId": self.fill_event.makerOrderId,
            "quoteSize": self.fill_event.quoteSize,
            "baseSize": self.fill_event.baseSize,
            "maker_trg_account": self.maker_callback_info.userAccount.__str__(),
            "maker_callback_id": self.maker_callback_info.callbackId,
            "taker_trg_account": self.taker_callback_info.userAccount.__str__(),
            "taker_callback_id": self.taker_callback_info.callbackId,
        }
@dataclass
class OutEvent:
    tag: int
    side: int
    orderId: int
    baseSize: int
    LEN: int = 40

@dataclass
class OutEventInfo:
    out_event: OutEvent
    callback_info: CallbackInfo

    def to_json(self):
        return {
            "eventType": "OutEvent",
            "side": self.out_event.side,
            "orderId": self.out_event.orderId,
            "baseSize": self.out_event.baseSize,
            "callback_trg_account":self.callback_info.userAccount.__str__(),
            "callback_open_order_idx": self.callback_info.openOrderIdx,
        }

@dataclass
class EventQueueHeader:
    accountTag: int
    head: int
    count: int
    seq_num: int
    LEN: int = 32  # 8 bytes for each u64 field and 8 bytes for accountTag


class EventQueue:
    def __init__(self, header: EventQueueHeader, buffer: bytes):
        self.header = header
        self.callBackInfoLen = CallbackInfo.LEN
        capacity = (
            len(buffer) - EventQueueHeader.LEN) // (FillEvent.LEN + 2 * self.callBackInfoLen)
        self.capacity = capacity
        callBackInfoOffset = EventQueueHeader.LEN + capacity * FillEvent.LEN
        self.eventsBuffer = buffer[EventQueueHeader.LEN:callBackInfoOffset]
        self.callbackInfoBuffer = buffer[callBackInfoOffset:]

    def get_fill_out_events(self) -> Tuple[List[FillEventInfo], List[OutEventInfo]]:
        fill_events: List[FillEventInfo] = []
        out_events: List[OutEventInfo] = []

        for i in range(0, self.capacity):
            event_idx = (self.header.head + i) % self.capacity
            event_start = event_idx * FillEvent.LEN
            event_end = event_start + FillEvent.LEN
            event_chunk = self.eventsBuffer[event_start:event_end]
            if len(event_chunk) < FillEvent.LEN:
                break  # Stop if there are not enough bytes for a complete event
            tag = event_chunk[0]
            if tag == 0:  # Assuming 0 indicates FillEvent
                takerSide, quoteSize, makerOrderIdDown, makerOrderIdUp, baseSize = struct.unpack(
                    '<B6xQQQQ', event_chunk[1: FillEvent.LEN])             
                makerOrderId = combine_u64_to_u128(
                    makerOrderIdUp, makerOrderIdDown)
                fill_event = FillEvent(
                    tag, takerSide, makerOrderId, quoteSize, baseSize)

                # Get the corresponding CallbackInfo
                # 2*i and 2*i+1 are the indices for maker and taker callback_info
                callback_start = event_idx * 2 * self.callBackInfoLen
                callback_maker_end = callback_start + self.callBackInfoLen
                callback_taker_end = callback_maker_end + self.callBackInfoLen

                callback_maker = self.callbackInfoBuffer[callback_start:callback_maker_end]
                callback_taker = self.callbackInfoBuffer[callback_maker_end:callback_taker_end]

                callback_maker = CallbackInfo.deserialize(callback_maker)
                callback_taker = CallbackInfo.deserialize(callback_taker)
                fill_event_info  = FillEventInfo(fill_event, callback_maker, callback_taker)
                fill_events.append(fill_event_info)
            elif tag == 1:  # Assuming 1 indicates OutEvent
                side, orderIdDown, orderIdUp, baseSize = struct.unpack(
                    '<B14xQQQ', event_chunk[1: FillEvent.LEN])
                orderId = combine_u64_to_u128(orderIdUp, orderIdDown)
                out_event = OutEvent(tag, side, orderId, baseSize)
                callback_info_start = event_idx * 2 * self.callBackInfoLen
                callback_info_end = callback_info_start + self.callBackInfoLen
                callback_info = self.callbackInfoBuffer[callback_info_start:callback_info_end]
                callback_info = CallbackInfo.deserialize(callback_info)
                out_event_info = OutEventInfo(out_event, callback_info)
                out_events.append(out_event_info)
        return (fill_events, out_events)

    @staticmethod
    def deserialize(data: bytes) -> 'EventQueue':
        # Deserialize EventQueueHeader
        header_data = data[:EventQueueHeader.LEN]
        accountTag, head, count, seq_num = struct.unpack('<QQQQ', header_data)
        header = EventQueueHeader(
            accountTag,
            head,
            count,
            seq_num
        )

        return EventQueue(header, data)
