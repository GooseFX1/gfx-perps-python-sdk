from enum import Enum
from typing import List, Tuple, Generator, Union
from dataclasses import dataclass
import struct
from solders.pubkey import Pubkey as PublicKey

def combine_u64_to_u128(a: int, b: int) -> int:
    # Shift a to the higher 64 bits of u128
    u128_a = a << 64
    # Combine a and b using bitwise OR
    u128_combined = u128_a | b
    return u128_combined

def bitwise_not_32_bits(number: int) -> int:
    # Create a bitmask with all bits set to 1 for 32 bits
    mask_32_bits = (1 << 32) - 1
    # Perform bitwise NOT operation
    result = ~number & mask_32_bits
    return result

@dataclass
class CallbackInfo:
    userAccount: PublicKey
    openOrderIdx: int
    callbackId: int
    LEN: int = 40

    @staticmethod
    def deserialize(data: bytes) -> 'CallbackInfo':
        user_account_bytes = data[:32]
        open_order_idx = struct.unpack('<L', data[32:36])[0]
        callback_id = struct.unpack('<L', data[36:40])[0]
        user_account = PublicKey(user_account_bytes)
        return CallbackInfo(user_account, open_order_idx, callback_id)


@dataclass
class Price:
    size: int
    price: float

class AccountTag:
    Initialized = 0
    Market = 1
    EventQueue = 2
    Bids = 3
    Asks = 4

class OrderSide(Enum):
    BID = "BID"
    ASK = "ASK"

@dataclass
class InnerNode:
    prefixLen: int
    key: int
    children: List[int]
    LEN = 32

@dataclass
class LeafNode:
    key: int
    baseQuantity: int
    LEN = 24
    def getPrice(self) -> int:
      return self.key >> 64

@dataclass
class SlabHeader:
    accountTag: int
    leafFreeListLen: int
    leafFreeListHead: int
    leafBumpIndex: int
    innerNodeFreeListLen: int
    innerNodeFreeListHead: int
    innerNodeBumpIndex: int
    rootNode: int
    leafCount: int
    LEN = 40
class Slab:
    NODE_SIZE: int = 32
    NODE_TAG_SIZE: int = 8
    SLOT_SIZE: int = 40
    INNER_FLAG: int = 1 << 31

    def __init__(self, header: SlabHeader, buffer: bytes, callBackInfoLen: int):
        self.header = header
        self.callBackInfoLen = callBackInfoLen
        leafSize = LeafNode.LEN + callBackInfoLen

        capacity = (len(buffer) - SlabHeader.LEN - leafSize) // (leafSize + InnerNode.LEN)
        innerNodesBufferOffset = SlabHeader.LEN + (capacity + 1) * LeafNode.LEN
        leavesBuffer = buffer[SlabHeader.LEN:innerNodesBufferOffset]
        callbackInfoBufferOffset = innerNodesBufferOffset + capacity * InnerNode.LEN
        innerNodeBuffer = buffer[innerNodesBufferOffset:callbackInfoBufferOffset]
        callbackInfoBuffer = buffer[callbackInfoBufferOffset:]
        self.orderCapacity = capacity
        self.leafBuffer = leavesBuffer
        self.innerNodeBuffer = innerNodeBuffer
        self.callbackInfoBuffer = callbackInfoBuffer

    @staticmethod
    def isLeaf(handle: int) -> bool:
        return (handle & Slab.INNER_FLAG) == 0
    
    @staticmethod
    def deserialize(data: bytes, callBackInfoLen: int) -> 'Slab':
        # Deserialize SlabHeader manually
        header_data = data[:SlabHeader.LEN]
        accountTag, leafFreeListLen, leafFreeListHead, leafBumpIndex, innerNodeFreeListLen, innerNodeFreeListHead, innerNodeBumpIndex, rootNode, leafCount = struct.unpack(
            '<QIIIIIIII', header_data
        )
        header = SlabHeader(
            accountTag,
            leafFreeListLen,
            leafFreeListHead,
            leafBumpIndex,
            innerNodeFreeListLen,
            innerNodeFreeListHead,
            innerNodeBumpIndex,
            rootNode,
            leafCount,
        )

        return Slab(header, data, callBackInfoLen)

    @staticmethod
    def computeAllocationSize(desiredOrderCapacity: int, callbackInfoLen: int) -> int:
        return (
            SlabHeader.LEN
            + LeafNode.LEN
            + callbackInfoLen
            + (desiredOrderCapacity - 1) * (LeafNode.LEN + InnerNode.LEN + callbackInfoLen)
        )

    def getNode(self, handle: int) -> Union[InnerNode, LeafNode]:
        
        if Slab.isLeaf(handle):
            buff = self.leafBuffer[handle * LeafNode.LEN : (handle + 1) * LeafNode.LEN]
            keyDown, keyUp, baseQuantity = struct.unpack("<QQQ", buff)
            key = combine_u64_to_u128(keyUp, keyDown)
            return LeafNode(key, baseQuantity)
        index = bitwise_not_32_bits(handle)
        #index = np.uint32(~handle).item()
        buff = self.innerNodeBuffer[
            index * InnerNode.LEN : (index + 1) * InnerNode.LEN
        ]
        keyDown, keyUp, prefixLen, child1, child2 = struct.unpack("<QQQII", buff)
        key = combine_u64_to_u128(keyUp, keyDown)
        return InnerNode(prefixLen, key, [child1, child2])

    def items(self, descending=False) -> Generator[Tuple[LeafNode, CallbackInfo], None, None]:
        if self.header.leafCount == 0:
            return

        stack = [self.header.rootNode]
        while stack:
            nodeHandle = stack.pop()
            node = self.getNode(nodeHandle)
            if isinstance(node, LeafNode):
                yield (node, self.getCallBackInfo(nodeHandle))
            elif isinstance(node, InnerNode):
                if descending:
                    stack.extend([node.children[0], node.children[1]])
                else:
                    stack.extend([node.children[1], node.children[0]])

    def getMinMaxNodes(self, maxNbOrders: int, max: bool) -> List[Tuple[LeafNode, CallbackInfo]]:
        minMaxOrders = []
        for leafNode, callbackInfo in self.items(max):
            if len(minMaxOrders) == maxNbOrders:
                break
            minMaxOrders.append((leafNode, callbackInfo))
        return minMaxOrders

    def getL2DepthJS(self, depth: int, increasing: bool) -> List[Price]:
        if self.header.leafCount == 0:
            return []
        raw = []
        stack = [self.header.rootNode]
        while True:
            if len(stack) != 0:
                current = stack.pop()
            else:
                break
            if current is None:
                break
            node = self.getNode(current)
            if isinstance(node, LeafNode):
                leafPrice = node.getPrice()
                if raw and raw[len(raw) - 1] == leafPrice:
                    idx = len(raw) - 2
                    raw[idx] += node.baseQuantity
                elif len(raw) == 2 * depth:
                    break
                else:
                    raw.append(node.baseQuantity)
                    raw.append(leafPrice)
            elif isinstance(node, InnerNode):
                stack.append(node.children[int(increasing)])
                stack.append(node.children[int(not increasing)])
        result = []
        for i in range(len(raw) // 2):
          size = int(raw[2 * i])  # Convert BN to int
          price = int(raw[2 * i + 1]) # Convert BN to int and scale down
          result.append({'size': size, 'price': price})
        return result

    def getCallBackInfo(self, nodeHandle: int) -> CallbackInfo:
        if not Slab.isLeaf(nodeHandle):
            return b""
        start = nodeHandle * self.callBackInfoLen
        end = (nodeHandle + 1) * self.callBackInfoLen
        callback_info = CallbackInfo.deserialize(self.callbackInfoBuffer[start:end])
        return callback_info
