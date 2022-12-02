from mmap import mmap
from struct import unpack

MIN_VERSION = 0x0002000e  # Shared Memory ≥ v2.14 REQUIRED
LENGTH = 5546080


class RTSSSharedMemory:
    def __init__(self, name):
        self.name = name
        self.shm = mmap(0, LENGTH, "RTSSSharedMemoryV2")

        self.shared_memory_version()

        if not self.dwVersion:
            raise ConnectionFailed()

        self.dwAppEntrySize, self.dwAppArrOffset, self.dwAppArrSize, self.dwOSDEntrySize, self.dwOSDArrOffset, self.dwOSDArrSize, self.dwOSDFrame = unpack(
            'LLLLLLL', self.shm[8:36])

        # mmap size adjustment
        calc_mmap_size = self.dwAppArrOffset + self.dwAppArrSize * self.dwAppEntrySize
        if LENGTH < calc_mmap_size:
            self.shm.close()
            self.shm = mmap(0, LENGTH, "RTSSSharedMemoryV2")

    def shared_memory_version(self):
        self.dwVersion = 0
        self.dwSignature = ""

        if self.shm:
            dwSignature, = unpack('4s', self.shm[0:4])
            dwVersion, = unpack('L', self.shm[4:8])

            if dwSignature[::-1] == b"RTSS" and dwVersion >= MIN_VERSION:
                self.dwVersion = dwVersion
                self.dwSignature = dwSignature

    def update_OSD(self, text: bytes):
        for dwPass in range(2):
            bResult = False
            for dwEntry in range(1, self.dwOSDArrSize):
                ptr = self.dwOSDArrOffset + dwEntry * self.dwOSDEntrySize
                entry = RTSSSharedMemoryOsd(
                    self.shm[ptr:ptr + self.dwOSDEntrySize])

                if dwPass:
                    if entry.szOSDOwner == "":
                        OSDowner = self.name.encode("ascii")
                        self.shm[ptr + entry.szOSDOwner_range[0]:ptr +
                                 entry.szOSDOwner_range[0] + len(OSDowner)] = OSDowner  # Write new OSDOwner

                if entry.szOSDOwner == self.name:
                    dwBusy = self.shm[36] & 0b10000000  # Get first bit

                    self.shm[36] = self.shm[36] | 0b10000000  # Set first bit
                    if not dwBusy:
                        self.shm[ptr + entry.szOSDEx_range[0]:ptr +
                                 entry.szOSDEx_range[1]] = b'\0' * 4096  # Empty szOSDex
                        self.shm[ptr + entry.szOSDEx_range[0]:ptr +
                                 entry.szOSDEx_range[0] + len(text)] = text  # Fill szOSDex

                    bResult = True
                    break
            if bResult:
                break

    def releaseOSD(self):
        for dwEntry in range(1, self.dwOSDArrSize):
            ptr = self.dwOSDArrOffset + dwEntry * self.dwOSDEntrySize
            entry = RTSSSharedMemoryOsd(
                self.shm[ptr:ptr + self.dwOSDEntrySize])

            if entry.szOSDOwner == self.name:
                self.shm[ptr:ptr + self.dwOSDEntrySize] = b'\0' * \
                    self.dwOSDEntrySize  # Empty OSD

    def close(self):
        self.shm.close()


class RTSSSharedMemoryOsd:
    szOSD_range = (0, 256)
    szOSDOwner_range = (256, 256*2)
    szOSDEx_range = (256*2, 256*2 + 4096)
    buffer_range = (256*2 + 4096, 256*2 + 4096 + 262144)
    szOSDEx2_range = (256*2 + 4096 + 262144,
                      256*2 + 4096 + 262144 + 32768)

    def __init__(self, mem: bytes):
        szOSD_bytes = mem[self.szOSD_range[0]:self.szOSD_range[1]]
        szOSDOwner_bytes = mem[self.szOSDOwner_range[0]                               :self.szOSDOwner_range[1]]
        szOSDEx_bytes = mem[self.szOSDEx_range[0]:self.szOSDEx_range[1]]
        buffer_bytes = mem[self.buffer_range[0]:self.buffer_range[1]]
        szOSDEx2_bytes = mem[self.szOSDEx2_range[0]:self.szOSDEx2_range[1]]

        self.szOSD, = unpack(
            "256s", szOSD_bytes)

        szOSDOwner, = unpack(
            "256s", szOSDOwner_bytes)
        self.szOSDOwner = szOSDOwner.decode().strip('\0')

        # next fields are valid for v2.7 and newer shared memory format only
        szOSDEx, = unpack(
            "4096s", szOSDEx_bytes)
        self.szOSDEx = szOSDEx.decode().strip('\0')

        # next fields are valid for v2.12 and newer shared memory format only
        buffer, = unpack(
            "262144s", buffer_bytes)
        self.buffer = buffer.decode().strip('\0')

        # next fields are valid for v2.20 and newer shared memory format only
        szOSDEx2, = unpack(
            "32768s", szOSDEx2_bytes)
        self.szOSDEx2 = szOSDEx2.decode().strip('\0')


class ConnectionFailed(Exception):
    pass
