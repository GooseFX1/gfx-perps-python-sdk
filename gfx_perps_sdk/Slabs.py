#from types.account_tag import AccountTag
#from podite import (pod, U64, U32)


#@pod
#class SlabHeader:
#  accountTag: AccountTag
#  leafFreeListLen: U32
#  leafFreeListHead: U32
#  leafBumpIndex: U32
#  innerNodeFreeListLen: U32
#  innerNodeFreeListHead: U32
#  innerNodeBumpIndex: U32
#  rootNode: U32
#  leafCount: U32

#class Slab:
#  header: SlabHeader
#  leafBuffer: bytes
#  innerNodeBuffer: bytes
#  callbackInfoBuffer: bytes
#  callBackInfoLen: int
#  orderCapacity: int