from ctypes import sizeof
from mmap import mmap
from struct import unpack

from .rtss_structures import *

MIN_VERSION = 0x00020000  # Shared Memory ≥ v2.0 REQUIRED


class SharedMemoryRTSS:
    def __init__(self, ownerID: str):
        self.ownerID = ownerID
        self._shm = mmap(0, sizeof(SharedMemoryStruct),
                         "RTSSSharedMemoryV2")
        self._struct = SharedMemoryStruct.from_buffer_copy(
            self._shm.read())

        self._get_shared_memory_version()
        if not self.version:
            raise ConnectionFailed()

        self._adjust_shared_memory_size()

        # init max OSD text size, we'll use extended text slot for v2.7 and higher shared memory,
        # it allows displaying 4096 symbols instead of 256 for regular text slot
        self.maxTextSize = 4096 if self.version >= 0x00020007 else 256

        # text format tags are supported for shared memory v2.11 and higher
        self.formatTagsSupported: bool = self.version >= 0x0002000b
        # embedded object tags are supporoted for shared memory v2.12 and higher
        self.objTagsSupported: bool = self.version >= 0x0002000c

    def _get_shared_memory_version(self):
        self.version = 0
        if (self._struct.dwSignature == b"RTSS"[::-1] and self._struct.dwVersion >= MIN_VERSION):
            self.version = self._struct.dwVersion

    def _adjust_shared_memory_size(self):
        new_size = self._struct.dwAppArrOffset + \
            self._struct.dwAppArrSize * self._struct.dwAppEntrySize

        self._shm.close()
        self._shm = mmap(0, new_size, "RTSSSharedMemoryV2")
        self._struct = SharedMemoryStruct.from_buffer(self._shm)

    def update_OSD(self, data: bytes) -> bool:
        if len(data) > self.maxTextSize:
            return False

        result = False

        for pass_ in range(2):
            # 1st pass: find previously captured OSD slot
            # 2nd pass: otherwise find the first unused OSD slot and capture it
            for entry in range(1, self._struct.dwOSDArrSize):
                offset = self._struct.dwOSDArrOffset + entry * self._struct.dwOSDEntrySize
                entryStruct = SharedMemoryOSDEntry.from_buffer(
                    self._shm, offset)

                if pass_ and not len(entryStruct.szOSDOwner):
                    entryStruct.szOSDOwner = self.ownerID.encode("ascii")

                if entryStruct.szOSDOwner == self.ownerID.encode("ascii"):
                    # use extended text slot for v2.7 and higher shared memory, it allows displaying 4096 symbols
                    # instead of 256 for regular text slot
                    if self.version >= 0x00020007:
                        # OSD locking is supported on v2.14 and higher shared memory
                        if self.version >= 0x0002000e:
                            busy = self._struct.dwBusy & 0x80000000
                            self._struct.dwBusy = self._struct.dwBusy | 0x80000000

                            if not busy:
                                entryStruct.szOSDEx = data
                                self._struct.dwBusy = 0
                        else:
                            entryStruct.szOSDEx = data
                    else:
                        entryStruct.szOSD = data

                    self._struct.dwOSDFrame += 1
                    result = True
                    break

        return result

    def release_OSD(self):
        for entry in range(1, self._struct.dwOSDArrSize):
            offset = self._struct.dwOSDArrOffset + entry * self._struct.dwOSDEntrySize
            entryStruct = SharedMemoryOSDEntry.from_buffer(
                self._shm, offset)

            if entryStruct.szOSDOwner == self.ownerID.encode("ascii"):
                self._shm[offset:offset + self._struct.dwOSDEntrySize] = b'\0' * \
                    self._struct.dwOSDEntrySize  # Empty OSD

    def close(self):
        self._struct = None
        self._shm.close()


class ConnectionFailed(Exception):
    pass
